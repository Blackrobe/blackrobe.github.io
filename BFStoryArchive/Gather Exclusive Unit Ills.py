import urllib
import glob, os
from threading import Thread
from time import sleep

threadList = []
fileList = []

def checkAvailability(fetched):
    return "NoSuchKey" in fetched or "Not Found"  in fetched or "Request Timeout" in fetched or "Gateway Timeout" in fetched

def gatherUnitIlls(filename):
    f = urllib.urlopen("http://dlc.bfglobal.gumi.sg/content/unit/img/" + filename)
    #f = urllib.urlopen("http://v2.cdn.android.brave.a-lim.jp//unit/img/" + filename)
    fetched = f.read()
    f.close()
    
    if checkAvailability(fetched):
        print "File not found : ", filename
    else:
        print filename, "found"
        f = open ("resultEX/" + filename, "wb")
        f.write(fetched)
        f.close()

############################################################
#==========================================================#
############################################################


if __name__ == "__main__":

    alreadyExistFiles = []

    for filename in glob.glob("resultEX/" + "*.png"):    
        alreadyExistFiles.append(filename[9:])

    print "Already exist: ", len(alreadyExistFiles)

    for i in range(1, 7):
        for j in range(1, 150):
            for k in range(7, 9):
                s = "unit_ills_full_8%d%03d%d.png" % (i, j, k)                
                if not (s in alreadyExistFiles):
                    fileList.append(s)
                elif (s in alreadyExistFiles):
                    print s, "already exist"

    for i, filename in enumerate(fileList):        
        threadList.append(Thread(target = gatherUnitIlls, args = (filename,)))        

    for threadIndividual in threadList:
        sleep(0.05)
        threadIndividual.start()
    
    for threadIndividual in threadList:
        threadIndividual.join()

