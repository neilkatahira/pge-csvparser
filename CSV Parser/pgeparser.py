import csv
import glob

def personInputChecker(msg):
    boolpos = False
    while not boolpos:
        val = int(input(msg))
        if val >= 0:
            boolpos = True
        else:
            print("Enter a valid positive integer")
    return val

def pctInputChecker(msg):
    validPct = False
    while not validPct:
        val = float(input(msg))
        if val > 0 and val < 1:
            validPct = True
        else:
            print("Enter a valid percentage between 0 and 1")
    return val

def customerDetails(csvfile, output):
    custDetails = csv.reader(csvfile)
    for i in range(4):
        custLine = next(custDetails)
        print("%s: %s" % (custLine[0], custLine[1]))
        output.write("%s: %s\n" % (custLine[0], custLine[1]))
    next(csvfile) # skip line between customer details and costs

def costParser(csvfile, output, dayCosts):
    costs = csv.DictReader(csvfile)
    currentDate = units = ""
    totalCost = totalUsage = currentCost = currentUsage = majorityMonthCost = 0.0
    days = 0
    scalingFactor = 0.24 / 0.31 # tier 1 to tier 2 PGE electric difference
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
            dayCosts[currentDate] = dict({'Usage': currentUsage,
                                          'Cost': currentCost, 'Units': units})
            # start day count at beginning of month
            if currentDate.split('-')[2] == "01": 
                majorityMonthEnable = True
            currentDate = line["DATE"]
            units = line["UNITS"]
            if majorityMonthEnable:
                days += 1
                majorityMonthCost += currentCost
            currentCost = currentUnits = currentUsage = extPay = 0.0
    print("Total Cost: $%.2f, Total Usage: %.2f%s, Avg Cost/day: $%.2f,"
          " Scaled Avg: $%.2f" % (totalCost, totalUsage, units,
          majorityMonthCost / days, majorityMonthCost * scalingFactor / days))
    output.write("Total Cost: $%.2f, Total Usage: %.2f%s, Avg Cost/day: $%.2f,"
          " Scaled Avg: $%.2f\n" % (totalCost, totalUsage, units,
          majorityMonthCost / days, majorityMonthCost * scalingFactor / days))
    return majorityMonthCost * scalingFactor / days, totalCost

def overchargeParser(dayCosts, output, avgCost):
    print("\nOvercharges:")
    output.write("\nOvercharges:\n")
    totalOvercharge = 0.0
    majorityMonthEnable = False
    for days in dayCosts:
        if days.split('-')[2] == "13": #general hard code for after finals
            majorityMonthEnable = True
        if majorityMonthEnable:
            if dayCosts[days]['Cost'] > avgCost:
                totalOvercharge += dayCosts[days]['Cost'] - avgCost
                print("%s: Overcharge: $%.2f" % (days, dayCosts[days]['Cost'] - avgCost))
                output.write("%s: Overcharge: $%.2f\n" % (days, dayCosts[days]['Cost'] - avgCost))
    print("Total Overcharge: $%.2f" % (totalOvercharge))
    output.write("Total Overcharge: $%.2f" % (totalOvercharge))
    return totalOvercharge

def finalCharges(totalCost, overcharge, absentees, present, absenteepct):
    #Present pays leftover percentage disregarding overcharge
    presentPercentage = (1 - absenteepct * absentees) / present 
    absenteeCharge = (totalCost - overcharge) * absenteepct
    presentCharge = (totalCost - overcharge) * presentPercentage
    overchargeFinal = overcharge + presentCharge
    return overchargeFinal, absenteeCharge, presentCharge

csvfiles = glob.glob('*.csv')
absentees = personInputChecker("Number of people not in apartment: ")
present = personInputChecker("Number of people currently in apartment: ")
absenteepct = pctInputChecker("Percentage of bill each absentee pays (6 people pays 0.167 of bill): ")

for files in csvfiles:
    print("Parsing %s...\n" % (files))
    with open(files, 'r', encoding='utf-8-sig') as csvfile, open("pgeoutput.txt", 'w') as output:
            output.write("Parsing %s...\n\n" % (files))
            dayCosts = {}
            customerDetails(csvfile, output)
            scaledAvgCost, totalCost = costParser(csvfile, output, dayCosts)
            overcharge = overchargeParser(dayCosts, output, scaledAvgCost)
            ocFinal, absenteeCharge, presentCharge = finalCharges(totalCost, overcharge,
                                                                  absentees, present, absenteepct)
            presentCharge += totalCost - absenteeCharge * absentees - presentCharge * (present - 1) - ocFinal # fix rounding errors
            print("\nTotal: $%.2f" % (totalCost))
            print("Absentee Charge: $%.2f" % (absenteeCharge))
            print("Present Charge: $%.2f" % (presentCharge))
            print("Present with Overcharge: $%.2f" % (ocFinal))
            output.write("\nTotal: $%.2f\n" % (totalCost))
            output.write("Absentee Charge: $%.2f\n" % (absenteeCharge))
            output.write("Present Charge: $%.2f\n" % (presentCharge))
            output.write("Present with Overcharge: $%.2f\n" % (ocFinal))
            print("\nSession exported to pgeoutput.txt")
