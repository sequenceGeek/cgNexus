import bioLibCG
from cgNexus import Nexus
from cgNexusFlat import Nexus as NexusOld
import cgDL
from cgAutoCast import autocast
from cgAutoKeyWord import autokey
from bioLibJA import subit
from theTable import cgTest

def testNX(fN, fF):

    NX = Nexus(fN, fF)
    NX.load(['geneName', 'numReads', 'otherIDs'])

    for id in NX.ids:
        NX.id = id
        NX.geneName = 'CHANGE'
    
    NX.save()

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
    if sys.argv[1] == "help":
        bioLibCG.gd(sys.argv[0])
    else:
        bioLibCG.submitArgs(globals()[sys.argv[1]], sys.argv[1:])
