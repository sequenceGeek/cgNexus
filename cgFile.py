import os
import math
import cgMath

def getPacketInfo(fN, numPackets):
    #packet info is the (a,b) where a is byte of starting line, and b is id of ending line
    numPackets = int(numPackets)
    file = cgFile(fN)
    splitPoints = [int(math.floor(x)) for x in cgMath.linspace(0, file.fileSize, numPackets + 1)]
    packetInfo = []
    idInfo = []

    for packetNumber in range(1, numPackets + 1):

        #start
        if  packetNumber == 1:
            start = 0
        else:
            start = file.getLineStartByte(splitPoints[packetNumber - 1])

        #end
        if packetNumber == numPackets:
            #the last packet doesn't have a line that follows it at the end so it is -1
            end = -1
        else:
            file.seekToLineStart(splitPoints[packetNumber])
            nextLine = file.file.readline()
            end = int(nextLine.strip().split('\t')[0])


        packetInfo.append((start, end))

    return packetInfo                

class cgFile:
    '''return a specific line from an file that has one entry per row (tab spaced columns)'''
    
    def __init__(self, fN):
            
        self.file = open(fN, 'r')
        self.fileSize = os.path.getsize(fN)
                    
    def getLineStartByte(self, i):
            
        j = 1
        while (i - j) > 0:
            self.file.seek(i - j)
            if self.file.read(1) == '\n':				
                return i - j + 1
            j += 1
        
        #if it is the first line of file (while cond failed)
        return 0 #0th byte
    
    def seekToLineStart(self, i):
        startByte = self.getLineStartByte(i)
        self.file.seek(startByte)

