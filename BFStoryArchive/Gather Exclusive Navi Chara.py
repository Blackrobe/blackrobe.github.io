import urllib.request, urllib.parse, urllib.error
import glob, os
from threading import Thread
from time import sleep
from utilities import write_to_log, checkAvailability

threadList = []
fileList = []

foundFilesCount = 0

def gatherNaviChara(filename):    
    
    try:
        f = urllib.request.urlopen("http://dlc.bfglobal.gumi.sg/content/event/" + filename)
        fetched = f.read()
        f.close()

        print(filename, "found")
        f = open ("resultEX/" + filename, "wb")
        f.write(fetched)
        f.close()

        global foundFilesCount
        foundFilesCount += 1

        write_to_log("BFGL Navi Chara", "Found " + filename + "\n")
        
    except urllib.error.URLError:    
        print("File not found : ", filename)


    
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
        sleep(0.02)
        threadIndividual.start()
    
    for threadIndividual in threadList:
        threadIndividual.join()

    write_to_log("BFGL Navi Chara", "Found " + str(foundFilesCount) + " new files, " + str(len(alreadyExistFiles)) + " already exist files\n")    
