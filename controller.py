
import os
import sys
import time
import pdb
import glob
from datetime import datetime, timedelta
from dateutil import parser


import user

class Controller:
    
    pathToUsers = ""
    pathToInbox = ""
    delay = -1
    senderGetsHisOwnMessage = False

    def __init__(self, in_pathToUsers, in_pathToInbox, in_delay):
        #pdb.set_trace()
        if in_pathToInbox[-1:] != "/":
            in_pathToInbox = in_pathToInbox + "/"
        if in_pathToUsers[-1:] != "/":
            in_pathToUsers = in_pathToUsers + "/"
        self.pathToUsers = in_pathToUsers
        self.pathToInbox = in_pathToInbox
        self.delay = in_delay
        print("inbox path: " + self.pathToInbox)
        print("user path: " + self.pathToUsers)
        #check for new messages:
        while 42 == 42:
            #print("once again")
            time.sleep( int(self.delay) )
            completePath = self.pathToInbox[:-1] + "/*.txt"
            pathesToIncommingMessages = glob.glob( completePath )
            for path in pathesToIncommingMessages:
                print("\n\nreceived a message: " + str(path) )
                numberOfSender = path.split("_")[3]
                textFile = open(path, 'r')
                text = textFile.read()
                text = text.lower()             #everything to lower case. it could cause problems, when channel names are not spelled correctly (upper/lower-case)
                if text[-1:] == "\n":
                    text = text[:-1]            #removing "/n" if there (happens at debugging)
                
                print("text: " + text)
                self.interpretMessage( numberOfSender, text )
                print("removing file: " + path)
                os.remove(path)


    def getAllUsers(self):
        pathesToUsers = glob.glob(self.pathToUsers + "*")
        output = []
        for path in pathesToUsers:
            otherUser = user.User(path)
            output.append(otherUser)
        return output


    def interpretMessage(self, in_numberOfSender, in_text):
        #catch special cases:
        if in_text == "mute":
            in_text = "@mute"       #because most people probalby won't accept the "@", i'm doing an exeption here. "mute" without an "@" is enough to mute, and will be handlet the same as "@mute"
        elif in_text == "ping":
            in_text = "@ping"    
        elif in_text == "":           #handle empty messages to avoid spam
            print("that was an empty message from: " + in_numberOfSender )
            return False
        elif in_text == "unmute":
            in_text = "@unmute"

        if in_text[0] == "@":
            print("it is a command")
            self.interpretCommand( in_numberOfSender, in_text )
        
        #if the message doesn't beginn with an "@", 
        #then we just want to send the message to channel, the user is in
        #if the user is in more then one channel, this doesn't work and 
        #the user needs to get a sms about that fact
        else:
            #neet to check, it the user is existing in database:
            sender = False
            allUsers = self.getAllUsers()
            for user in allUsers:
                if in_numberOfSender == user.getNumber():
                    sender = user

            if sender != False:
                #temp_path = self.pathToUsers + in_numberOfSender 
                #sender = user.User( temp_path )
                channelsSenderIsIn = sender.getChannels()

                #pdb.set_trace()
                
                if len(channelsSenderIsIn) == 1:                    # user is in one channel or in no channel
                    if channelsSenderIsIn[0] == "":                 #user is in no channel
                        sender.sendSMS( "", "derDurchschlag", "you are in no channel. please send '@join.channelName' to join a channel")
                    else:                                           #user is only in one channel
                        allOtherUsers = self.getAllUsers()
                        for otherUser in allOtherUsers:
                            channelsOtherUserIsIn = otherUser.getChannels()
                            if channelsSenderIsIn[0] in channelsOtherUserIsIn:
                                #pdb.set_trace()
                                if ( otherUser.getNumber() != in_numberOfSender ) or self.senderGetsHisOwnMessage:        #sender doesn't need to get his own message
                                    otherUser.sendSMS( channelsSenderIsIn[0], sender.getNick(), in_text )

                if len( channelsSenderIsIn ) > 1:
                    sender.sendSMS( "", "derDurchschlag", "you are in more then one channel. you must specify the channel, you want to send your message to. do that by add '@channelName' to the beginning of your message")
            else:
                print("received a message but doesn't begin with an '@' and is not in database")

    
    def interpretCommand(self, in_number, in_text ):
        print("entering interpretCommand()")
        commandBlock = in_text.split(" ")[0]
        noMessageContent = False
        potentialText = ""
        try:
            potentialText = in_text.split(" ", 1)[1]
        except IndexError:
            noMessageContent = True
        blocks = commandBlock.split(".")
        print("blocks: " + str( blocks ) )
        blocks[0] = blocks[0][1:]       #remove the "@" from first block
        pathToAllExistingUsers = glob.glob(self.pathToUsers + "*")
        NumbersOfAllExistingUsers = []
        senderIsAlreadyAUser = False
        #pdb.set_trace()
        for path in pathToAllExistingUsers:
            NumbersOfAllExistingUsers.append( path.split("/")[-1] )
        if in_number in NumbersOfAllExistingUsers:
            senderIsAlreadyAUser = True

        try:

            if len(blocks) == 4:
                if ( blocks[0] == "hello" or blocks[0] == "hallo" ):
                    if senderIsAlreadyAUser == False:
                        if blocks[2] == "join":  #for example: @hallo.myNickname.join.SomeChannelName
                            nick = blocks[1]
                            channel = []
                            channel.append(blocks[3])
                            self.writeNewUserFile( in_number, nick, channel )
                            temp_path = self.pathToUsers + in_number
                            sender = user.User( temp_path )
                            sender.sendSMS( "", "derDurchschlag", "you have been added to channel: '" + channel[0] + "'")
                        else:
                            print("wrong syntax")
                            toSendString =  "echo 'it seems you used a wrong syntax. write: @join.channelName' | gammu-smsd-inject TEXT " + in_number 
                            os.system( toSendString )
                    else:                       # senderIsAlreadyAUser == True
                        #user is already an existing user
                        sender = user.User( self.pathToUsers + in_number )
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
                        self.writeNewUserFile( in_number, nick, channels )
                    else:                       # senderIsAlreadyAUser == True
                        #user is already an existing user
                        sender = user.User( self.pathToUsers + in_number )
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
                        temp_path = self.pathToUsers + in_number
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
                        UserFilePath = self.pathToUsers + in_number
                        sender = user.User( UserFilePath )
                        sender.joinChannel( blocks[1] )
                        sender.sendSMS( "", "derDurchschlag", "you joined the channel " + blocks[1] )
                    else:
                        #user tryed to join a channel but is not even an existing user...
                        toSendString =  "echo 'derDurchschlag: you tryed to join a channel but you need to join the system first. send '@hello.yourNickname.join.someChannel' to do so' | gammu-smsd-inject TEXT " + in_number 
                        os.system( toSendString )

            elif len( blocks ) == 1:
                if blocks[0] == "ping":                               # @ping
                    print( "sending a pong to: " + in_number )
                    toSendString =  "echo pong | gammu-smsd-inject TEXT " + in_number 
                    os.system( toSendString )
                elif blocks[0] == "mute":                           #mute
                    if senderIsAlreadyAUser == True:
                        UserFilePath = self.pathToUsers + in_number
                        sender = user.User( UserFilePath )
                        sender.mute()
                    else:
                        #user tryed to mute not even an existing user...
                        print("user tryed to mute not even an existing user...")
                        toSendString =  "echo 'derDurchschlag: you tryed to mute a channel but you need to join the system first. send '@hello.yourNickname.join.someChannel' to do so' | gammu-smsd-inject TEXT " + in_number 
                        os.system( toSendString )
                elif blocks[0] == "unmute":                         # @unmute
                    if senderIsAlreadyAUser == True:
                        UserFilePath = self.pathToUsers + in_number
                        sender = user.User( UserFilePath )
                        sender.unmute()
                    else:
                        print("user tryed to unmute not even an existing user...")
                        toSendString =  "echo 'derDurchschlag: you tryed to unmute a channel but you need to join the system first. send '@hello.yourNickname.join.someChannel' to do so' | gammu-smsd-inject TEXT " + in_number 
                        os.system( toSendString )
                else:
                    if len(blocks) == 1 and senderIsAlreadyAUser == True:                        #command only consists of one word. for example '@mensen'. then its clear, it is a channel name
                        channelName = blocks[0].split(" ")[0]
                        messageHasBeenSend = False
                        allOtherUsers = self.getAllUsers()
                        sender = user.User(self.pathToUsers+in_number)
                        for otherUser in allOtherUsers:
                            channelsOtherUserIsIn = otherUser.getChannels()
                            if channelName in channelsOtherUserIsIn:
                                if (otherUser.getNumber() != in_number) or self.senderGetsHisOwnMessage:          #the sender doesn't need to get his own message
                                    otherUser.sendSMS( channelName, sender.getNick(), potentialText )
                    else:
                        pass
                        #user tryed to send a message to a channel, but is not even an existing user
                        print("user tryed to send a message to a channel, but is needs to register first, or used wrong syntax")
        except KeyError:
            pass
            print("error while trying to handle a incomming command")
            pdb.set_trace()
            #missing: send user a sms back, that his command is not valid.



    def writeNewUserFile( self, in_number, in_nick, in_channels):    #, in_generalMute ):
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

