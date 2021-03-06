import os

import cgLuckyCharmsFlat as cgLuckyCharms
from copy import copy
import cgFile

def lineUpdate(lineData, colPos__newVal):
    '''lineList must NOT contain CR.  data must be string'''
    numCurrentSlots = len(lineData) #should be same every time...just pass as argument
    
    for colPos, newVal in colPos__newVal:

        #put data in right position
        if colPos < numCurrentSlots:
            lineData[colPos] = newVal 
        else:
            #update lines that don't exist/have no values
            for i in range(numCurrentSlots, colPos):
                lineData.append('.')
            lineData.append(newVal)
    
    return lineData

class Nexus:

    def __init__(self, dataFileName, dataFormatFN, loadHints = '', paraInfo = [None, None], ids = True):
        self._dataFileName = dataFileName
        self._dataFormatFN = dataFormatFN
        self._attName__formatInfo = {} # name: (position, type, default)
        self._attName_id_value = {}
        self._attName_casteFromFxn = {}
        self._attName_casteToFxn = {}
        self._attName_columnPosition = {}
        self._attName_defaultValue = {}
        self._loadedAttNames = []
        self._packetInfo = None
        self._splitRunFlag = False
        self._iterIDGen = None
        self._ids = None
        self.id = None #have to init to packet starting id
        self.hasIDs = ids
        
        #initialize Nexus
        #TODO optional initialization of ids if there are hints...
        #may be able to just load "first ID in file and when it loops through it will load the rest?"
        self.initializePacketInfo(paraInfo)
        self._initializeIDs()
        self.id = (x for x in self._ids).next()
        self.numSlots = self.getNumberOfSlots()
        self.loadFormatInfo()
        self.loadTranscriptionInfo() #loading/casting fxn loading

        #used for get/set efficiency
        self._initialzed = True
        
        #initial load if specified 
        if loadHints:
            self.load(loadHints.split(' '))


    def __getattr__(self, name):
        '''this will only work for attributes that arent defined
        note: try/except faster than if/else'''
        try:
            return self._attName_id_value[name][self.id]
        except KeyError:
            #first load attribute
            if name in self._attName__formatInfo: #name in text table?
                self.load([name])
                return self._attName_id_value[name][self.id]
            else:
                raise NameError("Cannot get Attribute: it is not in text table")

        
    def __setattr__(self, name, value):
        '''this will set EVERYTHING if possible
        note try/except was faster than if/else'''
        #NOTE TRY SPEED FOR __dict__
        #TODO is this slowing down id scrolling?
        #print 'setting', name 
        try:
            self.__dict__['_attName_id_value'][name][self.id] = value
        except KeyError:
            #print '..NON DATA ATTRIBUTE'

            # check if attribute needs loading (error if trying to load attribute that isnt in format table)
            #TODO no way of knowing if accidentally setting property that is not in table
            #for instance if the user meant to type NX.geneName but typed NX.genename....
            #may make all private variables _X and if it isnt private and isnt in format file....raise error
            if '_initialzed' in self.__dict__:
                if (name in self.__dict__['_attName__formatInfo']) and (name not in self._loadedAttNames):
                    self.load([name])
                    self.__dict__['_attName_id_value'][name][self.id] = value
                    return
            
            # set "normal" object property
            #print '....setting normal prop', name
            self.__dict__[name] = value

    def __str__(self):
        newLines = []
        for id in self._ids:
            newLine = [str(id)]
            
            for attName in self._attName_id_value:
                newLine.append(str(self._attName_id_value[attName][id]))
            newLines.append('\t'.join(newLine))    

        return '\n'.join(newLines)

    def __iter__(self):
        self.resetLoop()
        return self
   
    def next(self):
        
        if self.nextID():
            return self
        else:
            raise StopIteration
    
    def _initializeIDs(self):
        
        with open(self._dataFileName, 'r') as f:
            self._ids = set(int(x.split('\t')[0]) for x in f)

    def resetLoop(self):
        self._iterIDGen = None

    def nextID(self):
        if self._iterIDGen:
            try:
                self.id = self._iterIDGen.next()
                return True
            except StopIteration:
                self._iterIDGen = None
                return False
        else:
            self._iterIDGen = (x for x in self._ids)
            self.id = self._iterIDGen.next()
            return True
       
    def loadFormatInfo(self):
        '''from column format file, get positions and such
        0 is always the id so start from 1'''

        #handle quickFormat
        if type(self._dataFormatFN) == type([]):
            for formatLine in self._dataFormatFN:
                colNum, attName, theType, defValue = formatLine.strip().split(' ')
                colNum = int(colNum)
            
                #check for empty lists:
                if 'List' in theType and defValue == '.':
                    defValue = list()
                else:
                    defValue = cgLuckyCharms.getCasteFunction(theType)(defValue)

                self._attName__formatInfo[attName] = (colNum, theType, defValue) 
        #handle file
        else:
            f = open(self._dataFormatFN, 'r')
            for i, line in enumerate(f):

                #blank line means skipped data
                if line.strip() == '': continue 

                #get formatting info
                attName, theType, defValue = line.strip().split('\t')

                #check for empty lists:
                if 'List' in theType and defValue == '.':
                    defValue = list()
                else:
                    defValue = cgLuckyCharms.getCasteFunction(theType)(defValue)

                self._attName__formatInfo[attName] = (i + 1, theType, defValue) 
            f.close()
            
    def loadTranscriptionInfo(self):
        '''loads caste fxns, column positions, default values for each ALL attributes in format file'''		

        for attName in self._attName__formatInfo:
            dataSlot, dataType, dataDefault = self._attName__formatInfo[attName]
            self._attName_casteFromFxn[attName] = cgLuckyCharms.getCasteFunction(dataType, True)
            self._attName_casteToFxn[attName] = cgLuckyCharms.getCasteFunction(dataType, False)
            self._attName_columnPosition[attName] = dataSlot
            self._attName_defaultValue[attName] = dataDefault

    def updateMasterDict(self, attNames):
        #initialize master dict
        for attName in attNames:
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
        self._ids = self._attName_id_value[self._loadedAttNames[0]]

    def initializePacketInfo(self, paraInfo):

        #for split runs 
        if paraInfo == ['splitRun', 'splitRun']:
            self._splitRunFlag = True
            paraInfo = [None, None] # now treat paraInfo as if there was nothing...
       
        #for normal runs
        if paraInfo != [None, None]: 
            paraInfo[0] = int(paraInfo[0])
            paraInfo[1] = int(paraInfo[1])
            self._packetInfo = cgFile.getPacketInfo(self._dataFileName, paraInfo[1])[paraInfo[0] - 1]

    def load(self, attNames):
        '''load attributes specified into nexus master dictionary.  Should be callable multiple times
        during Nexus lifetime'''

        #print 'loading', attNames

        #update selected attribute names
        [self._loadedAttNames.append(x) for x in attNames if x not in self._loadedAttNames]		

        #make entry in master dictionary
        [self.updateMasterDict([x]) for x in attNames if x not in self._attName_id_value]

        #open file and binary skip to correct line if packet            
        dataFile = cgFile.cgFile(self._dataFileName)
        if self._packetInfo:
            dataFile.seekToLineStart(self._packetInfo[0])

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
                if colPosition < self.numSlots:
                    if ls[colPosition] != '.':
                        self._attName_id_value[attName][id] = self._attName_casteFromFxn[attName](ls[colPosition])
                    elif 'List' in self._attName__formatInfo[attName][1]: #change "in" to ==[-4:]?
                        self._attName_id_value[attName][id] = self._attName_defaultValue[attName][:]
                    else:
                        self._attName_id_value[attName][id] = copy(self._attName_defaultValue[attName])
                else:
                    self._attName_id_value[attName][id] = self._attName_defaultValue[attName] #no need for copy on primitive types

        dataFile.file.close()
        
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
           
            #id = int(ls[0]) if self.hasIDs else currentID
            if self.hasIDs:
                id = int(ls[0])
            else:
                id = currentID
                currentID += 1
            
            if self._packetInfo:
                if id == self._packetInfo[1]: break

            #save the rest
            colPos__vals = [(self._attName_columnPosition[x], self._attName_casteToFxn[x](self._attName_id_value[x][id])) for x in self._loadedAttNames]
            ls = lineUpdate(ls, colPos__vals)

            #only one newLine no matter the amount of attributes updated	
            newLines.append('%s\n' % '\t'.join(ls))
        dataFile.file.close()

        #output file
        #TODO have to write as you update...test if causes I/O clogging.  Can buffer it anyways...
        #update line --> write to temp file --> rename file after writing complete
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
        #TODO should load attribute if not loaded?
        
        '''if id-->attribute, return copy of already made id-->att.  SHOULD be copy because editing of original
        Nexus data should not be allowed'''
        if attributeOneName == 'id':
            return copy(self._attName_id_value[attributeTwoName])

        #if att1 is a list it is unhashable --> turn into tuple
        convertToTuple = (type(self._attName_id_value[attributeOneName][self.id]) == type([]))

        #get requested mapping
        att1_att2 = {}
        while self.nextID():

            #get One//wont be id --> covered above
            att1Val = self._attName_id_value[attributeOneName][self.id]
            if convertToTuple:
                att1Val = tuple(att1Val)
            
            #get Two
            if attributeTwoName == 'id':
                att2Val = self.id
            else:
                att2Val = self._attName_id_value[attributeTwoName][self.id]

            #update map
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

