

import os
import sys
import pdb
from datetime import datetime, timedelta
from dateutil import parser

class User:
    
    pathToUserFile = ""
    nick = ""
    number = ""
    channels = []
    muteUntil = False
    



    def __init__(self, in_pathToUserFile):
        self.pathToUserFile = in_pathToUserFile
        self.number = in_pathToUserFile.split("/")[-1]
        with open( in_pathToUserFile ) as userFile:
            lines = userFile.readlines()
        #pdb.set_trace()
        for line in lines:
            key = line.split(" ")[0]
            #pdb.set_trace()
            if len( line.split(" ") ) > 1:
                value = line.split(" ")[1][:-1]
                if key[:-1] == "nick":
                    self.nick = value
                elif key[:-1] == "channels":
                    self.channels = value.split(",")
                elif key[:-1] == "mutedUntil":
                    #pdb.set_trace() 
                    value = line[:-1].split(": ", 1)[1]              #because we have a white space in the date and need to split the value differently..
                    #if value != "":
                    if value != "":
                        #pdb.set_trace()
                        self.muteUntil = datetime.strptime( value, "%Y-%m-%d %H:%M:%S" )
                        if self.muteUntil < datetime.now():         # when the muteUntil-time is in the past, it doesn't need to be saved again
                            self.muteUntil = False
                            self.rewriteUserFile()                  #that is actually not necessary, but looks better
                    else:
                        pass
                        #print("there is no muteUntil-value")
                    

    def getChannels(self):
        return self.channels

    def joinChannel(self, in_newChannel):
        self.channels.append( in_newChannel)
        self.rewriteUserFile()

    def exitChannel(self, in_whichChannel):
        #pdb.set_trace()
        if in_whichChannel in self.channels:
            self.channels.remove(in_whichChannel)
            self.rewriteUserFile()
            return True
        else:
            return False

    def getMuteUntil(self):
        return self.muteUntil

    def unmute(self):
        self.muteUntil = False
        self.rewriteUserFile()
                
    def getNick(self):
        return self.nick

    def getNumber(self):
        return self.number    

    def mute(self):
        #pdb.set_trace()
        self.muteUntil = datetime.now() + timedelta( hours = 6 )
        print("user muted until " + str( self.muteUntil ) )
        self.rewriteUserFile()

    def rewriteUserFile(self):
        print("entering rewriteUserFile()")
        #pdb.set_trace()
        os.remove(self.pathToUserFile)          #need to remove the old file, and make a complete new one..
        userFile = open( self.pathToUserFile, 'a')
        userFile.write( "nick: " + self.nick + "\n" )
        #pdb.set_trace()
        try:
            self.channels.remove("")
        except:
            pass
        if len(self.channels) >= 1:
            userFile.write( "channels: " + self.channels[0] )
        if len(self.channels) > 1:
            for index in range(1, len(self.channels) ):
                userFile.write( "," + self.channels[index] )
        if len(self.channels) == 0:
            userFile.write( "channels: " )
        userFile.write("\n")
        stringMuteUntil = ""
        if self.muteUntil != False:
            print( "marked user as muted until: " + stringMuteUntil )
            #serialize mutedUntil:
            #pdb.set_trace()
            stringMuteUntil = '{:%Y-%m-%d %H:%M:%S}'.format( self.muteUntil )
        userFile.write( "mutedUntil: " + stringMuteUntil + "\n")
        userFile.close()

    def sendSMS(self, in_channel, in_sender, in_text):
        print("entering sendSMS()")
        canBeSent = True
        if self.muteUntil != False:                         #check if there is something at all in the muteUntil-variable
            if self.muteUntil > datetime.now():
                canBeSent = False
        if canBeSent == True:
            toSendString =  "echo '(" + in_channel + ") " + in_sender + ":  " + in_text + "' | gammu-smsd-inject TEXT " + self.number 
            #print("sms sending is suppressed")
            os.system( toSendString )
            print("sending SMS to " + self.number + " (" + self.nick + "): " + str( toSendString ) )
        else:
            print("didn't send message to " + self.nick + " (" + self.number + "), because user is muted")
