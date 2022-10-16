import sys

from utils import utilities

# Get CLI for input
if (len(sys.argv) != 2):
    print("Specify your WOL directory")
    exit()
WOLPath = sys.argv[1]

myUtils = utilities(WOLPath)

# Filter by only military units
unitList = list(filter(lambda unit: myUtils.isValidUnit(unit),myUtils.protoyXml))



docFormat = [{'header': 'Name', 'function': lambda unitSchema: myUtils.getUnitName(unitSchema)},
             {'header': 'Food', 'function': lambda unitSchema: myUtils.prettyValue(
                 myUtils.getResourceCost(unitSchema, 'Food'))},
             {'header': 'Wood', 'function': lambda unitSchema: myUtils.prettyValue(
                 myUtils.getResourceCost(unitSchema, 'Wood'))},
             {'header': 'Gold', 'function': lambda unitSchema: myUtils.prettyValue(myUtils.getResourceCost(unitSchema, 'Coin'))},
             {'header': 'Trainable By', 'function': lambda unitSchema: myUtils.prettyValue(myUtils.findCivsThatCanTrain(unitSchema))}]


# construct the CSV
csv = ''
for column in docFormat:
    csv += column['header'] + ','
csv = csv[:-1]
csv += '\n'

for unit in unitList:
    for column in docFormat:
        csv += (column['function'](unit) or '-') + ','
    csv = csv[:-1]
    csv += '\n'

# write to csv
f = open("output.csv", "w")
f.write(csv)
