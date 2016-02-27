# coding: utf-8

navi_chara_collectionDirectory = "navi_chara_collection/"

story_txtDirectory = "BFStoryArchive/"
currentTxtList = []
currentTxt = ""
playerName = "Hans"

speakerFacePortraitStack = []
speakerName = ""

fadeOut = False

alias = {}

speakerFacePortraitStack.append("blank.png")

import glob, os
import codecs

for file in glob.glob(story_txtDirectory + "*.txt"):
    currentTxtList.append(file)

for currentTxt in currentTxtList:

    outputLines = []

    
    outputLines += "<html>"
    outputLines += "<head>"
    outputLines += "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">"
    outputLines += "</head>"
    outputLines += "<body>"
    
    with codecs.open(currentTxt,'r',encoding='utf8') as f:

        line = f.readline()

        while line:                        

            # Searching for aliases
            if not (line.find("type=PARAM,id=1,") == -1):
                aliasBegin = line.find("param=") + 6
                aliasEnd = definitionBegin = line.find(":")
                definitionEnd = line.find(",#")
                alias[line[aliasBegin:aliasEnd]] = line[definitionBegin+1:definitionEnd]

            # Begin extracting

            if not (line.find("type=PARAM,id=2,") == -1):
                aliasBegin = line.find("param=") + 6
                aliasEnd = line.find(":")
                if not (alias[line[aliasBegin:aliasEnd]].find("navi_chara") == -1):
                    speakerFacePortraitStack.append(alias[line[aliasBegin:aliasEnd]])

                line = f.readline()
                if not (line.find("type=PARAM,id=2,") == -1):
                    aliasBegin = line.find("param=") + 6
                    aliasEnd = line.find(":")
                    if not (alias[line[aliasBegin:aliasEnd]].find("navi_chara") == -1):
                        speakerFacePortraitStack.append(alias[line[aliasBegin:aliasEnd]])

            if not (line.find("type=PARAM,id=3,") == -1):
                aliasBegin = line.find("param=") + 6
                aliasEnd = line.find(":")
                if not (alias[line[aliasBegin:aliasEnd]].find("navi_chara") == -1):
                    speakerFacePortraitStack.pop()
                    if speakerFacePortraitStack == []:
                        speakerFacePortraitStack.append("blank.png")
                    

            #if not (line.find("type=PARAM,id=36,") == -1) or not (line.find("type=PARAM,id=40,") == -1):
            #    speakerFacePortrait = "blank.png"
            #    fadeOut = True

            #if fadeOut and not (line.find("type=STOP,") == -1):
            #    fadeOut = False

            if not (line.find("type=PARAM,id=15,") == -1):
                messageBegin = line.find("msg=") + 4
                messageEnd = line.find(",#*,type=MSGWAIT")

                message = line[messageBegin:messageEnd]

                message = message.replace("<rep_handlename>", playerName)
                message = message.replace("<br>", "")

                while (message.find("<wait=") != -1):
                    tempMessage = message[:message.find("<wait=")] + message[message.find("<wait=")+message[message.find("<wait="):].find(">")+1:]
                    message = tempMessage

                while (message.find("<size=") != -1):
                    tempMessage = message[:message.find("<size=")] + message[message.find("<size=")+message[message.find("<size="):].find(">")+1:]
                    message = tempMessage

                #print len(speakerFacePortraitStack), "<div class=\"facePortrait\"> <img src=\"" + navi_chara_collectionDirectory + speakerFacePortraitStack[len(speakerFacePortraitStack)-1] + "\" style=\"width:125px;height:125px;\"></div><div class=\"speakerName\">", speakerName, "</div><div class=\"speakerMessage\">", message, "</div><br>"
                
                outputLines += "<div class=\"facePortrait\"> <img src=\"" + navi_chara_collectionDirectory + speakerFacePortraitStack[len(speakerFacePortraitStack)-1] + "\" style=\"width:125px;height:125px;\"></div><div class=\"speakerName\">", speakerName, "</div><div class=\"speakerMessage\">", message, "</div><br>"

            if not (line.find("type=PARAM,id=39,") == -1):
                nameBegin = line.find("param=") + 6
                nameEnd = line.find(",#")
                speakerName = line[nameBegin:nameEnd]

            line = f.readline()

    outputLines += "</body>"
    outputLines += "</html>"
    outputLines += ""
    outputLines += ""
    outputLines += ""
    outputLines += "<!-- contact me at reddit /u/blackrobe199 -->"

    fileName = f.name[:-4]

    with codecs.open(fileName + ".html", 'w+', encoding='utf8') as f:    
        for outputLine in outputLines:
            f.write(outputLine)
            
