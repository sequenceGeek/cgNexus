import os, sys
sys.path.append('/home/chris/cgNexus')
from cgNexus import Nexus

def testNX(fN, fF):

    NX = Nexus(fN, fF)
    NX.load(['geneName', 'numReads', 'otherIDs'])

    for id in NX.ids:
        NX.id = id
        NX.geneName = 'CHANGE'
    
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
