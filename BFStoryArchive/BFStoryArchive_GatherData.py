import urllib
import glob, os
from threading import Thread
from time import sleep

threadList = []
fileList = []

def checkAvailability(fetched):
    return "NoSuchKey" in fetched or "Not Found"  in fetched or "Request Timeout" in fetched or "Gateway Timeout" in fetched

def gatherDungeonBattle(filename):
    #f = urllib.urlopen("http://dlc.bfglobal.gumi.sg/content/dungeon/" + filename)
    f = urllib.urlopen("http://v2.cdn.android.brave.a-lim.jp/dungeon/" + filename)

    fetched = f.read()
    f.close()

    if checkAvailability(fetched):
        print filename, "not found"
    else:
        print filename
        f = open ("result/" + filename, "wb")
        f.write(fetched)
        f.close()

def gatherNaviChara(filename):    
    #f = urllib.urlopen("http://dlc.bfglobal.gumi.sg/content/event/" + filename)
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

def gatherArea(filename):    
    f = urllib.urlopen("http://dlc.bfglobal.gumi.sg/content/area/" + filename)
    #f = urllib.urlopen("http://v2.cdn.android.brave.a-lim.jp/area/" + filename)
    
    fetched = f.read()
    f.close()
    
    if checkAvailability(fetched):
        print filename, "not found"
    else:
        print filename
        f = open ("result/" + filename, "wb")
        f.write(fetched)
        f.close()

def gatherMap(filename):
    urllib.urlretrieve("http://dlc.bfglobal.gumi.sg/content/raid/raid_map/" + filename, "result/" + filename)

def gatherMapStory(filename):
    f = urllib.urlopen("http://dlc.bfglobal.gumi.sg/content/event/" + filename)
    #f = urllib.urlopen("http://v2.cdn.android.brave.a-lim.jp/event/" + filename)
    fetched = f.read()
    f.close()

    if checkAvailability(fetched):
        print filename, "not found"
    else:
        print filename
        f = open ("result/" + filename, "wb")
        f.write(fetched)
        f.close()

    #urllib.urlretrieve("http://dlc.bfglobal.gumi.sg/content/event/" + filename, "result/" + filename)

def gatherUnitIlls(filename):
    #f = urllib.urlopen("http://dlc.bfglobal.gumi.sg/content/unit/img/" + filename)
    f = urllib.urlopen("http://v2.cdn.android.brave.a-lim.jp//unit/img/" + filename)
    fetched = f.read()
    f.close()
    
    if checkAvailability(fetched):
        print filename, "not found"
    else:
        print filename
        f = open ("result/" + filename, "wb")
        f.write(fetched)
        f.close()
        
    #urllib.urlretrieve("http://dlc.bfglobal.gumi.sg/content/unit/img/" + filename, "result/" + filename)    
    #urllib.urlretrieve("http://dlc.bfglobal.gumi.sg/content/event/" + filename, "result/" + filename)
    #urllib.urlretrieve("http://v2.cdn.android.brave.a-lim.jp/event/" + filename, "result/" + filename)


############################################################
#==========================================================#
############################################################


if __name__ == "__main__":

    #for filename in glob.glob("BFStoryArchive/" + "*.jpg"):
    #for filename in glob.glob("BFStoryArchive/" + "*.png"):
    #    filename = filename[15:]
    #    fileList.append(filename)
    #for filename in glob.glob("*.jpg"):
    #for filename in glob.glob("*.txt"):
    #    fileList.append(filename)
    #for filename in glob.glob("BFStoryArchive/" + "*.jpg"):
    #for filename in glob.glob("*.txt"):
        #filename = filename[:-4]
        #fileList.append(filename)

##    for i in range(1, 7):
##        for j in range(1, 150):
##            for k in range(7, 9):
##                s = "unit_ills_full_8%d%03d%d.png" % (i, j, k)
##                print s
##                fileList.append(s)

    alreadyExistFiles = []

    for filename in glob.glob("result/" + "*.png"):    
        alreadyExistFiles.append(filename)

    # Summoner Avatar
    for i in range(0, 100):
        for j in range(1, 20):
            for k in range(6, 7):
                s = "unit_ills_full_10%02d%02d%02d_U.png" % (i, j, k)
                print s
                fileList.append(s)
                s = "unit_ills_full_10%02d%02d%02d_L.png" % (i, j, k)
                print s
                fileList.append(s)    


##    for x in range(20, 30):
##        fileList.append("grand_%d_op.txt" % (x,)) 
##        for i in range(0, 50):
##            fileList.append("grand_%d_%02d.txt" % (x,i))        

##    for i in range(103, 104):
##        fileList.append("map%d-open.txt" % (i,))
##        fileList.append("map%d-open2.txt" % (i,))
##        for j in range(0, 15):
##            fileList.append("map%d-dungeon%d.txt" % (i,j))
##            for k in range(0, 5):
##                fileList.append("map%d-dungeon%d-%d.txt" % (i,j,k))
##        fileList.append("map%d-ending.txt" % (i,))
##        fileList.append("map%d-dungeon_ex_open.txt" % (i,))
##        fileList.append("map%d-dungeon_ex_clear.txt" % (i,))
##        fileList.append("map%d-dungeon_ex1_clear.txt" % (i,))
##        fileList.append("map%d-dungeon_ex2_clear.txt" % (i,))


##    for i in range(80, 250):
##        #fileList.append("navi_chara80%03d.png" % (i,))
##        fileList.append("navi_chara%d.png" % (i,))
##        for j in range(0, 12):            
##            #fileList.append("navi_chara_80%02d_%d.png" % (i,j))
##            fileList.append("navi_chara%d_%d.png" % (i,j))

##    for i in range(0, 100):
##        fileList.append("area_%04d.jpg" % (i,))
##        fileList.append("area_plate_%04d.png" % (i,))
##    for i in range(100, 200):
##        fileList.append("area_%03d.jpg" % (i,))
##        fileList.append("area_plate_%03d.png" % (i,))

##    for i in range(0, 20):
##        fileList.append("raid_804_%d.txt" % (i,))

    for i, filename in enumerate(fileList):        
        #threadList.append(Thread(target = gatherDungeonBattle, args = (filename,)))
        #threadList.append(Thread(target = gatherNaviChara, args = (filename,)))
        #threadList.append(Thread(target = gatherMapStory, args = (filename,)))
        threadList.append(Thread(target = gatherUnitIlls, args = (filename,)))
        #threadList.append(Thread(target = gatherArea, args = (filename,)))

    for threadIndividual in threadList:
        sleep(0.02)
        threadIndividual.start()
    
    for threadIndividual in threadList:
        threadIndividual.join()

