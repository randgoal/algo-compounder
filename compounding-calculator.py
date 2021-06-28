#!/usr/bin/env python3

# Simple calculator to find optimal number of times to compound in a given period.
# Just edit the variables below and run the script.

import math

principal = 10000 # Algos
annual_rate = 0.0575 # 5.75%
compounding_period_in_years = 1
compounding_fee = 0.01 # Algos
show_work = False # Show compounded amount in each loop below.

# Returns compounded amount minus transaction fees.
# After a certain point, compounding will have diminishing returns and
# transaction fees will cause the compounded amount to actually decrease.
def compound(principal, annual_rate, compounding_period_in_years, compounding_times):
    amount = principal * (1 + annual_rate / compounding_times) ** (compounding_period_in_years * compounding_times)
    fee = compounding_times * compounding_fee
    return amount - fee

if principal < 1:
    print("1 Algo is required to stake.")
    quit()
elif principal > 10000000000:
    print("Principal exceeds Algo total supply of 10,000,000,000.")
    quit()

compounded_times = 0
compounded_amount = 0

# Keep increasing compounding times until the maximum balance is reached.
# Stop when we've compounded too many times and the balance decreases
# due to transaction fees.
while True:
    new_compounded_times = compounded_times + 1
    new_compounded_amount = compound(principal, annual_rate, compounding_period_in_years, new_compounded_times)

    if new_compounded_amount > 10000000000:
        print("Error: compounded amount cannot exceed total Algo supply of 10,000,000,000.")
        quit()

    if show_work:
        print("*" * 80)
        print("")
        print("Compounded times: " + format(new_compounded_times, ","))
        print("Compounded amount minus transaction fees: " + format(round(new_compounded_amount, 6), ","))

        if new_compounded_amount < compounded_amount:
            print("This amount is less than the previous amount. Stopping...")

        print("")

    # The maximum balance has been reached in the previous loop. Report the previous loop's data.
    if new_compounded_amount < compounded_amount:
        if show_work:
            print("*" * 80)
            print("")

        print("Compounding period: " + str(compounding_period_in_years) + " year")
        print("Annual rate: " + str(round(annual_rate * 100, 2)) + "%")

        # Days.
        if (365 / compounded_times) >= 1:
            formatted_compounded_times = str(round(365 / compounded_times, 2)) + " days"
        # Hours.
        elif ((365 * 24) / compounded_times) >= 1:
            formatted_compounded_times = str(round((365 * 24) / compounded_times, 2)) + " hours"
        # Minutes.
        else:
            formatted_compounded_times = str(round((365 * 24 * 60) / compounded_times, 2)) + " minutes"

        print("Optimal number of times to compound per period: " + format(compounded_times, ",") + " (about every " + formatted_compounded_times + ")")
        print("Starting balance: " + format(round(principal, 6), ",") + " Algos")
        print("Ending balance: " + format(round(compounded_amount, 6), ",") + " Algos")
        print("Total interest minus transaction fees: " + format(round(compounded_amount - principal, 6), ",") + " Algos")
        break
    # The maximum balance has not been reached yet.
    else:
        compounded_times = new_compounded_times
        compounded_amount = new_compounded_amount