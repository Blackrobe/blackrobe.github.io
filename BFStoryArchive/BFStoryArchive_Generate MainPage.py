import glob, os
import codecs
from math import floor
from storylabels import arenaRankName, mapName

class StoryPage(object):
    def __init__(self):
        self.order = 0
        self.directory = "none"
        self.name = "(Unknown)"

    def __init__(self, pageName):
        if not (pageName[:3].find("map") == -1):
            print "we found map"
            mapNumber = pageName.split("-")[0][3:]
            if (str(mapNumber) in [str(i) for i in range(0, 99)]):
                if not (pageName.find("dungeon_ex") == -1):
                    self.setOrder(int(mapNumber)*1000+990)
                    self.setDirectory(pageName)
                    self.setName("Chapter " + mapNumber + " Special: " + mapName[mapNumber]["name"] + " " + pageName.split("-")[1])
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
                        print "this one"
                        dungeonNumber = pageName.split("-")[1][7:]
                        sceneNumber = pageName.split("-")[2]
                        self.setOrder(int(mapNumber)*1000+int(dungeonNumber)*10+int(sceneNumber))
                        self.setDirectory(pageName)
                        self.setName("Chapter " + mapNumber + "-" + dungeonNumber + ": " + mapName[mapNumber]["name"] + " - " + mapName[mapNumber]["dungeon"][dungeonNumber] + " Scene " + sceneNumber)
                    # ===============
                    # Single scene
                    # ===============
                    else:
                        print "That one", pageName
                        dungeonNumber = pageName.split("-")[1][7:]
                        self.setOrder(int(mapNumber)*1000+int(dungeonNumber)*10)
                        self.setDirectory(pageName)
                        self.setName("Chapter " + mapNumber + "-" + dungeonNumber + ": " + mapName[mapNumber]["name"] + " - " + mapName[mapNumber]["dungeon"][dungeonNumber])
            else:
                self.setOrder(100000)
                self.setDirectory(pageName)
                self.setName(pageName)
        elif not (pageName.find("randall_tuto2") == -1):
            self.setOrder(399820)
            self.setDirectory(pageName)
            self.setName("Tutorial - Akras Administration Office")
        elif not (pageName.find("randall_tuto3") == -1):
            self.setOrder(399830)
            self.setDirectory(pageName)
            self.setName("Tutorial - Akras Survey Office ")
        elif not (pageName.find("randall_tuto4") == -1):
            self.setOrder(399840)
            self.setDirectory(pageName)
            self.setName("Tutorial - Summoners' Research Lab")
        elif not (pageName.find("hunter01") == -1):
            self.setOrder(399850)
            self.setDirectory(pageName)
            self.setName("Tutorial - Frontier Hunter")
        elif not (pageName.find("frontiergate_op") == -1):
            self.setOrder(399860)
            self.setDirectory(pageName)
            self.setName("Tutorial - Frontier Gate part 1")
        elif not (pageName.find("frontiergate_v2_op") == -1):
            self.setOrder(399870)
            self.setDirectory(pageName)
            self.setName("Tutorial - Frontier Gate part 2")
        elif not (pageName.find("syuurenjyo_tuto00") == -1):
            self.setOrder(399880)
            self.setDirectory(pageName)
            self.setName("Tutorial - Summoners' Training Ground")
        elif not (pageName.find("colosseum_tuto00") == -1):
            self.setOrder(399890)
            self.setDirectory(pageName)
            self.setName("Tutorial - Colosseum")
        elif not (pageName.find("arena_tuto") == -1):
            self.setOrder(399895)
            self.setDirectory(pageName)
            self.setName("Tutorial - Arena")
        elif not (pageName.find("arena") == -1):
            self.setOrder(400000 + int(pageName[5:])*10)
            self.setDirectory(pageName)
            self.setName("Arena - Rank " + arenaRankName[pageName[5:]])
        else:
            self.setOrder(500000)
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

    outputLines += "<html>"
    outputLines += "<head>"
    outputLines += "<title>Brave Frontier Story Archive</title>"
    outputLines += "<link rel=\"stylesheet\" type=\"text/css\" href=\"BFStoryArchive/style/style.css\">"
    outputLines += "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">"
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
    outputLines += "</head>"
    outputLines += "<body>"
    outputLines += "<div id=\"greetingsText\">Your name is <b>Hans</b>. You are the talented summoner from the organization called Akras Summoners' Hall, located in your homeworld of Elgaia. Your first journey brings you into Grand Gaia, a world completely different from your origin...</div>"
    outputLines += "<ul>"

    pageList = []

    for currentHtmlPage in htmlPageList:
        pageDirectory = str(currentHtmlPage[:-5])
        pageName = pageDirectory[len(story_txtDirectory):]
        pageList.append(StoryPage(pageName))

        #outputLines += "<li><a href=\"" + story_txtDirectory + pageDirectory[len(story_txtDirectory):] + ".html\">" + "" + "</a>"
        #print "<li><a href=\"" + story_txtDirectory + pageDirectory[len(story_txtDirectory):] + ".html\">" + pageLabel + "</a>"

    currentOrder = 0
    currentMapOrder = 0

    for currentPage in sorted(pageList, key=lambda StoryPage: StoryPage.order):
        print currentPage.order, currentMapOrder, currentPage.name
        if (currentPage.order - currentOrder < 100000):
            if (currentPage.order < 100000) and (floor(currentPage.order/1000) - floor(currentMapOrder/1000) > 0):
                print "Above!"
                currentMapOrder = floor(currentPage.order/1000)*1000
                outputLines += "<li>--------------------"
                outputLines += "<li><a href=\"" + story_txtDirectory + currentPage.directory + ".html\">" + currentPage.name + "</a>"
            else:
                outputLines += "<li><a href=\"" + story_txtDirectory + currentPage.directory + ".html\">" + currentPage.name + "</a>"
        else:
            currentOrder = currentPage.order
            outputLines += "<li>===================="
            outputLines += "<li><a href=\"" + story_txtDirectory + currentPage.directory + ".html\">" + currentPage.name + "</a>"


    outputLines += "</ul>"
    outputLines += "</body>"
    outputLines += "</html>"
    outputLines += ""
    outputLines += ""
    outputLines += ""
    outputLines += "<!-- contact me at reddit /u/blackrobe199 -->"

    fileName = "index"

    with codecs.open(fileName + ".html", 'w+', encoding='utf8') as f:
        for outputLine in outputLines:
            f.write(outputLine)

    print "Process finished"
