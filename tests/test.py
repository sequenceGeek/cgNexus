import os, sys
sys.path.append('/home/chris/cgNexus')
sys.path.append('/home/chris/projects/cgNexus')
from cgNexus import Nexus, GNexus

def head(dict):

    rList = []
    for i, (key, value) in enumerate(dict.iteritems()):
        rList.append((key, value))
        if i == 9: break

    return rList

def testNX(fN, fF):

    NX = Nexus(fN, fF, 'geneName numReads isCoding otherIDs')

    print 'START LOOPING'
    for gene in NX:
        gene.isCoding = True
        gene.otherIDs = range(10)
        gene.geneName = "testAuto"
        gene.numReads = 300
    
    NX.save()

def testGNexus(fN, fF):

    gNX = GNexus(fN, fF) 
    id_isCoding = gNX.create_map('id', 'isCoding')
    print head(id_isCoding)
    for read in gNX:
        read.isCoding = False 
        read.write()

    gNX.save()


def testAutoLoad(fN, ff):

    NX = Nexus(fN, ff)

    print 'START LOOPING'
    while NX.nextID():

        NX.isCoding = True
        NX.otherIDs = range(10)
        NX.geneName = "testAuto"
        NX.numReads = 300

    NX.save()

def testQuickLoad(fN):

    ff = ['1 geneName string .',
          '3 otherIDs intList .',
          '4 isCoding bool F'
         ]
    NX = Nexus(fN, ff)

    while NX.nextID():

        NX.isCoding = True
        NX.otherIDs = range(18)
        NX.geneName = "testAuto"
        
    NX.save()

def testMap(fN, fF):

    NX = Nexus(fN, fF)
    NX.load(['geneName', 'numReads', 'otherIDs'])

    geneName_numReads = NX.createMap('otherIDs', 'geneName', False) #not 1to1

    for k,v in geneName_numReads.iteritems():
        print k, v[:5]
        return
    
def testNXOld(fN, fF):

    NX = NexusOld(fN, cgTest)
    NX.load(['geneName', 'geneLength', 'geneTargets'])

    #iterkeys
    for id in NX.ids:
        NX.geneName[id] = 'CHANGE'
    
def testFlat(fN, fF):

    a_b = {}
    b_b = {}
    c_c = {}
    f = open(fN, 'r')
    for line in f:
        ls = line.strip().split('\t')
        
    f.close()
    

    f = open(fN, 'r')
    for line in f:
        ls = line.strip().split('\t')
        a, b, c = ls[1], int(ls[2]), [int(x) for x in ls[3].split(',') if x != '.'] 
    f.close()

if __name__ == "__main__":
    import sys
    assert sys.argv[1] in globals(), "Need name of fxn to run from command line!"
    fxnToRun = globals()[sys.argv[1]] 
    fxnToRun(*sys.argv[2:])
