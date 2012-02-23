import cgLuckyCharmsFlat as cgLuckyCharms
from copy import copy
import bioLibCG
import cgIndex
import cgFile

'''TODO:
  X 1) make attributes properties for non-[id] access
        a) this means make internal id tracker
    2) load everything on init (call it hints)
  X 3) make format files just a txt file 
        a) need good way to access them...
    3) load items as they are needed
        b) this is complicated cuz going through file every time
        you need to load something is SLOOOOW? or is it?
    4) fix the copy issue, should be able to return default w/o copy


SPEED
replace split with [:-1]
use str.split as splitIt (no dot)
    possibly switch to regex
try to get rid of for loops (use comprehension/map)
'''

def lineUpdate(lineData, data, position):
	'''lineList must NOT contain CR.  data must be string'''

	numSlots = len(lineData)

	#put data in right position
	if position < numSlots:
		lineData[position] = data
	else:
		#update lines that don't exist/have no values
		for i in range(numSlots, position):
			lineData.append('.')
		lineData.append(data)
	
	return lineData

def getNumFileLines(fn):
        for i, l in enumerate(open(fn)):
            pass
	return i + 1

def getIDRange(paraInfo, fn):
	'''numJobs and job number are 1 based'''
	numJobs = int(paraInfo[1])
	n = int(paraInfo[0])
	numIDs = getNumFileLines(fn) #one id per line
	sectorLength = float(numIDs)/numJobs #plus one will not work on small numbers

	rStart = int((n-1)*sectorLength) + 1
	rEnd = int((n)*sectorLength)
	if n == numJobs: rEnd = numIDs - 1
	if n == 1: rStart = 0

	return [rStart, rEnd]	

class Field:

	def __init__(self, dataType, dataDefault, dataSlot):
		self.dataType = dataType
                self.dataDefault = dataDefault #prevents list aggregation
		self.dataSlot = dataSlot

def shellNexus(NX, dataFileName, select):

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
       
        def collapseColumnNumbers(self, attNames):
                
                #make column numbers 0...n
                for i, attName in enumerate(attNames):
                    self._attName_columnPosition[attName] = i
    
	def bindAttributes(self, attributeNames):
		
		#bind data to class attribute for easy access
                for attributeName in attributeNames:
                    setattr(self, attributeName, self._attName_id_value[attributeName])

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
       
                #t = bioLibCG.cgTimer()
                #stage_cumTime = dict( (x, 0.0) for x in (''))
                #t.start()

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

                #print 'after loop', t.split()
                dataFile.file.close()
                
		#bind attribute names to dictionaries
                #self.bindAttributes(attNames) #getattr will get it

                #bind id attribute to first attribute, they all have the same ids...
                self.linkIDsToColumn()
                #print 'finishing stuff', t.split()

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


            att1_att2 = {}
            while self.nextID():

                if attributeOneName == 'id':
                    att1Val = self.id
                else:
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

        def iDictionary(self, property,  assumeUnique = True):
            '''get the property --> id dict for the Nexus
            if assumeUnique dict will not have lists and will give error
            if there is a non-unique mapping.  If not assuming unique, dict will
            have a list as value to keys'''

            theProperty = eval('self.%s' % property)
            iDict = {}
            for id in self.ids:
                val = theProperty[id]
                if val in iDict:

                    if assumeUnique:
                        raise NameError("Mapping is not 1 to 1!")
                    else:
                        iDict[val].append(id)
                
                else:

                    if assumeUnique:
                        iDict[val] = id 
                    else:
                        iDict[val] = [id]

            return iDict                

def quickTable(*args):
    '''make a class for nexus to use as table template
    on the fly
    args are 4tuples (attName, type, defVal, colPosition)'''
    
    class QuickTable: pass

    for col in args:
        setattr(QuickTable, col[0], Field(col[1], col[2], col[3]))
    
    return QuickTable


