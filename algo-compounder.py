#!/usr/bin/env python3

import os, json, qrcode
from algosdk.v2client import algod
from algosdk import account, encoding, mnemonic
from algosdk.future.transaction import PaymentTxn

# Connect to Algorand node.
try:
    algod_address = "http://localhost:4001"
    algod_token = "a" * 64
    algod_client = algod.AlgodClient(algod_token, algod_address)
    status = algod_client.status()
except:
    print("Couldn't connect to Algorand node. Please try again.")
    quit()

script_directory = os.path.dirname(os.path.realpath(__file__))

# Create or load Algorand wallet.
if not os.path.isfile(os.path.join(script_directory, "settings.json")):
    sender_private_key, sender_address = account.generate_account()
    sender_passphrase = mnemonic.from_private_key(sender_private_key)

    receiver_address = input("What is the address of the wallet receiving the 0 Algo transaction?\nAddress: ")

    if not encoding.is_valid_address(receiver_address):
        print("Invalid wallet address. Please start over.")
        quit()

    # Check receiving wallet balance.
    try:
        account_info = algod_client.account_info(receiver_address)
    except:
        print("Couldn't connect to Algorand node. Please try again.")

    microalgos_in_account = account_info.get('amount')
    algos_in_account = microalgos_in_account / 1000000

    confirm = input("There are " + format(algos_in_account, ",") + " Algos in the receiving account. Is this correct? [Y/N] ")

    if confirm.lower() not in ('y', 'yes'):
        print("Please reenter the receiving address and try again.")
        print("Check Algorand Sandbox is running in mainnet mode and it's had enough time to update.")
        quit()

    with open(os.path.join(script_directory, "settings.json"), "w") as file:
        data = {
            "sender_address": sender_address,
            "sender_private_key": sender_private_key,
            "sender_passphrase": sender_passphrase,
            "receiver_address": receiver_address
        }

        json.dump(data, file)

    # Create Algorand sender address text file.
    if not os.path.isfile(os.path.join(script_directory, "sender_address.txt")):
        with open(os.path.join(script_directory, "sender_address.txt"), "w") as file:
            file.write(sender_address)

    # Create Algorand sender address QR code image.
    if not os.path.isfile(os.path.join(script_directory, "sender_address_qr_code.png")):
        qr = qrcode.QRCode(
                version=1,
                box_size=10,
                border=5)
        qr.add_data(sender_address)
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")
        img.save(os.path.join(script_directory, "sender_address_qr_code.png"))

    print("")
    print("-" * 80)
    print("Wallet sending 0 Algo transaction:\n" + sender_address)
    print("")
    print("Wallet receiving 0 Algo transaction:\n" + receiver_address)
    print("-" * 80)
    print("")
    print("Please fund the sending wallet with 1 Algo and run this script again.")
    print("A text file and a QR code image of the sender address was generated in the script directory.")
    quit()
else:
    with open(os.path.join(script_directory, "settings.json")) as file:
        data = json.load(file)

    sender_address = data["sender_address"]
    sender_private_key = data["sender_private_key"]
    sender_passphrase = data["sender_passphrase"]

    receiver_address  = data["receiver_address"]

# Check wallet balance.
account_info = algod_client.account_info(sender_address)
microalgos_in_account = account_info.get('amount')

if microalgos_in_account == 0:
    print("There are no Algos in the sending wallet. Did you remember to fund it?")
    quit()

# Build and send transaction.
params = algod_client.suggested_params()
unsigned_txn = PaymentTxn(sender_address, params, receiver_address, 0, None, None)
signed_txn = unsigned_txn.sign(mnemonic.to_private_key(sender_passphrase))
txid = algod_client.send_transaction(signed_txn)

# Utility for waiting on a transaction confirmation.
def wait_for_confirmation(client, transaction_id, timeout):
    """
    Wait until the transaction is confirmed or rejected, or until 'timeout'
    number of rounds have passed.
    Args:
        transaction_id (str): the transaction to wait for
        timeout (int): maximum number of rounds to wait
    Returns:
        dict: pending transaction information, or throws an error if the transaction
            is not confirmed or rejected in the next timeout rounds
    """
    start_round = client.status()["last-round"] + 1;
    current_round = start_round

    while current_round < start_round + timeout:
        try:
            pending_txn = client.pending_transaction_info(transaction_id)
        except Exception:
            return
        if pending_txn.get("confirmed-round", 0) > 0:
            return pending_txn
        elif pending_txn["pool-error"]:
            raise Exception(
                'pool error: {}'.format(pending_txn["pool-error"]))
        client.status_after_block(current_round)
        current_round += 1
    raise Exception(
        'pending tx not found in timeout rounds, timeout value = : {}'.format(timeout))


# Wait for confirmation
try:
    confirmed_txn = wait_for_confirmation(algod_client, txid, 4)
    # print("Transaction information: {}".format(json.dumps(confirmed_txn, indent=4)))
    print("Success")
except Exception as error:
    # print(error)
    print("Error sending transaction.")