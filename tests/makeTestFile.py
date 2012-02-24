import bioLibCG
from cgNexus import Nexus
import cgDL
from cgAutoCast import autocast
from cgAutoKeyWord import autokey
from bioLibJA import subit

@autocast
def makeFile(numberLines, outFN):

    fOut = open(outFN, 'w')
    for i in range(numberLines):
        fOut.write('%s\t%s\t%s\t%s\n' % (i, 'XRN1', 1000, '1,2,3'))
    fOut.close()
    

if __name__ == "__main__":
    import sys
    if sys.argv[1] == "help":
        bioLibCG.gd(sys.argv[0])
    else:
        bioLibCG.submitArgs(globals()[sys.argv[1]], sys.argv[1:])

