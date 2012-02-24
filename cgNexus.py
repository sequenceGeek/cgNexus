import cgLuckyCharmsFlat as cgLuckyCharms
from copy import copy
import cgFile

def lineUpdate(lineData, data, position):
    '''lineList must NOT contain CR.  data must be string'''
    numSlots = len(lineData) #should be same every time...just pass as argument

    #put data in right position
    if position < numSlots:
        lineData[position] = data
    else:
        #update lines that don't exist/have no values
        for i in range(numSlots, position):
            lineData.append('.')
        lineData.append(data)
    
    return lineData

def shellNexus(NX, dataFileName, select):
    '''used for copying Loaded NXs'''

    newNX = Nexus(dataFileName, NX._dataFormatFN, NX.hasIDs)
    newNX._attName_id_value = {}
    newNX._selectedAttNames = select
    newNX.loadTranscriptionInfo(select)
    newNX._rangeSpecified = copy(NX._rangeSpecified)
    newNX._selectedIDs = set()
    newNX._packetInfo = copy(NX._packetInfo)
    newNX._splitRunFlag = copy(NX._splitRunFlag)
    newNX.hasIDs = NX.hasIDs

    return newNX

class Nexus:

    def __init__(self, dataFileName, dataFormatFN, ids = True):
        self._dataFileName = dataFileName
        self._dataFormatFN = dataFormatFN
        self._attName__formatInfo = {} # name: (position, type, default)
        self._attName_id_value = {}
        self._attName_casteFromFxn = {}
        self._attName_casteToFxn = {}
        self._attName_columnPosition = {}
        self._attName_defaultValue = {}
        self._selectedAttNames = []
        self._rangeSpecified = []
        self._selectedIDs = set()
        self._packetInfo = None
        self._splitRunFlag = False
        self._iterIDGen = None
        self.id = 0 #have to init to packet starting id
        self.hasIDs = ids
       
    def __getattr__(self, name):
        '''this will only work for attributes that arent defined
        note: try/except faster than if/else'''
        return self._attName_id_value[name][self.id]
        
    def __setattr__(self, name, value):
        '''this will set EVERYTHING if possible
        note try/except was faster than if/else'''
        #NOTE TRY SPEED FOR __dict__
        try:
            self.__dict__['_attName_id_value'][name][self.id] = value
        except KeyError:
            if ('_attName__formatInfo' in self.__dict__) and ('_selectedAttNames' in self.__dict__):
                if (name in self.__dict__['_attName__formatInfo']) and (name not in self._selectedAttNames):
                    raise NameError("You need to specify the variable you are saving in hints!")

            self.__dict__[name] = value

    def __str__(self):
        newLines = []
        for id in self.ids:
            newLine = [str(id)]
            
            for attName in self._attName_id_value:
                newLine.append(str(self._attName_id_value[attName][id]))
            newLines.append('\t'.join(newLine))    

        return '\n'.join(newLines)

    def nextID(self):
        if self._iterIDGen:
            try:
                self.id = self._iterIDGen.next()
                return True
            except StopIteration:
                self._iterIDGen = None
                return False
        else:
            self._iterIDGen = self.ids.iterkeys()
            self.id = self._iterIDGen.next()
            return True
       
    def loadFormatInfo(self):
        '''from column format file, get positions and such
        0 is always the id so start from 1'''

        f = open(self._dataFormatFN, 'r')
        for i, line in enumerate(f):

            #blank line means skipped data
            if line.strip() == '': continue 

            #get formatting info
            attName, type, defValue = line.strip().split('\t')

            #check for empty lists:
            if 'List' in type and defValue == '.':
                defValue = list()
            else:
                defValue = cgLuckyCharms.getCasteFunction(type)(defValue)

            self._attName__formatInfo[attName] = (i + 1, type, defValue) 
        f.close()
            
    def loadTranscriptionInfo(self, attNames):
        '''loads caste fxns, column positions, default values for each selected attribute'''		

        if not self._attName__formatInfo:
            self.loadFormatInfo()

        for attName in attNames:
            dataSlot, dataType, dataDefault = self._attName__formatInfo[attName]
            self._attName_casteFromFxn[attName] = cgLuckyCharms.getCasteFunction(dataType, True)
            self._attName_casteToFxn[attName] = cgLuckyCharms.getCasteFunction(dataType, False)
            self._attName_columnPosition[attName] = dataSlot
            self._attName_defaultValue[attName] = dataDefault

    def initializeMasterDict(self):
        #initialize master dict
        for attName in self._selectedAttNames:
            self._attName_id_value[attName] = {}

    def getNumberOfSlots(self):
        try:
            f = open(self._dataFileName, 'r')
            numSlots = len(f.readline().split('\t'))
            f.close()
            return numSlots
        except IOError:
            return 0

    def linkIDsToColumn(self):
        self.ids = self._attName_id_value[self._selectedAttNames[0]]

    def load(self, attNames, paraInfo = [None, None]):
        '''paraInfo is [runNumber, numberOfRuns]'''

        if paraInfo == ['splitRun', 'splitRun']:
            self._splitRunFlag = True
            paraInfo = [None, None] # now treat paraInfo as if there was nothing...
        
        if paraInfo != [None, None]: 
            paraInfo[0] = int(paraInfo[0])
            paraInfo[1] = int(paraInfo[1])
            self._packetInfo = cgFile.getPacketInfo(self._dataFileName, paraInfo[1])[paraInfo[0] - 1]
                
        #if running parallel or specific range, mark range info
        self._selectedAttNames = attNames		
        
        #get casting and column info
        self.loadTranscriptionInfo(attNames)

        #init master dictionaries
        self.initializeMasterDict()

        #get number of slots
        numSlots = self.getNumberOfSlots()
        
        #open file and binary skip to correct line if packet            
        dataFile = cgFile.cgFile(self._dataFileName)
        if self._packetInfo:
            dataFile.seekToLineStart(self._packetInfo[0])

        #print 'before loop', t.split()
        #transcribe values
        currentID = 0
        for line in dataFile.file:

            ls = line.strip().split('\t')

            #get ID
            if self.hasIDs:
                id = int(ls[0]) #id is always first slot
            else:
                id = currentID
                currentID += 1
    
            #stop if at end of range
            if self._packetInfo:
                if id == self._packetInfo[1]:
                    break

            #transcribe
            #Note lots of copying is SLOW (10x)
            #only copy if list?
            #for listed stuff, do not use copy,
            #make new fxn that will just return a copy...faster
            for attName in attNames:
                colPosition = self._attName_columnPosition[attName]
                if colPosition < numSlots:
                    if ls[colPosition] != '.':
                        self._attName_id_value[attName][id] = self._attName_casteFromFxn[attName](ls[colPosition])
                    else:
                        self._attName_id_value[attName][id] = copy(self._attName_defaultValue[attName])
                else:
                    self._attName_id_value[attName][id] = copy(self._attName_defaultValue[attName])

        dataFile.file.close()
        
        #bind id attribute to first attribute, they all have the same ids...
        self.linkIDsToColumn()

    def save(self, outFN = None):
            
        if outFN == None: outFN = self._dataFileName

        if self._packetInfo:
            outFN += '.range.%s.%s' % (self._packetInfo[0], self._packetInfo[1]) 

        
        dataFile = cgFile.cgFile(self._dataFileName)
        if self._packetInfo:
            dataFile.seekToLineStart(self._packetInfo[0])
        
        #create new file contents
        currentID = 0
        newLines = []
        for line in dataFile.file:
            ls = line.strip().split('\t')
            
            if self.hasIDs:
                id = int(ls[0])
            else:
                id = currentID
                currentID += 1
            
            if self._packetInfo:
                if id == self._packetInfo[1]: break

            #save the rest
            #TODO: lineUpdate with multiple injections
            for attName in self._selectedAttNames:
                newVal = self._attName_casteToFxn[attName](self._attName_id_value[attName][id])
                ls = lineUpdate(ls, newVal, self._attName_columnPosition[attName])

            #only one newLine no matter the amount of attributes updated	
            newLines.append('%s\n' % '\t'.join(ls))
        dataFile.file.close()

        #output file
        newLines = ''.join(newLines) #might cause less clogging if there is only one write operation...
        f = open(outFN, 'w')
        f.write(newLines)
        f.close()

        #exit signal for parallel processes
        if self._packetInfo or self._splitRunFlag:
            f = open(outFN + '.exitSignal', 'w')
            f.write('DONE')
            f.close()


    def createMap(self, attributeOneName, attributeTwoName, assumeUnique = True):
        '''once Nexus is loaded user may need a different data mapping besides id-->attribute
        This allows user to create custom mappings. Note: 'id' will give back self.id'''
        
        '''if id-->attribute, return copy of already made id-->att.  SHOULD be copy because editing of original
        Nexus data should not be allowed'''
        if attributeOneName == 'id':
            return copy(self._attName_id_value[attributeTwoName])

        #get requested mapping
        att1_att2 = {}
        while self.nextID():

            #wont be id --> covered above
            att1Val = self._attName_id_value[attributeOneName][self.id]

            if attributeTwoName == 'id':
                att2Val = self.id
            else:
                att2Val = self._attName_id_value[attributeTwoName][self.id]

            if att1Val in att1_att2:

                if assumeUnique:
                    raise NameError("Mapping is not 1 to 1")
                else:
                    att1_att2[att1Val].append(att2Val)
            else:

                if assumeUnique:
                    att1_att2[att1Val] = att2Val
                else:
                    att1_att2[att1Val] = [att2Val]

        return att1_att2

