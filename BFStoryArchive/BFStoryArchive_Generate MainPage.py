import glob, os
import codecs
from math import floor
from storyutil import arenaRankName, mapName, grandQuestName

class StoryPage(object):
    def __init__(self):
        self.order = 0
        self.directory = "none"
        self.name = "(Unknown)"

    def __init__(self, pageName):
        if not (pageName[:3].find("map") == -1):
            mapNumber = pageName.split("-")[0][3:]


            # ===============
            # Classic Arc
            # ===============

            
            if (str(mapNumber) in [str(i) for i in range(0, 99)]):
                if not (pageName.find("dungeon_ex") == -1):
                    if not (pageName.find("ex1_clear") == -1):
                        self.setOrder(int(mapNumber)*1000+993)
                        self.setDirectory(pageName)
                        self.setName("Chapter " + mapNumber + " Special: " + mapName[mapNumber]["name"] + " - " + mapName[mapNumber]["special"] + " [ Ending 1 ]")
                    elif not (pageName.find("ex2_clear") == -1):
                        self.setOrder(int(mapNumber)*1000+994)
                        self.setDirectory(pageName)
                        self.setName("Chapter " + mapNumber + " Special: " + mapName[mapNumber]["name"] + " - " + mapName[mapNumber]["special"] + " [ Ending 2 ]")
                    elif not (pageName.find("ex_clear") == -1):
                        self.setOrder(int(mapNumber)*1000+995)
                        self.setDirectory(pageName)
                        self.setName("Chapter " + mapNumber + " Special: " + mapName[mapNumber]["name"] + " - " + mapName[mapNumber]["special"] + " [ Ending ]")
                    else:
                        self.setOrder(int(mapNumber)*1000+990)
                        self.setDirectory(pageName)
                        self.setName("Chapter " + mapNumber + " Special: " + mapName[mapNumber]["name"] + " - " + mapName[mapNumber]["special"])
                elif not (pageName.find("open") == -1):
                    self.setOrder(int(mapNumber)*1000)
                    self.setDirectory(pageName)
                    self.setName("Chapter " + mapNumber + ": " + mapName[mapNumber]["name"] + " [ Opening ]")
                elif not (pageName.find("ending") == -1):
                    self.setOrder(int(mapNumber)*1000+980)
                    self.setDirectory(pageName)
                    self.setName("Chapter " + mapNumber + ": " + mapName[mapNumber]["name"] + " [ Ending ]")
                else:
                    # ===============
                    # Multiple scenes
                    # ===============
                    if len(pageName.split("-")) > 2:
                        dungeonNumber = pageName.split("-")[1][7:]
                        sceneNumber = pageName.split("-")[2]
                        self.setOrder(int(mapNumber)*1000+int(dungeonNumber)*10+int(sceneNumber))
                        self.setDirectory(pageName)
                        self.setName("Chapter " + mapNumber + "-" + dungeonNumber + ": " + mapName[mapNumber]["name"] + " - " + mapName[mapNumber]["dungeon"][dungeonNumber] + " Scene " + sceneNumber)
                    # ===============
                    # Single scene
                    # ===============
                    else:                        
                        dungeonNumber = pageName.split("-")[1][7:]
                        self.setOrder(int(mapNumber)*1000+int(dungeonNumber)*10)
                        self.setDirectory(pageName)
                        self.setName("Chapter " + mapNumber + "-" + dungeonNumber + ": " + mapName[mapNumber]["name"] + " - " + mapName[mapNumber]["dungeon"][dungeonNumber])
            else:

                
                # ===============
                # Summoner's Arc
                # ===============

                
                if (str(mapNumber) in [str(i) for i in range(100, 200)]):
                    if not (pageName.find("dungeon_ex") == -1):
                        if not (pageName.find("ex1_open") == -1):
                            self.setOrder(int(mapNumber)*1000+991)
                            self.setDirectory(pageName)
                            self.setName("Summoner's Arc Chapter " + str(int(mapNumber) % 100) + " Special: " + mapName[mapNumber]["name"] + " - " + mapName[mapNumber]["special1"] + " [ Opening ]")
                        elif not (pageName.find("ex1_clear") == -1):
                            self.setOrder(int(mapNumber)*1000+992)
                            self.setDirectory(pageName)
                            self.setName("Summoner's Arc Chapter " + str(int(mapNumber) % 100) + " Special: " + mapName[mapNumber]["name"] + " - " + mapName[mapNumber]["special1"] + " [ Ending ]")
                        elif not (pageName.find("ex2_open") == -1):
                            self.setOrder(int(mapNumber)*1000+993)
                            self.setDirectory(pageName)
                            self.setName("Summoner's Arc Chapter " + str(int(mapNumber) % 100) + " Special: " + mapName[mapNumber]["name"] + " - " + mapName[mapNumber]["special2"] + " [ Opening ]")
                        elif not (pageName.find("ex2_clear") == -1):
                            self.setOrder(int(mapNumber)*1000+994)
                            self.setDirectory(pageName)
                            self.setName("Summoner's Arc Chapter " + str(int(mapNumber) % 100) + " Special: " + mapName[mapNumber]["name"] + " - " + mapName[mapNumber]["special2"] + " [ Ending ]")
                        elif not (pageName.find("ex_clear") == -1):
                            self.setOrder(int(mapNumber)*1000+995)
                            self.setDirectory(pageName)
                            self.setName("Summoner's Arc Chapter " + str(int(mapNumber) % 100) + " Special: " + mapName[mapNumber]["name"] + " - " + mapName[mapNumber]["special"] + " [ Ending ]")
                        else:
                            self.setOrder(int(mapNumber)*1000+990)
                            self.setDirectory(pageName)
                            self.setName("Summoner's Arc Chapter " + str(int(mapNumber) % 100) + " Special: " + mapName[mapNumber]["name"] + " - " + mapName[mapNumber]["special"])
                    elif not (pageName.find("open") == -1):
                        if not (pageName.find("open1") == -1):
                            self.setOrder(int(mapNumber)*1000)
                            self.setDirectory(pageName)
                            self.setName("Summoner's Arc Chapter " + str(int(mapNumber) % 100) + ": " + mapName[mapNumber]["name"] + " [ Opening 1 ]")
                        elif not (pageName.find("open2") == -1):
                            self.setOrder(int(mapNumber)*1000 + 1)
                            self.setDirectory(pageName)
                            self.setName("Summoner's Arc Chapter " + str(int(mapNumber) % 100) + ": " + mapName[mapNumber]["name"] + " [ Opening 2 ]")
                        else:
                            self.setOrder(int(mapNumber)*1000)
                            self.setDirectory(pageName)
                            self.setName("Summoner's Arc Chapter " + str(int(mapNumber) % 100) + ": " + mapName[mapNumber]["name"] + " [ Opening ]")
                    elif not (pageName.find("ending") == -1):
                        self.setOrder(int(mapNumber)*1000+980)
                        self.setDirectory(pageName)
                        self.setName("Summoner's Arc Chapter " + str(int(mapNumber) % 100) + ": " + mapName[mapNumber]["name"] + " [ Ending ]")
                    else:
                        # ===============
                        # Multiple scenes
                        # ===============
                        if len(pageName.split("-")) > 2:
                            
                            dungeonNumber = pageName.split("-")[1][7:]
                            sceneNumber = pageName.split("-")[2]
                            print "this one: ", pageName, dungeonNumber, sceneNumber
                            self.setOrder(int(mapNumber)*1000+int(dungeonNumber)*10+int(sceneNumber))
                            self.setDirectory(pageName)
                            self.setName("Summoner's Arc Chapter " + str(int(mapNumber) % 100) + "-" + dungeonNumber + ": " + mapName[mapNumber]["name"] + " - " + mapName[mapNumber]["dungeon"][dungeonNumber] + " Scene " + sceneNumber)
                        # ===============
                        # Single scene
                        # ===============
                        else:
                            
                            dungeonNumber = pageName.split("-")[1][7:]
                            print "That one", pageName, dungeonNumber
                            self.setOrder(int(mapNumber)*1000+int(dungeonNumber)*10)
                            self.setDirectory(pageName)
                            self.setName("Summoner's Arc Chapter " + str(int(mapNumber) % 100) + "-" + dungeonNumber + ": " + mapName[mapNumber]["name"] + " - " + mapName[mapNumber]["dungeon"][dungeonNumber])                        
                else:
                    self.setOrder(1000000)
                    self.setDirectory(pageName)
                    self.setName(pageName)
        elif not (pageName[:4].find("tuto") == -1):
            tutorialNumber = pageName[4:]
            self.setOrder(0 + int(tutorialNumber))
            self.setDirectory(pageName)
            self.setName("Chapter 0: Tutorial Scene " + tutorialNumber)
        elif not (pageName.find("GQX") == -1):            
            grandQuestNumber = pageName[3]
            grandQuestID = pageName[2:4]
            if not (pageName[4:].find("OP") == -1):
                self.setOrder(380000 + int(grandQuestNumber)*1000)
                self.setDirectory(pageName)
                self.setName("Exclusive Grand Quest " + grandQuestNumber + ": " + grandQuestName[grandQuestID]["name"] + " [ Opening Scene ]")
            else:
                grandQuestSceneNumber = pageName[-2:]
                if grandQuestSceneNumber.isdigit():
                    self.setOrder(380000 + int(grandQuestNumber)*1000 + int(grandQuestSceneNumber))
                else:
                    self.setOrder(380000 + int(grandQuestNumber)*1000 + int(ord(grandQuestSceneNumber[:-1])))
                self.setDirectory(pageName)
                self.setName("Exclusive Grand Quest " + grandQuestNumber + ": " + grandQuestName[grandQuestID]["name"] + " Scene " + grandQuestSceneNumber)
        elif not (pageName.find("grand") == -1):
            if pageName == "grand_op":
                self.setOrder(300000)
                self.setDirectory(pageName)
                self.setName("Grand Quest Introduction - Dawn of the Summoner")
            elif pageName == "grand_op2":
                self.setOrder(300001)
                self.setDirectory(pageName)
                self.setName("Grand Quest Introduction - Saga of Heroes")
            else:
                grandQuestNumber = pageName.split("_")[1]
                if not (pageName[9:].find("op") == -1):
                    self.setOrder(300000 + int(grandQuestNumber)*1000)
                    self.setDirectory(pageName)
                    self.setName("Grand Quest " + grandQuestNumber + ": " + grandQuestName[str(int(grandQuestNumber))]["name"] + " -- Opening Scene")
                else:
                    grandQuestSceneNumber = pageName[9:]
                    self.setOrder(300000 + int(grandQuestNumber)*1000 + int(grandQuestSceneNumber))
                    self.setDirectory(pageName)
                    self.setName("Grand Quest " + grandQuestNumber + ": " + grandQuestName[str(int(grandQuestNumber))]["name"] + " -- Scene " + pageName[9:])

        # =============
        #   TUTORIALS  
        # =============
        
        elif not (pageName.find("randall_tuto2") == -1):
            self.setOrder(600010)
            self.setDirectory(pageName)
            self.setName("Tutorial - Akras Administration Office")
        elif not (pageName.find("randall_tuto3") == -1):
            self.setOrder(600020)
            self.setDirectory(pageName)
            self.setName("Tutorial - Akras Survey Office ")
        elif not (pageName.find("randall_tuto4") == -1):
            self.setOrder(600030)
            self.setDirectory(pageName)
            self.setName("Tutorial - Summoners' Research Lab")
        elif not (pageName.find("hunter01") == -1):
            self.setOrder(600040)
            self.setDirectory(pageName)
            self.setName("Tutorial - Frontier Hunter")
        elif not (pageName.find("frontiergate_op") == -1):
            self.setOrder(600050)
            self.setDirectory(pageName)
            self.setName("Tutorial - Frontier Gate part 1")
        elif not (pageName.find("frontiergate_v2_op") == -1):
            self.setOrder(600060)
            self.setDirectory(pageName)
            self.setName("Tutorial - Frontier Gate part 2")
        elif not (pageName.find("syuurenjyo_tuto00") == -1):
            self.setOrder(600070)
            self.setDirectory(pageName)
            self.setName("Tutorial - Summoners' Training Ground")
        elif not (pageName.find("randall_library") == -1):
            self.setOrder(600074)
            self.setDirectory(pageName)
            self.setName("Tutorial - Library")
        elif not (pageName.find("randall_achievement") == -1):
            self.setOrder(600078)
            self.setDirectory(pageName)
            self.setName("Tutorial - Achievement Store")
        elif not (pageName.find("colosseum_tuto00") == -1):
            self.setOrder(600080)
            self.setDirectory(pageName)
            self.setName("Tutorial - Colosseum")
        elif not (pageName.find("guild_tut") == -1):
            if pageName == "guild_tut_01":
                self.setOrder(610003)
                self.setDirectory(pageName)
                self.setName("Tutorial - Guild Raid part 1")
            elif pageName == "guild_tut_02":
                self.setOrder(610004)
                self.setDirectory(pageName)
                self.setName("Tutorial - Guild Raid part 2")
            elif pageName == "guild_tut_03":
                self.setOrder(610005)
                self.setDirectory(pageName)
                self.setName("Tutorial - Guild Raid part 3")
        elif not (pageName.find("guild") == -1):
            if pageName == "guild_01":
                self.setOrder(610001)
                self.setDirectory(pageName)
                self.setName("Tutorial - Introduction to Guilds part 1")
            elif pageName == "guild_02":
                self.setOrder(610002)
                self.setDirectory(pageName)
                self.setName("Tutorial - Introduction to Guilds part 2")
        elif not (pageName.find("arena_tuto") == -1):
            self.setOrder(650000)
            self.setDirectory(pageName)
            self.setName("Tutorial - Arena")

        # ============
        #     RAID    
        # ============
            
        elif not (pageName.find("raid") == -1):
            if not (pageName.find("raid_op") == -1):
                self.setOrder(800000)
                self.setDirectory(pageName)
                self.setName("Raid - Opening Scene")
            elif (len(pageName.split("_")) > 3):
                if not (pageName.find("802") == -1):
                    raidNumber = pageName.split("_")[1]
                    raidSceneNumber = pageName.split("_")[2]
                    self.setOrder(800000 + int(raidNumber)*100 + int(raidSceneNumber))
                    self.setDirectory(pageName)
                    self.setName("Raid - World of Eneroth: Scene 1 and 2")
                else:
                    raidClass = pageName.split("_")[1]
                    raidScene = pageName.split("_")[2]
                    raidSceneIndicator = pageName.split("_")[3]
                    self.setOrder(800000 + int(raidClass)*100 + int(raidScene)*10 + int(raidSceneIndicator))
                    self.setDirectory(pageName)
                    if (int(raidSceneIndicator) == 1):
                        self.setName("Raid Class " + raidClass + " Scene " + raidScene + " Opening")
                    elif (int(raidSceneIndicator) == 2):
                        self.setName("Raid Class " + raidClass + " Scene " + raidScene + " Ending")
                    else:
                        self.setName("Raid Class " + raidClass + " Scene " + raidScene)
            else:
                if not (pageName.find("802") == -1):
                    raidNumber = pageName.split("_")[1]
                    raidSceneNumber = pageName.split("_")[2]
                    self.setOrder(800000 + int(raidNumber)*100 + int(raidSceneNumber))
                    self.setDirectory(pageName)
                    self.setName("Raid - World of Eneroth: Scene " + raidSceneNumber)
                elif not (pageName.find("803") == -1):
                    raidNumber = pageName.split("_")[1]
                    raidSceneNumber = pageName.split("_")[2]
                    self.setOrder(800000 + int(raidNumber)*100 + int(raidSceneNumber))
                    self.setDirectory(pageName)
                    self.setName("Raid - Baldemar wasteland: Scene " + raidSceneNumber)
                elif not (pageName.find("804") == -1):
                    raidNumber = pageName.split("_")[1]
                    raidSceneNumber = pageName.split("_")[2]
                    self.setOrder(800000 + int(raidNumber)*100 + int(raidSceneNumber))
                    self.setDirectory(pageName)
                    self.setName("Raid - Lords of Fuindor: Scene " + raidSceneNumber)
                elif not (pageName.find("805") == -1):
                    raidNumber = pageName.split("_")[1]
                    raidSceneNumber = pageName.split("_")[2]
                    self.setOrder(800000 + int(raidNumber)*100 + int(raidSceneNumber))
                    self.setDirectory(pageName)
                    self.setName("Raid - Maw of Madness: Scene " + raidSceneNumber)
                else:
                    raidClass = pageName.split("_")[1]
                    raidScene = pageName.split("_")[2]                    
                    self.setOrder(800000 + int(raidClass)*100 + int(raidScene)*10)
                    self.setDirectory(pageName)
                    self.setName("Raid Class " + raidClass + " Scene " + raidScene)

        # =============
        #     ARENA    
        # =============
        
        elif not (pageName.find("arena") == -1):
            self.setOrder(1000000 + int(pageName[5:])*10)
            self.setDirectory(pageName)
            self.setName("Arena - Rank " + arenaRankName[pageName[5:]])

        # ==============
        #     VORTEX    
        # ==============

        elif not (pageName.find("xmas2016") == -1):
            sceneNumber = pageName.split("_")[1]            
            self.setOrder(1200000 + int(sceneNumber))
            self.setDirectory(pageName)
            self.setName("2016 Christmas Special Mission Scene " + sceneNumber)

        elif not (pageName.find("Vday2017") == -1):
            sceneNumber = pageName.split("_")[1]            
            self.setOrder(1200010 + int(sceneNumber))
            self.setDirectory(pageName)
            self.setName("2017 Valentine Special Mission Scene " + sceneNumber)

        elif not (pageName.find("easter2017") == -1):
            sceneNumber = pageName.split("_")[1]            
            self.setOrder(1200020 + int(sceneNumber))
            self.setDirectory(pageName)
            self.setName("2017 Easter Special Mission Scene " + sceneNumber)

        # ==============
        #     OTHERS    
        # ==============        
        
        else:
            self.setOrder(5000000)
            self.setDirectory(pageName)
            self.setName(pageName)

    def setOrder(self, orderArg):
        self.order = orderArg

    def setDirectory(self, directoryArg):
        self.directory = directoryArg

    def setName(self, nameArg):
        self.name = nameArg

