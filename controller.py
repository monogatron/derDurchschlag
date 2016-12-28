
import os
import sys
import time
import pdb
import glob
from datetime import datetime, timedelta
from dateutil import parser

import message
import user

class Controller:
    
    

    def __init__(self, in_pathToUsers, in_pathToInbox, in_delay, in_senderGetsHisOwnMessage, in_pullmessageKeywordArray, in_pullmessageAnswerArray, in_pullmessageDefaultAnswer, in_partyMode):
        self.pathToUsers = ""
        self.pathToInbox = ""
        self.delay = -1
        self.senderGetsHisOwnMessage = in_senderGetsHisOwnMessage
        self.partialReplacementOfSpecialCharacters = True
        self.pullmessageKeywordArray = in_pullmessageKeywordArray
        self.pullmessageAnswerArray = in_pullmessageAnswerArray
        self.pullmessageDefaultAnswer = in_pullmessageDefaultAnswer
        self.partyMode = in_partyMode

        if in_pathToInbox[-1:] != "/":
            in_pathToInbox = in_pathToInbox + "/"
        if in_pathToUsers[-1:] != "/":
            in_pathToUsers = in_pathToUsers + "/"
        self.pathToUsers = in_pathToUsers
        self.pathToInbox = in_pathToInbox
        self.delay = in_delay
        print("inbox path: " + self.pathToInbox)
        print("user path: " + self.pathToUsers)
        while 42 == 42:         #check for new messages:
            time.sleep( int(self.delay) )
            #print("checking")
            completePath = self.pathToInbox[:-1] + "/*.txt"
            pathesToIncommingMessages = False
            pathesToIncommingMessages = glob.glob( completePath )
            ArrayWithMessages = []
            if len(pathesToIncommingMessages) >= 1:
                ArrayWithMessages = self.getArrayWithMessages( pathesToIncommingMessages )  #is is very likely that messages, that are longer then the standard-sms-size will be split into multiple "small" messages. this function merges them back together to a single one
            for incommingMessage in ArrayWithMessages:
                print( "\n\nreceived a message: " + str(incommingMessage.path) )
                print( "content: " + str(incommingMessage.content) )
                numberOfSender = incommingMessage.fromNumber
                #pdb.set_trace()
                pass
                if incommingMessage.isPullMessageRequest == False:
                    self.interpretMessage( incommingMessage )
                else:
                    print( "got pullMessageRequest from number: " + str(incommingMessage.fromNumber) + str(" ; answerIndex: ") + str(incommingMessage.answerIndex) )
                    self.handlePullMessageRequest( incommingMessage )
                




    def getArrayWithMessages(self, in_pathesToIncommingMessages):
        # first we need to check if there are multiple-messages at all. 
        # a multiple-message can be recognized by the file-name. a single-message 
        # has the format: IN20160514_110957_00_+49123456798_00.txt
        # where             ^ this is the date
        #                            ^ this is the time of receive.
        #          i do not know what this ^ is
        #                              but this ^ is the sender's number
        #                                          and this ^ is a counter, which indicates the 'position' in a multi-message.
        # so, first we check for this numbers.
        arrayWithMessages = []
        answerIndex = -1
        for singlePath in in_pathesToIncommingMessages:
            fileName = singlePath.split("/").pop()  #file name of the message
            fileName = fileName.split(".")[0]       #without the '.'-extention
            splitted = fileName.split("_")          # zeroes element contains date, first the time, second i dont know, third the number of sender, fourth the position in a multi-message
            date = False
            time = False
            fromNumber = False
            positionInMultiMessage = False
            try:
                date = splitted[0][2:]              #date without the 'IN'
                time = splitted[1]
                fromNumber = splitted[3]
                positionInMultiMessage = int( splitted[4] )
            except:
                print("unknown filename-format")    #something went wrong
                self.shutdown()
            
            #that^ was the header,
            #now comes the content:
            
            
            
            
            textFile = open(singlePath, 'rb')               # i need to open it as a byte-object to decode it as utf-8 and replace non-valid characters with the '?'-symbol. i learned that at the 33c3
            text = textFile.read()
            text = text.decode("utf-8", errors="replace")   
            
            
            
            
            text = text.lower()                                     #everything to lower case. it could cause problems, when channel names are not spelled correctly (upper/lower-case)
            
            if self.partialReplacementOfSpecialCharacters == True:
                text = text.replace("ä", "ae")                      #gammu has problems to send utf-8 characters. i was not able to fix that. so i just replace the characters with ascii-conform ones
                text = text.replace("ö", "oe")
                text = text.replace("ü", "ue")
                text = text.replace("ß", "ss")
                text = text.replace('"', "'")
            if text[-1:] == "\n":
                text = text[:-1]            #removing "/n" if there (happens at debugging)
            print("text: " + text)
            isPullMessageRequest = False
            #answerIndex = -1
            #pdb.set_trace()
            for index in range(0, len(self.pullmessageKeywordArray)):
                if text in self.pullmessageKeywordArray[index]:
                    answerIndex = index
                    isPullMessageRequest = True
            #if text == self.pullMessageKeyword:
                #isPullMessageRequest = True                
            arrayWithMessages.append( message.Message( singlePath, date, time, fromNumber, positionInMultiMessage, text, isPullMessageRequest, answerIndex) )
            
            print("removing file: " + singlePath)
            os.remove(singlePath) #removing the incomming message
        #so now we have an array with message-objects. but the multi-messages are still separated
        sorted_arrayWithMessages = sorted( arrayWithMessages, key = lambda x: x.positionInMultiMessage, reverse = True )
        #the 0th element in this array should now have the highest positionInMultiMessage
        
        
        
        while sorted_arrayWithMessages[0].positionInMultiMessage != 0: #is there a multi-message at all??
            #print("entering while-loop")
            #ok, we have a multi message. now we need to merge that message.
            #first we make an extra array with messages from the sender
            arrayWithMessagesFromSender = []
            numberOfSenderOfMultiMessage = sorted_arrayWithMessages[0].fromNumber
            indexesOfMessagesIn_sorted_arrayWithMessages_whichMustBeDeleted = []
            #pdb.set_trace()
            index = 0
            for messageInArray in sorted_arrayWithMessages:
                if messageInArray.fromNumber == numberOfSenderOfMultiMessage:
                    arrayWithMessagesFromSender.append(messageInArray)
                    indexesOfMessagesIn_sorted_arrayWithMessages_whichMustBeDeleted.append(index)
                index += 1
            for indexToDelete in reversed(indexesOfMessagesIn_sorted_arrayWithMessages_whichMustBeDeleted):#need to reverse the order of to-delete-indexes because otherwise the indexes wouldn't be correct any more...
                sorted_arrayWithMessages.pop(indexToDelete)
            sorted_arrayWithMessagesFromSender = sorted( arrayWithMessagesFromSender, key = lambda x: x.positionInMultiMessage, reverse = False )
            # now we have an array with messages from a sender who sent a multi-message. the order is the lowest number of "positionInMultiMessage" in the beginning
            mergedContent = ""
            for messageInArray in sorted_arrayWithMessagesFromSender:
                mergedContent += messageInArray.content
            newMergedMessage = message.Message( sorted_arrayWithMessagesFromSender[0].path, sorted_arrayWithMessagesFromSender[0].date, sorted_arrayWithMessagesFromSender[0].time, sorted_arrayWithMessagesFromSender[0].fromNumber, 0, mergedContent, isPullMessageRequest, answerIndex )
            sorted_arrayWithMessages.append(newMergedMessage)
            sorted_arrayWithMessages = sorted( sorted_arrayWithMessages, key = lambda x: x.positionInMultiMessage, reverse = True )
        return sorted_arrayWithMessages
        
        
        

    def getAllUsers(self):
        pathesToUsers = glob.glob(self.pathToUsers + "*")   #puts all pathes to all user-files into an array
        output = []
        for path in pathesToUsers:
            otherUser = user.User(path) #creates an user-object out of the path
            output.append(otherUser)
        return output       #returns the array with user-objects


    def interpretMessage(self, in_incommingMessage):
        
        #catch special cases:
        if in_incommingMessage.content == "mute":
            in_incommingMessage.content = "@mute"       #because most people probalby won't accept the "@", i'm doing an exeption here. "mute" without an "@" is enough to mute, and will be handlet the same as "@mute"
        elif in_incommingMessage.content == "ping":
            in_incommingMessage.content = "@ping"    
        elif in_incommingMessage.content == "":           #handle empty messages to avoid spam
            print("that was an empty message from: " + in_incommingMessage.fromNumber )
            return False
        elif in_incommingMessage.content == "unmute":
            in_incommingMessage.content = "@unmute"

        if in_incommingMessage.content[0] == "@":
            #print("it is a command")
            self.interpretCommand( in_incommingMessage )
        
        #if the message doesn't beginn with an "@", 
        #then we just want to send the message to the channel, the user is in.
        #if the user is in more then one channel, this doesn't work and 
        #the user needs to get an sms about that fact
        
        else:
            
            #no pullMessage-request...
            #need to check, if the user is existing in database:
            sender = False
            allUsers = self.getAllUsers()       #getAllUser() returns a array with user-objects
            for user in allUsers:
                if in_incommingMessage.fromNumber == user.getNumber():
                    sender = user
            if sender != False:
                channelsSenderIsIn = sender.getChannels()
                if len(channelsSenderIsIn) == 1:                    # user is in one channel or in no channel
                    if channelsSenderIsIn[0] == "":                 #user is in no channel
                        sender.sendSMS( "", "derDurchschlag", "you are in no channel. please send '@join.channelName' to join a channel")
                    else:                                           #user is only in one channel
                        for user in allUsers:
                            channelsOtherUserIsIn = user.getChannels()
                            if channelsSenderIsIn[0] in channelsOtherUserIsIn:
                                if ( user.getNumber() != in_incommingMessage.fromNumber ) or self.senderGetsHisOwnMessage:        #sender doesn't need to get his own message
                                    time.sleep(2)   #it sometimes happend, that users get the same message twice, but this program only sent it once. trying if it is any better with this delay.
                                    user.sendSMS( channelsSenderIsIn[0], sender.getNick(), in_incommingMessage.content )
                if len( channelsSenderIsIn ) > 1:
                    sender.sendSMS( "", "derDurchschlag", "you are in more then one channel. you must specify the channel, you want to send your message to. do that by add '@channelName' to the beginning of your message")
            else:
                print("received a message but doesn't begin with an '@' and is not in database")
                if self.partyMode:
                    self.sendDefaultMessageTo(in_incommingMessage.fromNumber)
                    
    


    def interpretCommand(self, in_incommingMessage ):
        commandBlock = in_incommingMessage.content.split(" ")[0]
        noMessageContent = False
        potentialText = ""
        try:
            potentialText = in_incommingMessage.content.split(" ", 1)[1]
        except IndexError:
            noMessageContent = True
        blocks = commandBlock.split(".")
        blocks[0] = blocks[0][1:]       #remove the "@" from first block
        pathToAllExistingUsers = glob.glob(self.pathToUsers + "*")          #get pathes to all existing users
        NumbersOfAllExistingUsers = []
        senderIsAlreadyAUser = False
        for path in pathToAllExistingUsers:
            NumbersOfAllExistingUsers.append( path.split("/")[-1] )
        if in_incommingMessage.fromNumber in NumbersOfAllExistingUsers:
            senderIsAlreadyAUser = True

        try:
            if len(blocks) == 4:
                if ( blocks[0] == "hello" or blocks[0] == "hallo" ):
                    if senderIsAlreadyAUser == False:
                        if blocks[2] == "join":  #for example: @hallo.myNickname.join.SomeChannelName
                            nick = blocks[1]
                            channel = []
                            channel.append(blocks[3])
                            self.writeNewUserFile( in_incommingMessage.fromNumber, nick, channel )
                            temp_path = self.pathToUsers + in_incommingMessage.fromNumber
                            sender = user.User( temp_path )
                            sender.sendSMS( "", "derDurchschlag", "you have been added to channel: '" + channel[0] + "'")
                        else:
                            print("wrong syntax")
                            toSendString =  "echo 'it seems you used a wrong syntax. write: @join.channelName' | gammu-smsd-inject TEXT " + in_number 
                            os.system( toSendString )
                    else:                       # senderIsAlreadyAUser == True
                        #user is already an existing user
                        sender = user.User( self.pathToUsers + in_incommingMessage.fromNumber )
                        sender.sendSMS( "", "derDurchschlag", "you are already an existing user. if you want to join a channel, just send '@join.channelName'")
                else:
                    print("unknown command")
                    toSendString =  "echo 'unknown command. if you want to register, send: @hello.yourNickname.join.SomeChannel or @hello.yourNickname and join a channel later' | gammu-smsd-inject TEXT " + in_number 
                    os.system( toSendString )


            if len(blocks) == 2:
                if ( blocks[0] == "hello" or blocks[0] == "hallo" ):    #for example: @hello.myNickname
                    if senderIsAlreadyAUser == False:                        
                        nick = blocks[1]
                        channels = []
                        channels.append("")             #adding no channel, because user has not joined yet
                        self.writeNewUserFile( in_incommingMessage.fromNumber, nick, channels )
                    else:                       # senderIsAlreadyAUser == True
                        #user is already an existing user
                        sender = user.User( self.pathToUsers + in_incommingMessage.fromNumber )
                        sender.sendSMS( "", "derDurchschlag", "you are already an existing user. if you want to join a channel, just send '@join.channelName'")

                elif blocks[0] == "exit" or blocks[1] == "exit":        #for example @exit.myChannel or @myChannel.exit
                    if senderIsAlreadyAUser:
                        channelToLeave = ""
                        if blocks[0] == "exit":
                            channelToLeave = blocks[1]
                        elif blocks[1] == "exit":
                            channelToLeave = blocks[0]
                        else:
                            print("something went wrong")
                            exit(0)
                        temp_path = self.pathToUsers + in_incommingMessage.fromNumber
                        sender = user.User( temp_path )
                        if sender.exitChannel( channelToLeave ) == True:
                            sender.sendSMS( "", "derDurchschlag", "you left the channel '" + channelToLeave + "'" )
                        else:
                            sender.sendSMS( "", "derDurchschlag", "you tryed to left channel '" + channelToLeave + "' but you are not even in that channel"  )
                    else:
                        print("someone tryed to left a channel but is not even registered")

                elif blocks[0] == "join":          #for example: @join.someChannel
                    #pdb.set_trace()
                    if senderIsAlreadyAUser == True:
                        UserFilePath = self.pathToUsers + in_incommingMessage.fromNumber
                        sender = user.User( UserFilePath )
                        successfullyJoined = sender.joinChannel( blocks[1] )
                        if successfullyJoined:
                            sender.sendSMS( "", "derDurchschlag", "you joined the channel '" + blocks[1] + "'. cu!" )
                        else:
                            sender.sendSMS( "", "derDurchschlag", "it seems, you are already in the channel '" + blocks[1] + "'" )
                    else:
                        #user tryed to join a channel but is not even an existing user...
                        toSendString =  "echo 'derDurchschlag: you tryed to join a channel but you need to join the system first. send '@hello.yourNickname.join.someChannel' to do so' | gammu-smsd-inject TEXT " + in_number 
                        os.system( toSendString )

            elif len( blocks ) == 1:
                if blocks[0] == "ping":                               # @ping
                    print( "sending a pong to: " + in_incommingMessage.fromNumber )
                    toSendString =  "echo pong | gammu-smsd-inject TEXT " + in_incommingMessage.fromNumber 
                    os.system( toSendString )
                elif blocks[0] == "mute":                           #mute
                    if senderIsAlreadyAUser == True:
                        UserFilePath = self.pathToUsers + in_incommingMessage.fromNumber
                        sender = user.User( UserFilePath )
                        sender.mute()
                    else:
                        #user tryed to mute not even an existing user...
                        print("user tryed to mute not even an existing user...")
                        toSendString =  "echo 'derDurchschlag: you tryed to mute a channel but you need to join the system first. send '@hello.yourNickname.join.someChannel' to do so' | gammu-smsd-inject TEXT " + in_number 
                        os.system( toSendString )
                elif blocks[0] == "unmute":                         # @unmute
                    if senderIsAlreadyAUser == True:
                        UserFilePath = self.pathToUsers + in_incommingMessage.fromNumber
                        sender = user.User( UserFilePath )
                        sender.unmute()
                    else:
                        print("user tryed to unmute not even an existing user...")
                        toSendString =  "echo 'derDurchschlag: you tryed to unmute a channel but you need to join the system first. send '@hello.yourNickname.join.someChannel' to do so' | gammu-smsd-inject TEXT " + in_number 
                        os.system( toSendString )
                else:
                    if len(blocks) == 1 and senderIsAlreadyAUser == True:                        #command only consists of one word. for example '@mensen'. then its clear, it is a channel name
                        channelName = blocks[0].split(" ")[0]
                        messageHasBeenSend = False                  #message has been send at least once. if not, we can write the user back, that the channel is empty
                        allUsers = self.getAllUsers()
                        sender = user.User(self.pathToUsers+in_incommingMessage.fromNumber)
                        channelsSenderIsIn = sender.getChannels()
                        if channelName in channelsSenderIsIn:    #checking if sender is in that channel
                            for otherUser in allUsers:
                                channelsOtherUserIsIn = otherUser.getChannels()
                                if channelName in channelsOtherUserIsIn:
                                    if otherUser.getNumber() != in_incommingMessage.fromNumber or self.senderGetsHisOwnMessage:          #the sender doesn't need to get his own message
                                        otherUser.sendSMS( channelName, sender.getNick(), potentialText )
                                        messageHasBeenSend = True
                            if messageHasBeenSend == False:
                                toSendString = "you tryed to send a message to the channel '" + str( channelName ) + "' but it seems, you are the only one in that channel. make sure, the channel-name is not missspelled or join another channel with more party-people. or contact your admin."
                                sender.sendSMS("", "derDurchschlag", toSendString)
                        else:
                            toSendString = "echo 'derDurchschlag: your tryed to send a message to channel '" + str(channelName) + "' but you are not even in that channel. please send '@join." + str(channelName) + "' to do so."
                            sender.sendSMS("", "derDurchschlag", toSendString)
                    else:
                        #user tryed to send a message to a channel, but is not even an existing user
                        print("user tryed to send a message to a channel, but is needs to register first, or used wrong syntax")
        except KeyError:
            print("error while trying to handle a incomming command")
            #missing: send user a sms back, that his command is not valid.



    def writeNewUserFile( self, in_number, in_nick, in_channels):
        print("entering writeUserFile")
        userFilePath = self.pathToUsers + in_number
        userFile = open( userFilePath, 'a')
        userFile.write( "nick: " + in_nick + "\n" )
        userFile.write( "channels: " + in_channels[0] )
        if len(in_channels) > 1:
            for index in range( 1, len(in_channels) ):
                userFile.write( "," + in_channels[index] )
        userFile.write("\n")
        userFile.write("mutedUntil: \n")
        userFile.close()



    def handlePullMessageRequest( self, in_incommingMessage ):
        toSendString =  'echo ' + self.pullmessageAnswerArray[in_incommingMessage.answerIndex] + ' | gammu-smsd-inject TEXT ' + in_incommingMessage.fromNumber + ' -len ' + str( len(self.pullmessageAnswerArray[in_incommingMessage.answerIndex]) )
        print("handlePullMessageRequest(): toSendString: " + toSendString )
        os.system( toSendString )
        
        
    def sendDefaultMessageTo(self, in_number):
        toSendString = 'echo ' + self.pullmessageDefaultAnswer + ' | gammu-smsd-inject TEXT ' + in_number + ' -len ' + str( len(self.pullmessageDefaultAnswer) )
        print("sendDefaultMessageTo(): toSendString: " + toSendString) 
        os.system(toSendString)
