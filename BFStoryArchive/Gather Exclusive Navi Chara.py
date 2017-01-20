import urllib
import glob, os
from threading import Thread
from time import sleep

threadList = []
fileList = []

def checkAvailability(fetched):
    return "NoSuchKey" in fetched or "Not Found"  in fetched or "Request Timeout" in fetched or "Gateway Timeout" in fetched

def gatherNaviChara(filename):    
    f = urllib.urlopen("http://dlc.bfglobal.gumi.sg/content/event/" + filename)
    fetched = f.read()
    f.close()
    
    if checkAvailability(fetched):
        print "File not found : ", filename
    else:
        print filename, "found"
        f = open ("resultEX/" + filename, "wb")
        f.write(fetched)
        f.close()

if __name__ == "__main__":

    alreadyExistFiles = []

    for filename in glob.glob("resultEX/" + "*.png"):    
        alreadyExistFiles.append(filename[9:])
    
    for i in range(1, 200):

        s = "navi_chara80%03d.png" % (i,)
        
        if not s in alreadyExistFiles:        
            fileList.append(s)

        for j in range(0, 12):

            s = "navi_chara80%03d_%d.png" % (i,j)

            if not s in alreadyExistFiles:
                fileList.append(s)            

    for i, filename in enumerate(fileList):        
        threadList.append(Thread(target = gatherNaviChara, args = (filename,)))

    for threadIndividual in threadList:
        sleep(0.05)
        threadIndividual.start()
    
    for threadIndividual in threadList:
        threadIndividual.join()

