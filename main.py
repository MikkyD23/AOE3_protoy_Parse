import sys

from utils import utilities

# Get CLI for input
if (len(sys.argv) != 2):
    print("Specify your WOL directory")
    exit()
WOLPath = sys.argv[1]

myUtils = utilities(WOLPath)

# Filter by only military units
unitList = list(filter(lambda unit: 'UnitType' in unit.keys()
                and 'Military' in unit['UnitType'] and 'Unit' in unit['UnitType'], myUtils.protoyXml))



docFormat = [{'header': 'Name', 'function': lambda unitSchema: myUtils.getUnitName(unitSchema)},
             {'header': '🥩', 'function': lambda unitSchema: myUtils.prettyValue(
                 myUtils.getResourceCost(unitSchema, 'Food'))},
             {'header': '🌳', 'function': lambda unitSchema: myUtils.prettyValue(
                 myUtils.getResourceCost(unitSchema, 'Wood'))},
             {'header': '🥇', 'function': lambda unitSchema: myUtils.prettyValue(myUtils.getResourceCost(unitSchema, 'Coin'))},
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

print(csv).encode('utf-8')