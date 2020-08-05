import csv, glob, os

# Checks input for a positive integer
def personInputChecker(msg):
    boolpos = False
    while not boolpos:
        val = int(input(msg))
        if val >= 0:
            boolpos = True
        else:
            print("Enter a valid positive integer")
    return val

# Checks input for percentage number between 0 and 1
def pctInputChecker(msg):
    validPct = False
    while not validPct:
        val = float(input(msg))
        if val > 0 and val < 1:
            validPct = True
        else:
            print("Enter a valid percentage between 0 and 1")
    return val

# Checks input for a positive floating value
def realInputChecker(msg):
    validVal = False
    while not validVal:
        val = float(input(msg))
        if isinstance(val, float) or val.is_integer():
            validVal = True
        else:
            print("Enter a valid real number")
    return val

# Print first 4 lines of csv file as customer details
def customerDetails(csvfile, output):
    custDetails = csv.reader(csvfile)
    for i in range(4):
        custLine = next(custDetails)
        print(f"{custLine[0]}: {custLine[1]}")
        output.write(f"{custLine[0]}: {custLine[1]}\n")
    next(csvfile) # skip line between customer details and costs

# Parse csv file tallying daily and total costs
def costParser(csvfile, output, dayCosts):
    costs = csv.DictReader(csvfile)
    currentDate = units = ""
    totalCost = totalUsage = currentCost = currentUsage = majorityMonthCost = 0.0
    days = 0
    majorityMonthEnable = False
    scalingFactor = 0.24 / 0.31 # tier 1 PGE to tier 2 PGE

    print("\nDaily Breakdown:")
    output.write("\nDaily Breakdown:\n")
    for line in costs:
        totalCost += float(line["COST"].replace('$', ''))
        totalUsage += float(line["USAGE"])
        if units == "":
            units = line["UNITS"]
        if currentDate == "":
            currentDate = line["DATE"]
        if currentDate == line["DATE"]:
            currentUsage += float(line["USAGE"])
            currentCost += float(line["COST"].replace('$', ''))
        else:
            print(f"Date: {currentDate}, Daily Usage: {currentUsage:.2f}{units}, Daily Cost: ${currentCost:.2f}")
            output.write(f"Date: {currentDate}, Daily Usage: {currentUsage:.2f}{units}, Daily Cost: ${currentCost:.2f}\n")
            dayCosts[currentDate] = dict({'Usage': currentUsage, 'Cost': currentCost, 'Units': units})
            # start day count at beginning of month
            if currentDate.split('-')[2] == "01": 
                majorityMonthEnable = True
            currentDate = line["DATE"]
            units = line["UNITS"]
            if majorityMonthEnable:
                days += 1
                majorityMonthCost += currentCost
            currentCost = currentUnits = currentUsage = extPay = 0.0

    # process last date of file
    print(f"Date: {currentDate}, Daily Usage: {currentUsage:.2f}{units}, Daily Cost: ${currentCost:.2f}")
    output.write(f"Date: {currentDate}, Daily Usage: {currentUsage:.2f}{units}, Daily Cost: ${currentCost:.2f}\n")
    dayCosts[currentDate] = dict({'Usage': currentUsage, 'Cost': currentCost, 'Units': units})

    avg = scalingFactor * majorityMonthCost / days
    print(f"Total Cost: {totalCost:.2f}, Total Usage: {totalUsage:.2f}{units}, Scaled Avg Cost/day: ${avg:.2f}")
    output.write(f"Total Cost: {totalCost:.2f}, Total Usage: {totalUsage:.2f}{units}, Scaled Avg Cost/day: ${avg:.2f}\n")
    return avg, totalCost

# Calculate overcharge based on average for A/C usage
def overchargeParser(dayCosts, output, avgCost):
    print("\nOvercharges:")
    output.write("\nOvercharges:\n")
    totalOvercharge = 0.0
    majorityMonthEnable = False
    for days in dayCosts:
        if days.split('-')[2] == "01": # change day to start counting overcharges
            majorityMonthEnable = True
        if majorityMonthEnable:
            if dayCosts[days]['Cost'] > avgCost:
                totalOvercharge += dayCosts[days]['Cost'] - avgCost
                print(f"{days}: Overcharge: ${(dayCosts[days]['Cost'] - avgCost):.2f}")
                output.write(f"{days}: Overcharge: ${(dayCosts[days]['Cost'] - avgCost):.2f}\n")
    print(f"Total Overcharge: ${totalOvercharge:.2f}")
    output.write(f"Total Overcharge: ${totalOvercharge:.2f}\n")
    return totalOvercharge

# Calculate final payments
def finalCharges(totalCost, overcharge, absentees, present, absenteepct, adjustments):
    presentPercentage = (1 - absenteepct * absentees) / present 
    absenteeCharge = (totalCost - overcharge) * absenteepct
    presentCharge = (totalCost - overcharge) * presentPercentage
    overchargeFinal = overcharge + presentCharge
    return overchargeFinal, absenteeCharge, presentCharge

def main():
    absentees = personInputChecker("Number of people not in apartment: ")
    present = personInputChecker("Number of people currently in apartment: ")
    absenteepct = pctInputChecker("Percentage of bill each absentee pays (6 people pays 0.167 of bill): ")
    adjustments = realInputChecker("PGE Adjustments: ")
    csvfiles = glob.glob('*.csv')

    for files in csvfiles:
        with open(files, 'r', encoding='utf-8-sig') as csvfile, open("pgeoutput_%s.txt" % (os.path.splitext(files)[0]), 'w') as output:
            print(f'Parsing {files}...\n')
            output.write(f'Parsing {files}...\n\n')

            dayCosts = {}
            customerDetails(csvfile, output)
            AvgCost, totalCost = costParser(csvfile, output, dayCosts)
            totalCost = totalCost - adjustments
            overcharge = overchargeParser(dayCosts, output, AvgCost)

            print(f"\nAdjustments: ${adjustments:.2f}")
            output.write(f"\nAdjustments: ${adjustments:.2f}\n")
            ocFinal, absenteeCharge, presentCharge = finalCharges(totalCost, overcharge, absentees, present, absenteepct, adjustments)
            # fix rounding errors
            presentCharge += totalCost - absenteeCharge * absentees - presentCharge * (present - 1) - ocFinal
            
            print(f"\nTotal: ${totalCost:.2f}")
            print(f"Absentee Charge for {absentees} absentees paying {(absenteepct * 100):.2f}%: ${absenteeCharge:.2f}")
            print(f"Present Charge for {present} present: ${presentCharge:.2f}")
            print(f"Present with Overcharge: ${ocFinal:.2f}")
            print(f"\nSession exported to pgeoutput_{os.path.splitext(files)[0]}.txt")
            output.write(f"\nTotal: ${totalCost:.2f}\n")
            output.write(f"Absentee Charge for {absentees} absentees paying {(absenteepct * 100):.2f}%: ${absenteeCharge:.2f}\n")
            output.write(f"Present Charge for {present} present: ${presentCharge:.2f}\n")
            output.write(f"Present with Overcharge: ${ocFinal:.2f}\n")
            
    r = input("Press enter to exit...\n")

if __name__ == "__main__":
    main()
