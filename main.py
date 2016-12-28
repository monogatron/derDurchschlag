#!/usr/bin/python3

import pdb
import sys
import os
import time
import glob

import controller
import user

print("starting derDurchschlag")


pathToConfig = os.getcwd() + "/config"          #get current directory of application and define path to config file

pathToUsers = ""
pathToInbox = ""
delay = -1
admin = ""
senderGetsHisOwnMessage = False
#pullMessageKeyword = ""
#pullMessageContent = ""
keywordArray = []                               #this is an array which will contain other arrays. each of them 
defaultAnswer = "There is no default answer"    #this answer will be sent to any non-valid pull-message request. the string will be overwritten while parsing the config-file, if a defaultAnswer is provided      
answerArray = []  
partyMode = False                               #this array will contain the answers. the the answer on the position in this array corresponds with the keyword (aka question) in the keywordArray.

Debug_lineCounter = 0

try:
    try:
        with open(pathToConfig) as config:
            lines = config.readlines()
    except:
        print("prblem while opening config-file")

    #parsing config-files
    
    for line in lines:
        Debug_lineCounter += 1
        #if Debug_lineCounter == 17:
        #    pdb.set_trace()
        
        line = line.split("#")[0]
        line=line.lstrip(" ")
        
        if line.split(" ")[0] == "inbox:":
            pathToInbox = line.split(" ")[1][:-1]
        elif line.split(" ")[0] == "users:":
            pathToUsers = line.split(" ")[1][:-1]
        elif line.split(" ")[0] == "delay:":
            #pdb.set_trace()
            #delay = int( line.split(" ")[1][:-1] )
            delay = int( line.split(" ")[1] )
        elif line.split(" ")[0] == "admin:":
            admin = line.split(" ")[1][:-1]
        elif line.split(" ")[0] == "senderGetsHisOwnMessage:":
            value = line.split(" ")[1][:-1]
            if value == "False":
                senderGetsHisOwnMessage = False
            elif value == "True":
                senderGetsHisOwnMessage = True
            else:
                print("error while reading 'senderGetsHisOwnMessage'-value from config file")
                exit(1)
        #elif line.split(" ")[0] == "PullMessageKeyword":
        #    pullMessageKeyword = line.split(" ")[1][:-1]
        #elif line.split(" ")[0] == "PullMessageContent":
        #    #pdb.set_trace()
        #    pullMessageContent = line.split(" ", 1)[1][:-1]
        #    print("pullMessageContent: " + str(pullMessageContent))
        elif "keyword" in line:
            #pdb.set_trace()
            positionOfKeyword = int( ( line.split(" ")[0][:-1] ).split("keyword")[1] )
            #print("positionOfKeyword: " + str(positionOfKeyword))
            if len(keywordArray) != positionOfKeyword:
                print("something went wrong. maybe the order of keywords in config file is not right. it must be right numerical order starting with keyword0")
                exit(1)
            else:   #is in right order
                keywordArray.append( ( line.lower() ).split(" ")[1:] )
                for index in range(0, len(keywordArray[positionOfKeyword])):
                    #pdb.set_trace()
                    keywordArray[positionOfKeyword][index] = keywordArray[positionOfKeyword][index].replace("\n", "") #removes the \n at the end of the last keyword in each line of config-file
                #pdb.set_trace()
        elif "answer" in line:
            positionOfAnswer = int( ( line.split(" ")[0][:-1] ).split("answer")[1] )
            if len(answerArray) != positionOfAnswer:
                print("something went wrong. maybe the order of answers in config file is not right. it must be right numerical order starting with answer0")
                exit(1)
            else:
                answerArray.append( line.split(" ")[1].replace("\n", "") )
        elif line.split(" ")[0][:-1] == "partyMode":
            if line.split(" ")[1] == "True":
                partyMode = True
            elif line.split(" ")[1] == "False":
                partyMode = False
            else:
                print("something went wrong parsing 'partyMode'-parameter in config-file") 
        elif line.split(" ")[0][:-1] == "defaultAnswer":
            defaultAnswer = line.split(" ")[1].replace("\n", "")
        else:
            if len(line) != 0:
                #pdb.set_trace()
                if line[0] != "#" and line != "\n":
                    #pdb.set_trace()
                    print("something went wrong parsing config file. line: " + str(line))
                    exit(1)
                else:
                    pass
                    #print("comment found: " + str(line))
            else:
                pass
    #pdb.set_trace()
    pass

    if len(keywordArray) != len(answerArray):
        print("something wrent wrong. len(keywordArray) not len(answerArray)")
        exit(1)
                
except Exception as e:
    print("problem while parsing config-file. Exception:")
    print("stoped at config-file, line: " + str(Debug_lineCounter))
    print(e)
    exit(1)





#try:
controller = controller.Controller(pathToUsers, pathToInbox, delay, senderGetsHisOwnMessage, keywordArray, answerArray, defaultAnswer, partyMode)
#except KeyboardInterrupt as e:
#    print("\nshutdown by user")
#    print(e)
#except Exception as e:
#    print("\nentering except: ")
#    #pdb.set_trace()
#    text = "derDurchschlag is shutting down. bad coding?"
#    toSendString =  "echo '" + text + "' | gammu-smsd-inject TEXT " + admin
#    os.system( toSendString )
#    print("sending SMS to " + admin + " (admin): " + str( toSendString ) )
#    print(e)

exit(1)

