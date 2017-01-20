import urllib
import glob, os
from threading import Thread
from time import sleep

threadList = []
fileList = []

def checkAvailability(fetched):
    return "NoSuchKey" in fetched or "Not Found"  in fetched or "Request Timeout" in fetched or "Gateway Timeout" in fetched

def gatherNaviChara(filename):    
    f = urllib.urlopen("http://v2.cdn.android.brave.a-lim.jp/event/" + filename)
    fetched = f.read()
    f.close()
    
    if checkAvailability(fetched):
        print filename, "not found"
    else:
        print filename
        f = open ("result/" + filename, "wb")
        f.write(fetched)
        f.close()


############################################################
#==========================================================#
############################################################


if __name__ == "__main__":

    alreadyExistFiles = []

    for filename in glob.glob("result/" + "*.png"):        
        alreadyExistFiles.append(filename[7:])
    
    for i in range(1, 150):

        s = "navi_chara%d.png" % (i,)

        if not (s in alreadyExistFiles):
            fileList.append(s)

        for j in range(0, 10):

            s = "navi_chara%d_%d.png" % (i,j)
            
            if not (s in alreadyExistFiles):
                fileList.append(s)

    for i, filename in enumerate(fileList):        
        threadList.append(Thread(target = gatherNaviChara, args = (filename,)))

    for threadIndividual in threadList:
        sleep(0.02)
        threadIndividual.start()
    
    for threadIndividual in threadList:
        threadIndividual.join()

