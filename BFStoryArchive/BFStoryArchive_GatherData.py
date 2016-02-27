import urllib

for i in range(1, 2):
    #urllib.urlretrieve("http://dlc.bfglobal.gumi.sg/content/event/navi_chara80%03d.png" % (i), "navi_chara80%03d.png" % (i))    
    for j in range(0, 20):
        urllib.urlretrieve("http://dlc.bfglobal.gumi.sg/content/event/navi_chara%s_%s.png" % (i, j), "navi_chara%s_%s.png" % (i, j))

#for i in range(0, 20):
    #urllib.urlretrieve("http://dlc.bfglobal.gumi.sg/content/event/navi_chara35_%s.png" % (i), "navi_chara35_%s.png" % (i))
