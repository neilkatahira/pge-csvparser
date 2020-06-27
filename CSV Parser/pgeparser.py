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

# Print first 4 lines of csv file as customer details
def customerDetails(csvfile, output):
    custDetails = csv.reader(csvfile)
    for i in range(4):
        custLine = next(custDetails)
        print("%s: %s" % (custLine[0], custLine[1]))
        output.write("%s: %s\n" % (custLine[0], custLine[1]))
    next(csvfile) # skip line between customer details and costs

# Parse csv file tallying daily and total costs
def costParser(csvfile, output, dayCosts):
    costs = csv.DictReader(csvfile)
    currentDate = units = ""
    totalCost = totalUsage = currentCost = currentUsage = majorityMonthCost = 0.0
    days = 0
    majorityMonthEnable = False

    print("\nDaily Breakdown:")
    output.write("\nDaily Breakdown:\n")
    for line in costs:
        totalCost += float(line["COST"].replace('$', ''))
        totalUsage += float(line["USAGE"])
        if majorityMonthEnable:
            majorityMonthCost
        if units == "":
            units = line["UNITS"]
        if currentDate == "":
            currentDate = line["DATE"]
        if currentDate == line["DATE"]:
            currentUsage += float(line["USAGE"])
            currentCost += float(line["COST"].replace('$', ''))
        else:
            print("Date: %s, Daily Usage: %.2f%s, Daily Cost: $%.2f"  %
                  (currentDate, currentUsage, units, currentCost))
            output.write("Date: %s, Daily Usage: %.2f%s, Daily Cost: $%.2f\n"  %
                  (currentDate, currentUsage, units, currentCost))
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

    avg = majorityMonthCost / days
    print("Total Cost: $%.2f, Total Usage: %.2f%s, Avg Cost/day: $%.2f"
          % (totalCost, totalUsage, units, avg))
    output.write("Total Cost: $%.2f, Total Usage: %.2f%s, Avg Cost/day: $%.2f\n"
                 % (totalCost, totalUsage, units, avg))
    return avg, totalCost

# Calculate overcharge based on average for A/C usage
def overchargeParser(dayCosts, output, avgCost):
    print("\nOvercharges:")
    output.write("\nOvercharges:\n")
    totalOvercharge = 0.0
    majorityMonthEnable = False
    for days in dayCosts:
        if days.split('-')[2] == "13": #general hard code for after finals, set to 01 otherwise
            majorityMonthEnable = True
        if majorityMonthEnable:
            if dayCosts[days]['Cost'] > avgCost:
                totalOvercharge += dayCosts[days]['Cost'] - avgCost
                print("%s: Overcharge: $%.2f" % (days, dayCosts[days]['Cost'] - avgCost))
                output.write("%s: Overcharge: $%.2f\n" % (days, dayCosts[days]['Cost'] - avgCost))
    print("Total Overcharge: $%.2f" % (totalOvercharge))
    output.write("Total Overcharge: $%.2f\n" % (totalOvercharge))
    return totalOvercharge

# Calculate final payments
def finalCharges(totalCost, overcharge, absentees, present, absenteepct):
    presentPercentage = (1 - absenteepct * absentees) / present 
    absenteeCharge = (totalCost - overcharge) * absenteepct
    presentCharge = (totalCost - overcharge) * presentPercentage
    overchargeFinal = overcharge + presentCharge
    return overchargeFinal, absenteeCharge, presentCharge

absentees = personInputChecker("Number of people not in apartment: ")
present = personInputChecker("Number of people currently in apartment: ")
absenteepct = pctInputChecker("Percentage of bill each absentee pays (6 people pays 0.167 of bill): ")
csvfiles = glob.glob('*.csv')

for files in csvfiles:
    with open(files, 'r', encoding='utf-8-sig') as csvfile, open("pgeoutput_%s.txt" % (os.path.splitext(files)[0]), 'w') as output:
        print("Parsing %s...\n" % (files))
        output.write("Parsing %s...\n\n" % (files))

        dayCosts = {}
        customerDetails(csvfile, output)
        AvgCost, totalCost = costParser(csvfile, output, dayCosts)
        overcharge = overchargeParser(dayCosts, output, AvgCost)
        ocFinal, absenteeCharge, presentCharge = finalCharges(totalCost, overcharge, absentees, present, absenteepct)
        # fix rounding errors
        presentCharge += totalCost - absenteeCharge * absentees - presentCharge * (present - 1) - ocFinal
        
        print("\nTotal: $%.2f" % (totalCost))
        print("Absentee Charge for %d absentees paying %.2f%%: $%.2f" % (absentees, absenteepct * 100, absenteeCharge))
        print("Present Charge for %d present: $%.2f" % (present, presentCharge))
        print("Present with Overcharge: $%.2f" % (ocFinal))
        print("\nSession exported to pgeoutput_%s.txt" % (os.path.splitext(files))[0])
        output.write("\nTotal: $%.2f\n" % (totalCost))
        output.write("Absentee Charge for %d absentees paying %.2f%%: $%.2f\n" % (absentees, absenteepct * 100, absenteeCharge))
        output.write("Present Charge for %d present: $%.2f\n" % (present, presentCharge))
        output.write("Present with Overcharge: $%.2f\n" % (ocFinal))
        
r = input("Press enter to exit...\n")