class GNexus(Nexus):

    def __init__(self, dataFileName, dataFormatFN, loadHints = '', paraInfo = [None, None], ids = True):
        #TODO refactor to Base Nexus class and Nexus ang GNexus to get rid of overlapping functions
        self._dataFileName = dataFileName
        self._dataFile = None
        self._tempOutFN = dataFileName + '~'
        self._tempOutFile = open(self._tempOutFN, 'w')
        self._dataFormatFN = dataFormatFN
        self._attName__formatInfo = {} # name: (position, type, default)
        self._attName_value = {}
        self._attName_casteFromFxn = {}
        self._attName_casteToFxn = {}
        self._attName_columnPosition = {}
        self._attName_defaultValue = {}
        self._loadedAttNames = []
        self.id = None #have to init to packet starting id
        self.hasIDs = ids
        
        #initialize Nexus
        #TODO optional initialization of ids if there are hints...
        #may be able to just load "first ID in file and when it loops through it will load the rest?"
        self.numSlots = self.getNumberOfSlots()
        self.loadFormatInfo() #load colPositions, var names, var types
        self.loadTranscriptionInfo() #loading/casting fxn loading
        self._initialized = True

    def __getattr__(self, name):
        '''this will only work for attributes that arent defined
        note: try/except faster than if/else'''
        try:
            return self.__dict__['_attName_value'][name]
        except KeyError:
            #all attributes are loaded per line so must not be attribute
            raise NameError("Cannot get Attribute: \"" + name + "\" is not in table")

    def __setattr__(self, name, value):
        '''this will set EVERYTHING if possible'''

        #try to set data attribute
        #have to check if the format files have even been created yet
        if "_initialized" in self.__dict__: 
            if self.__dict__['_initialized']:
                if name in self._attName__formatInfo:
                    self.__dict__['_attName_value'][name] = value
                    return None
                
        # set "normal" object property
        self.__dict__[name] = value

    def __iter__(self):
        #TODO maybe should have data container object for current id
        #can just bind attribute names to the line container
        #makes get/set much easier
        #this will fix regular nexus get/set problems as well
        if self._dataFile:
            self._dataFile.close()

        self._dataFile = open(self._dataFileName, 'r')
        return self

    def next(self):
        '''go to next line in file'''
        nextLine = self._dataFile.readline()
        if nextLine == '':
            self._dataFile.close()
            self._dataFile = None
            raise StopIteration
        else:
            self._loadNextLine(nextLine)
            #kinda funky returning self -> should make a separate "struct" object
            return self 

    def nextline(self):

        nextLine = self._dataFile.readline()
        if nextLine == '':
            return None
        else:
            self._loadNextLine(nextLine)
            return True 

    def _loadNextLine(self, nextLine):
        '''cast each value in line and place in attribute dictionary'''
        #extract line 
        ls = nextLine[:-1].split('\t')
     
        #update id
        if self.hasIDs:
            self.id = int(ls[0])
        else:
            id = (id + 1) if id != None else 0

        #update ALL parameters
        #TODO it may be faster to only update "loaded" parameters (i.e, only ones being used)
        for attName in self._attName_columnPosition:
            colPosition = self._attName_columnPosition[attName]
            if colPosition < self.numSlots:
                if ls[colPosition] != '.':
                    self._attName_value[attName] = self._attName_casteFromFxn[attName](ls[colPosition])
                elif 'List' in self._attName__formatInfo[attName][1]: #change "in" to ==[-4:]?
                    self._attName_value[attName] = self._attName_defaultValue[attName][:]
                else:
                    #TODO this copy is suspect, why is it needed?
                    self._attName_value[attName] = copy(self._attName_defaultValue[attName])
            else:
                #TODO dont i need to [:] for list?
                self._attName_value[attName] = self._attName_defaultValue[attName] #no need for copy on primitive types
    
    def write(self):
        '''write current line contents to temp file...save will overwrite/write read outfile'''
       
        outList = ['.' for x in self._attName__formatInfo] 

        if self.hasIDs:
            outList = [str(self.id)] + outList

        for attName in self._attName__formatInfo:
            #which column should the attribute be written to?
            colPos = self._attName_columnPosition[attName]
            colPos = colPos if self.hasIDs else colPos - 1 #tables are 1-based (if you ignore IDs)

            #output the value into a string representation of the value
            stringVal = self._attName_casteToFxn[attName](self._attName_value[attName])

            outList[colPos] = stringVal

        self._tempOutFile.write('\t'.join(outList) + '\n')

    def save(self, outFN = None):
        '''The writing is all done inner loop, this just renames the temp file to outFile'''

        if not outFN: outFN = self._dataFileName

        #flush temp file first before 
        #TODO should "exhaust" this GNX instance by marking it "used" in __iter__
        self._tempOutFile.close()
        os.rename(self._tempOutFN, outFN)

    def create_map(self, attributeOneName, attributeTwoName, assumeUnique = True):
        '''once Nexus is loaded user may need a different data mapping besides id-->attribute
        This allows user to create custom mappings. Note: 'id' will give back self.id'''
        #TODO make create_maps where it returns multiple dictionaries
        
        #if att1 is a list it is unhashable --> turn into tuple
        convertToTuple = False
        if attributeOneName != 'id':
            convertToTuple = ('List' in self._attName__formatInfo[attributeOneName][1])

        #get requested mapping
        att1_att2 = {}
        for line in self:

            #get One//wont be id --> covered above
            att1Val = self._attName_value[attributeOneName] if attributeOneName != 'id' else self.id
            if convertToTuple:
                att1Val = tuple(att1Val)
            
            #get Two
            att2Val = self._attName_value[attributeTwoName] if attributeTwoName != 'id' else self.id

            #update map
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





















