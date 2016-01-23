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
#pdb.set_trace()

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
except:
    print("problem while parsing config-file")
    exit(1)
    

controller = controller.Controller(pathToUsers, pathToInbox, delay)

exit(1)
