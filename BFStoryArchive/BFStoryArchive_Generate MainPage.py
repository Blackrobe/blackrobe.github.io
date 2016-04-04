import glob, os
import codecs

htmlPageList = []
story_txtDirectory = "BFStoryArchive/"

for filename in glob.glob(story_txtDirectory + "*.html"):    
    htmlPageList.append(filename)

outputLines = []

outputLines += "<html>"
outputLines += "<head>"
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

def calculatePageData(pageName):
    if not (pageName.find("arena") == -1):
        print 40000 + int(pageName[5:]), "Arena " + pageName[5:]
        return 40000 + int(pageName[5:]), "Arena " + pageName[5:]    
    else:
        return 50000, pageName

pageList = []

for currentHtmlPage in htmlPageList:    
    pageDirectory = str(currentHtmlPage[:-5])
    pageName = pageDirectory[len(story_txtDirectory):]
    pageOrder, pageLabel = calculatePageData(pageName)    
    outputLines += "<li><a href=\"" + story_txtDirectory + pageDirectory[len(story_txtDirectory):] + ".html\">" + pageLabel + "</a>"
    #print "<li><a href=\"" + story_txtDirectory + pageDirectory[len(story_txtDirectory):] + ".html\">" + pageLabel + "</a>"

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
