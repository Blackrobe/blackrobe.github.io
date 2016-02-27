import glob, os
import codecs

htmlPageList = []
story_txtDirectory = "BFStoryArchive/"

for file in glob.glob(story_txtDirectory + "*.html"):
    htmlPageList.append(file)

outputLines = []

outputLines += "<html>"
outputLines += "<head>"
outputLines += "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">"
outputLines += "</head>"
outputLines += "<body>"
outputLines += "<ul>"

for currentHtmlPage in htmlPageList:
    pageDirectory = currentHtmlPage[:-5]
    outputLines += "<li><a href=\"" + pageDirectory + ".html\">" + pageDirectory + "</a>"

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