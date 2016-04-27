import urllib
import glob, os
from threading import Thread

threadList = []
fileList = []

def gatherDungeonBattle(filename):
    urllib.urlretrieve("http://dlc.bfglobal.gumi.sg/content/dungeon/" + filename, filename)

def gatherNaviChara(filename):
    urllib.urlretrieve("http://dlc.bfglobal.gumi.sg/content/event/" + filename, filename)

def gatherMap(filename):
    urllib.urlretrieve("http://dlc.bfglobal.gumi.sg/content/raid/raid_map/" + filename, "result/" + filename)

def gatherMapStory(filename):
    #urllib.urlretrieve("http://dlc.bfglobal.gumi.sg/content/event/" + filename, "result/" + filename)
    urllib.urlretrieve("http://v2.cdn.android.brave.a-lim.jp/" + filename, "result/" + filename)

if __name__ == "__main__":

    #for filename in glob.glob("BFStoryArchive/" + "*.jpg"):
    #for filename in glob.glob("BFStoryArchive/" + "*.png"):
    #    filename = filename[15:]
    #    fileList.append(filename)
    #for filename in glob.glob("*.jpg"):
    #for filename in glob.glob("*.txt"):
    #    fileList.append(filename)

    #for filename in glob.glob("BFStoryArchive/" + "*.jpg"):
    #for filename in glob.glob("BFStoryArchive/" + "*.png"):
        #filename = filename[15:]
        #fileList.append(filename)

    #for i in range(0, 10):
    #    fileList.append("navi_chara39_%d.png" % (i,))

    #for i in range(50, 120):
    #    for j in range(0, 12):
    #        filename = "navi_chara%d_%d.png" % (i, j)
    #        fileList.append(filename)

    for i, filename in enumerate(fileList):
        #threadList.append(Thread(target = gatherDungeonBattle, args = (filename,)))
        threadList.append(Thread(target = gatherMapStory, args = (filename,)))

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

