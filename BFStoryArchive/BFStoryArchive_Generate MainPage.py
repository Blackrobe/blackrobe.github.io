import glob, os
import codecs
from storylabels import arenaRankName

class StoryPage(object):
    def __init__(self):
        self.order = 0
        self.directory = "none"
        self.name = "(Unknown)"

    def __init__(self, pageName):
        if not (pageName.find("arena_tuto") == -1):
            self.setOrder(40000)
            self.setDirectory(pageName)
            self.setName("Tutorial - Arena")
        elif not (pageName.find("randall_tuto2") == -1):
            self.setOrder(39982)
            self.setDirectory(pageName)
            self.setName("Tutorial - Akras Administration Office")
        elif not (pageName.find("randall_tuto3") == -1):
            self.setOrder(39983)
            self.setDirectory(pageName)
            self.setName("Tutorial - Akras Survey Office ")
        elif not (pageName.find("randall_tuto4") == -1):
            self.setOrder(39984)
            self.setDirectory(pageName)
            self.setName("Tutorial - Summoners' Research Lab")
        elif not (pageName.find("hunter01") == -1):
            self.setOrder(39985)
            self.setDirectory(pageName)
            self.setName("Tutorial - Frontier Hunter")
        elif not (pageName.find("frontiergate_op") == -1):
            self.setOrder(39986)
            self.setDirectory(pageName)
            self.setName("Tutorial - Frontier Gate part 1")
        elif not (pageName.find("frontiergate_v2_op") == -1):
            self.setOrder(39987)
            self.setDirectory(pageName)
            self.setName("Tutorial - Frontier Gate part 2")
        elif not (pageName.find("syuurenjyo_tuto00") == -1):
            self.setOrder(39988)
            self.setDirectory(pageName)
            self.setName("Tutorial - Summoners' Training Ground")
        elif not (pageName.find("colosseum_tuto00") == -1):
            self.setOrder(39989)
            self.setDirectory(pageName)
            self.setName("Tutorial - Colosseum")
        elif not (pageName.find("arena") == -1):
            self.setOrder(40000 + int(pageName[5:]))
            self.setDirectory(pageName)
            self.setName("Arena - Rank " + arenaRankName[pageName[5:]])
        else:
            self.setOrder(50000)
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

    for currentPage in sorted(pageList, key=lambda StoryPage: StoryPage.order):
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
