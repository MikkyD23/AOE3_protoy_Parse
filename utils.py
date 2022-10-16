import xmltodict

import unidecode


# All extra functions
# Can pass these in as the result for any field

# Since we need to find which civs have access to each unit
# We can find their tech that makes them available, and trace it back to
# age0<CIVNAME>

# with the age0 name we get can the pretty name from civs.xml

class utilities:

    protoyXml = ''
    techtreeXML = ''
    civsXml = ''
    stringTableXml = ''

    def __init__(self, WOLPath):
        # initialise protoy.xml
        f = open(f"{WOLPath}\\data\\protoy.xml",'r')
        self.protoyXml = xmltodict.parse(f.read())['Proto']['Unit']

        # initialise techtreey.xml
        f = open(f"{WOLPath}\\data\\techtreey.xml",'r')
        self.techtreeXML = xmltodict.parse(f.read())['TechTree']['Tech']

        f = open(f"{WOLPath}\\data\\civs.xml",'r')
        self.civsXml = xmltodict.parse(f.read())['civs']['civ']

        # f = open(f"{WOLPath}\\data\\stringtabley.xml",'r',encoding="utf-16-le")
        f = open(f"{WOLPath}\\data\\stringtabley.xml",'r',encoding='utf-16-le')

        # this string table is using utf-16-le
        # so we need to remove all invalid characters before we try and output to file (printing to console is fine)
        self.stringTableXml = xmltodict.parse(f.read())['StringTable']['Language']['String']



    # Returns a list of (pretty printed) civilisations that can train unitName
    def findCivsThatCanTrain(self, unitSchema):
        unitName = unitSchema.get('@name')


        techsThatAllow = []
        for tech in self.techtreeXML:

            if(not 'Effects' in tech or not tech["Effects"] or not "Effect" in tech['Effects']): continue
            if(not self._matchEnableProtoInEffectList(unitName,tech['Effects']["Effect"])): continue

            techsThatAllow.append(tech)

        # For each tech that enables the unit, we find which civ that originates in
        # keep going up the chain until we reach an age0<civ> tech
        civsThatCanTrain = []
        for tech in techsThatAllow:
            foundCiv = self._findTechCivName(tech['@name'],self.techtreeXML,self.civsXml)
            if(foundCiv): civsThatCanTrain.append(foundCiv)

        
        # remove duplicates (because e.g. two age 2 politicians allow a musketeer to be made)
        civsThatCanTrain = list(set(civsThatCanTrain))
        return civsThatCanTrain


    # Looks through the effects of a tech to see if it enabled @unitName
    def _matchEnableProtoInEffectList(self, unitName, effectList):
        # If there's only one effect it makes it a dist, rather than a 1-item list
        if(type(effectList) is dict): effectList = [effectList]

        # Check we have an effect with type=enable, and with a valid target
        effectsWithTargets = list(filter(lambda effect : '@subtype' in effect and effect['@subtype'] == 'Enable' and "Target" in effect,effectList))

        # Check the target exists and matches what we're looking for
        effectsThatMatch = list(filter(lambda effect : '#text' in effect['Target'] and effect['Target']['#text'] == unitName,effectsWithTargets))
        return effectsThatMatch




    def _findTechCivName(self, techName, techTreeXml, civsXml):
        # Check if we're a direct tech (i.e. an ageup)
        directCiv = self._techDirectlyAssociated(techName,civsXml)
        # print(f'_findTechCivName: looking for tech: {techName}. Directly found: {directCiv}')
        if(directCiv): return directCiv

        # Recursively check all techs for this tech's parent
        for tech in techTreeXml:
            techEffects = []
            
            try:
                techEffects = tech['Effects']['Effect']
            except:
                continue

            if(type(techEffects) is dict): techEffects = [techEffects]
            # Check all effects to find one that enables TechName
            for effect in techEffects:
                if(effect.get('@type') == 'TechStatus' and effect.get('@status') == 'obtainable' and effect.get('#text') == techName):
                    # recursive function that will hopefully end at a direct civname
                    return self._findTechCivName(tech['@name'],techTreeXml,civsXml)


        # print(f'ALERT, COULD NOT FIND A CIVNAME FOR TECH:{techName}')
        return False


    def getResourceCost(self, unitSchema,lookFor):
        costs = unitSchema.get('Cost')
        if(not costs): return
        if(type(costs) is dict): costs = [costs]

        for cost in costs:
            if(cost.get('@resourcetype') == lookFor): return cost.get('#text')


    def prettyValue(self,value):
        if(type(value) is str):
            try: return int(value)
            except: return float(value)
            finally: return value
        
        if(type(value) is list):
            accList = ''
            for item in value:
                accList += item + "; "
            return accList
        
        return value
    
    def getUnitName(self,unitSchema):
        name = self._getNameFromStringTable(unitSchema.get('DisplayNameID'))
        return name


    # Find associated language string from stringTable
    def _getNameFromStringTable(self,nameID):
        match = list(filter(lambda entry : entry.get('@_locID') == nameID,self.stringTableXml))

        # Wasn't in the table??
        if(len(match) < 1): return False
        
        unitName = match[0].get('#text')

        assert(type(unitName) is str)

        
        # since it's converted from utf-16-le (and there's invalid characters)
        # remove all non alphanumeric chars
        unitName = unidecode.unidecode(unitName)

        return unitName

    # Returns a pretty civilisation name if the tech is associated with a civ directly
    def _techDirectlyAssociated(self, techName, civsXml):

        for civ in civsXml:
            # print(f"Checking civ: {civ}")
            ageTechs = civ.get('agetech')
            if(not ageTechs): continue
            if(type(ageTechs) is dict): ageTechs = [ageTechs]

            for ageTech in ageTechs:
                # print(ageTech)
                try:
                    if(ageTech['tech'].lower() == techName.lower()): return civ['name']
                except:
                    continue
        # print(f"tech: {techName}, is not directly associated with a civ")
        return False


    def isValidUnit(self, unitSchema):
        # We only want to select units, they would have a unittype called "unit"
        # they would also have at least a HP value
        return 'UnitType' in unitSchema.keys() and 'Unit' in unitSchema['UnitType'] and unitSchema.get('MaxHitpoints')



