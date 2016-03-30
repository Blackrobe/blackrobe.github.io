import urllib
import glob, os
from threading import Thread

threadList = []
fileList = []

def gatherDungeonBattle(filename):
    urllib.urlretrieve("http://dlc.bfglobal.gumi.sg/content/dungeon/" + filename, filename)

def gatherNaviChara(filename):
    urllib.urlretrieve("http://dlc.bfglobal.gumi.sg/content/event/" + filename, filename)

if __name__ == "__main__":

    #for filename in glob.glob("BFStoryArchive/" + "*.jpg"):
    for filename in glob.glob("BFStoryArchive/" + "*.png"):
        filename = filename[15:]
        fileList.append(filename)

    for i, filename in enumerate(fileList):
        #threadList.append(Thread(target = gatherDungeonBattle, args = (filename,)))
        threadList.append(Thread(target = gatherNaviChara, args = (filename,)))

    for threadIndividual in threadList:
        threadIndividual.start()
    
    for threadIndividual in threadList:
        threadIndividual.join()

        

#for i in range(1, 2):
    #urllib.urlretrieve("http://dlc.bfglobal.gumi.sg/content/event/navi_chara80%03d.png" % (i), "navi_chara80%03d.png" % (i))    
    #for j in range(0, 20):
        #urllib.urlretrieve("http://dlc.bfglobal.gumi.sg/content/event/navi_chara%s_%s.png" % (i, j), "navi_chara%s_%s.png" % (i, j))

#for i in range(0, 20):
    #urllib.urlretrieve("http://dlc.bfglobal.gumi.sg/content/event/navi_chara35_%s.png" % (i), "navi_chara35_%s.png" % (i))

