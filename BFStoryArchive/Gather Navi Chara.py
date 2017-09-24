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
        f = urllib.request.urlopen("http://v2.cdn.android.brave.a-lim.jp/event/" + filename)
        fetched = f.read()
        f.close()   
    
        print(filename)
        f = open ("result/" + filename, "wb")
        f.write(fetched)
        f.close()

        global foundFilesCount
        foundFilesCount += 1

        write_to_log("BFJP Navi Chara", "Found " + filename + "\n")
        
    except urllib.error.URLError:    
        print("File not found : ", filename)
    


############################################################
#==========================================================#
############################################################


if __name__ == "__main__":

    alreadyExistFiles = []

    for filename in glob.glob("result/" + "*.png"):        
        alreadyExistFiles.append(filename[7:])
    
    for i in range(1, 200):

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
    
    write_to_log("BFJP Navi Chara", "Found " + str(foundFilesCount) + " new files, " + str(len(alreadyExistFiles)) + " already exist files\n")