if __name__ == '__main__':
    htmlPageList = []
    story_txtDirectory = "BFStoryArchive/"

    for filename in glob.glob(story_txtDirectory + "*.html"):
        htmlPageList.append(filename)

    outputLines = []

    outputLines.append("<!DOCTYPE html>")
    outputLines.append("<html>")
    outputLines.append("<head>")
    outputLines.append("<title>Brave Frontier Story Archive</title>")
    outputLines.append("<link rel=\"stylesheet\" type=\"text/css\" href=\"BFStoryArchive/style/style.css\">")
    outputLines.append("<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">")
    outputLines.append("<meta name=\"description\" content=\"An archive of most of the story told inside the mobile RPG Brave Frontier are here.\">")
    outputLines.append("<script>")
    outputLines.append("(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){")
    outputLines.append("(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),")
    outputLines.append("m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)")
    outputLines.append("})(window,document,'script','//www.google-analytics.com/analytics.js','ga');")
    outputLines.append("")
    outputLines.append("ga('create', 'UA-74917613-1', 'auto');")
    outputLines.append("ga('send', 'pageview');")
    outputLines.append("")
    outputLines.append("</script>")
    outputLines.append("</head>")
    outputLines.append("<body>")
    outputLines.append("<div id=\"greetingsText\">If you can't find what you're looking for, try searching <a href=\"../BFJPStoryArchive/\">Japanese-only version</a> of the repository<br><br>Your name is <b>Hans</b>. You are the talented summoner from the organization called Akras Summoners' Hall, located in your homeworld of Elgaia. Your first journey brings you into Grand Gaia, a world completely different from your origin...</div>")
    outputLines.append("<ul>")

    pageList = []

    for currentHtmlPage in htmlPageList:
        pageDirectory = str(currentHtmlPage[:-5])
        pageName = pageDirectory[len(story_txtDirectory):]
        pageList.append(StoryPage(pageName))

        #outputLines.append("<li><a href=\"" + story_txtDirectory + pageDirectory[len(story_txtDirectory):] + ".html\">" + "" + "</a>"
        #print "<li><a href=\"" + story_txtDirectory + pageDirectory[len(story_txtDirectory):] + ".html\">" + pageLabel + "</a>"

    currentOrder = 0
    currentMapOrder = 0

    for currentPage in sorted(pageList, key=lambda StoryPage: StoryPage.order):
        print currentPage.order, currentMapOrder, currentPage.name
        if (currentPage.order - currentOrder < 100000):
            if (
                       (floor(currentPage.order/100000) == 0)
                    or (floor(currentPage.order/100000) == 1)
                    or (floor(currentPage.order/100000) == 2)
                    or (floor(currentPage.order/100000) == 3)
                    or (floor(currentPage.order/100000) == 4)
                    or (floor(currentPage.order/100000) == 5)
                ) and (floor(currentPage.order/1000) - floor(currentMapOrder/1000) > 0):
                
                currentMapOrder = floor(currentPage.order/1000)*1000
                outputLines.append("    <li class=\"listSeparator\">--------------------")
                outputLines.append("        <li><a href=\"" + story_txtDirectory + currentPage.directory + ".html\">" + currentPage.name + "</a>")
            else:
                outputLines.append("        <li><a href=\"" + story_txtDirectory + currentPage.directory + ".html\">" + currentPage.name + "</a>")
        else:
            currentOrder = currentPage.order
            currentMapOrder = floor(currentPage.order/1000)*1000
            outputLines.append("<li class=\"listSeparatorLarge\">====================")
            outputLines.append("        <li><a href=\"" + story_txtDirectory + currentPage.directory + ".html\">" + currentPage.name + "</a>")


    outputLines.append("</ul>")
    outputLines.append("</body>")
    outputLines.append("</html>")
    outputLines.append("")
    outputLines.append("")
    outputLines.append("")
    outputLines.append("<!-- contact me at reddit /u/blackrobe199 -->")

    fileName = "index"

    with codecs.open(fileName + ".html", 'w+', encoding='utf8') as f:
        for outputLine in outputLines:
            f.write(outputLine + "\n")

    print "Process finished"
