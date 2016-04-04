# coding: utf-8

navi_chara_collectionDirectory = "navi_chara_collection/"
dungeon_battle_collectionDirectory = "dungeon_battle_collection/"
story_txtDirectory = "BFStoryArchive/"
currentTxtList = []
currentTxt = ""
playerName = "Hans"

ignoredPortraitList = [
    "navi_chara29",
    "navi_chara53",
    "navi_chara56",
    "navi_chara57",
    "navi_chara58",
    "navi_chara59",
    "navi_chara60",
    "navi_chara61",
    "navi_chara62",
    "navi_chara63",
    "navi_chara71",
    "navi_chara73",
    "navi_chara116",
    "navi_chara117",    
    ]

print "begin"
    
import glob, os
import codecs

for file in glob.glob(story_txtDirectory + "*.txt"):
    currentTxtList.append(file)

#currentTxtList = [story_txtDirectory + "raid_803_1.txt"]

for currentTxt in currentTxtList:

    print currentTxt

    outputLines = []

    outputLines.append("<!DOCTYPE html>")
    outputLines.append("")
    outputLines.append("<html>")
    outputLines.append("<head>")
    outputLines.append("<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">")
    outputLines.append("<link rel=\"stylesheet\" type=\"text/css\" href=\"style/style.css\">")
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
    
    with codecs.open(currentTxt,'r',encoding='utf8') as f:

        alias = {}
        speakerFacePortraitStack = []
        speakerFacePortraitStack.append("blank.png")
        speakerName = ""

        line = f.readline()

        while line:                        

            # Searching for aliases
            if not (line.find("type=PARAM,id=1,") == -1):
                aliasBegin = line.find("param=") + 6
                aliasEnd = definitionBegin = line.find(":")
                definitionEnd = line.find(",#")
                alias[line[aliasBegin:aliasEnd]] = line[definitionBegin+1:definitionEnd]

            # Begin extracting

            # ID = 2: add (push) portrait to stack / add background image
            if not (line.find("type=PARAM,id=2,") == -1):
                aliasBegin = line.find("param=") + 6
                aliasEnd = line.find(":")                                
                
                # Character portrait
                if not (alias[line[aliasBegin:aliasEnd]].find("navi_chara") == -1) and not (line[aliasBegin:aliasEnd] in ignoredPortraitList):
                    speakerFacePortraitStack.append(alias[line[aliasBegin:aliasEnd]])
                
                # Background image
                if not (alias[line[aliasBegin:aliasEnd]].find("dungeon") == -1):
                    outputLines.append("")                    
                    outputLines.append("<div class=\"dungeonBackgroundContainer\">")
                    outputLines.append("<img class=\"dungeonFrame\" src=\""+dungeon_battle_collectionDirectory+"baseDungeonFrame.png\" />")
                    outputLines.append("<img class=\"dungeonImage\" src=\""+dungeon_battle_collectionDirectory+alias[line[aliasBegin:aliasEnd]]+"\" />")
                    outputLines.append("</div>")
                    outputLines.append("")                

            # ID = 3: remove (pop) portrait from stack
            if not (line.find("type=PARAM,id=3,") == -1):
                aliasBegin = line.find("param=") + 6
                aliasEnd = line.find(":")
                if not (alias[line[aliasBegin:aliasEnd]].find("navi_chara") == -1) and not (line[aliasBegin:aliasEnd] in ignoredPortraitList):
                    speakerFacePortraitStack.pop()
                    if speakerFacePortraitStack == []:
                        speakerFacePortraitStack.append("blank.png")

            # ID = 5: mark a line of dialogue text information
            if not (line.find("type=PARAM,id=15,") == -1):
                messageBegin = line.find("msg=") + 4
                messageEnd = line.find(",#*,type=MSGWAIT")

                message = line[messageBegin:messageEnd]

                message = message.replace("<rep_handlename>", playerName)
                message = message.replace("<br>", " ")

                while (message.find("<wait=") != -1):
                    tempMessage = message[:message.find("<wait=")] + message[message.find("<wait=")+message[message.find("<wait="):].find(">")+1:]
                    tempMessage = tempMessage.replace("</wait>", "")
                    message = tempMessage

                while (message.find("<size=") != -1):                    
                    tagPosition = message.find("<size=")
                    if (tempMessage.find("</size>") != -1):
                        tempMessage = message[:tagPosition] + "<div style=\"display:inline;font-size:" + message[tagPosition+6:tagPosition+6+message[tagPosition+6:].find(">")] +"px\">" + message[tagPosition + message[tagPosition:].find(">")+1 :]
                        tempMessage = tempMessage.replace("</size>", "</div>")
                    else:
                        tempMessage = message[:tagPosition] + "<div style=\"display:inline;font-size:" + message[tagPosition+6:tagPosition+6+message[tagPosition+6:].find(">")] +"px\">" + message[tagPosition + message[tagPosition:].find(">")+1 :] + "</div>"
                    message = tempMessage

                while (message.find("<anchor=") != -1):
                    tempMessage = message[:message.find("<anchor=")] + message[message.find("<anchor=")+message[message.find("<anchor="):].find(">")+1:]
                    tempMessage = tempMessage.replace("</anchor>", "")
                    message = tempMessage

                while (message.find("<speed=") != -1):
                    tempMessage = message[:message.find("<speed=")] + message[message.find("<speed=")+message[message.find("<speed="):].find(">")+1:]
                    tempMessage = tempMessage.replace("</speed>", "")
                    message = tempMessage

                #print len(speakerFacePortraitStack), "<div class=\"facePortrait\"> <img src=\"" + navi_chara_collectionDirectory + speakerFacePortraitStack[len(speakerFacePortraitStack)-1] + "\" style=\"width:125px;height:125px;\"></div><div class=\"speakerName\">", speakerName, "</div><div class=\"speakerMessage\">", message, "</div><br>"
                
                outputLines.append("")
                outputLines.append("<div class=\"dialogueContainer\">")
                outputLines.append("<div class=\"facePortrait\">")
                outputLines.append("<img class=\"facePortraitFrame\" src=\"navi_chara_collection/characterFrame.png\" />")
                outputLines.append("<img class=\"facePortraitImg\" src=\"" + navi_chara_collectionDirectory + speakerFacePortraitStack[len(speakerFacePortraitStack)-1] + "\" />")                
                outputLines.append("</div>")
                outputLines.append("<div class=\"speakerName\">" + speakerName + "</div>")
                outputLines.append("<div class=\"speakerMessage\">" + message + "</div>")
                outputLines.append("</div>")
                outputLines.append("<br>")                
                outputLines.append("")

            # ID = 16: mark a line of NPC deity dialogue session
            if not (line.find("type=PARAM,id=16,") == -1):
                messageBegin = line.find("msg=") + 4
                messageEnd = len(line[:messageBegin]) + line[messageBegin:].find(",#")                

                message = line[messageBegin:messageEnd]

                message = message.replace("<rep_handlename>", playerName)
                message = message.replace("<br>", "")

                while (message.find("<wait=") != -1):
                    tempMessage = message[:message.find("<wait=")] + message[message.find("<wait=")+message[message.find("<wait="):].find(">")+1:]
                    message = tempMessage

                while (message.find("<size=") != -1):
                    tempMessage = message[:message.find("<size=")] + message[message.find("<size=")+message[message.find("<size="):].find(">")+1:]
                    message = tempMessage

                while (message.find("<anchor=") != -1):
                    tempMessage = message[:message.find("<anchor=")] + message[message.find("<anchor=")+message[message.find("<anchor="):].find(">")+1:]
                    message = tempMessage

                while (message.find("<speed=") != -1):
                    tempMessage = message[:message.find("<speed=")] + message[message.find("<speed=")+message[message.find("<speed="):].find(">")+1:]
                    message = tempMessage

                outputLines.append("")
                outputLines.append("<div class=\"deityMessage\">" + message + "</div>")                
                outputLines.append("<br>")
                outputLines.append("<br>")
                outputLines.append("")

            # ID = 39: mark a line of dialogue NPC name information
            if not (line.find("type=PARAM,id=39,") == -1):
                nameBegin = line.find("param=") + 6
                nameEnd = line.find(",#")
                speakerName = line[nameBegin:nameEnd]

            # ID = 40: reset NPC name information
            if not (line.find("type=PARAM,id=40,") == -1):
                speakerName = "   "

            # ID = 45: mark a dialogue long wait session (with fading in and out)
            if not (line.find("type=PARAM,id=45,") == -1):
                outputLines.append("")
                outputLines.append("<div class=\"dialogueSeparator\" >")
                outputLines.append("<img src=\"navi_chara_collection/dialogueSeparator.png\" align=\"middle\" />")
                outputLines.append("</div>")
                outputLines.append("")
            
            # ID = 46: mark a line of NPC deity portrait
            if not (line.find("type=PARAM,id=46,") == -1):
                outputLines.append("")
                outputLines.append("<div class=\"deityDialogueContainer\">")
                outputLines.append("<div class=\"deityPortrait\">")
                outputLines.append("<img class=\"deityPortraitFrame\" src=\"navi_chara_collection/deityFrame.png\" />")
                outputLines.append("<img class=\"deityPortraitImgBack\" src=\"navi_chara_collection/blank.png\" />")
                outputLines.append("<img class=\"deityPortraitImg\" src=\"navi_chara_collection/deity.gif\" />")
                outputLines.append("</div>")                
                outputLines.append("</div>")              
                outputLines.append("")
            
            line = f.readline()

    outputLines.append("</body>")
    outputLines.append("</html>")
    outputLines.append("")
    outputLines.append("")
    outputLines.append("")
    outputLines.append("<!-- contact me at reddit /u/blackrobe199 -->")

    fileName = f.name[:-4]

    with codecs.open(fileName + ".html", 'w+', encoding='utf8') as f:    
        for outputLine in outputLines:
            f.write(outputLine + "\n")
            
