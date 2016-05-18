#!/usr/bin/python3.4

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

try:
    try:
        with open(pathToConfig) as config:
            lines = config.readlines()
    except:
        print("prblem while opening config-file")

    #parsing config-files
    for line in lines:
        if line.split(" ")[0] == "inbox:":
            pathToInbox = line.split(" ")[1][:-1]
        elif line.split(" ")[0] == "users:":
            pathToUsers = line.split(" ")[1][:-1]
        elif line.split(" ")[0] == "delay:":
            delay = int( line.split(" ")[1][:-1] )
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
except:
    print("problem while parsing config-file")
    exit(1)
    
#try:
controller = controller.Controller(pathToUsers, pathToInbox, delay, senderGetsHisOwnMessage)
#except KeyboardInterrupt:
#    print("\nshutdown by user")
#except:
#    print("\nentering except")
#    #pdb.set_trace()
#    text = "derDurchschlag is shutting down. bad coding?"
#    toSendString =  "echo '" + text + "' | gammu-smsd-inject TEXT " + admin
#    os.system( toSendString )
#    print("sending SMS to " + admin + " (admin): " + str( toSendString ) )
    

exit(1)

