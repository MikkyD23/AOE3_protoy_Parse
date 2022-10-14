import sys
import xmltodict

# Get CLI for input
if(len(sys.argv) != 2):
    print("Specify the input file directory")
    exit()
inputfile = sys.argv[1]

# read protoy.xml
with open(inputfile,"r") as f:
    # Convert XML to JSON
    xmlFile = xmltodict.parse(f.read())
    unitList = xmlFile['Proto']['Unit']

    # Filter by only military units
    unitList = list(filter(lambda unit : 'UnitType' in unit.keys() and 'Military' in unit['UnitType'],unitList))

    print(unitList)






