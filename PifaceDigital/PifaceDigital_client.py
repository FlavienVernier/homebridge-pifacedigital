#!/usr/bin/python3

import pifacedigitalio as pfio

import sys
import socket
import os
import signal
import time
import threading
import getpass

import logging
from logging.handlers import RotatingFileHandler

running = True
pfd = None

logger = None

listener = None

def usage(programName):
        print("connector pins [action]")
        print()
        print("connectors:")
        print("\t(led|output|relay)")
        print("\twith only one pin in [0..7] except for relay were pin is 0 or 1.")
        print()
        print("\t(input|switche)")
        print("\twith only one pin in [0..7] except for switche were pin is 0, 1, 2 or 3.")
        print()
        print("inputs")
        print("\twith a list of pin in [0..7] except for switche were pin is 0, 1, 2 or 3.")
        print()
        print("Output actions:")
        print("\ton:")
        print("\toff")
        print("\tstatus")
        print("\tpush delay")
        print("Input actions:")
        print("\tstatus")
        print()
        print("Exemple:")
        print("\t" + programName + " relay 1 on")
        print("\t" + programName + " input 0 status")
        print("\t" + programName + " inputs 1 3 0")
        
def client(argv, addr, port):
        global logger
        global running
        if len(argv) > 1 :
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((addr, port))

                logger.info("send: " + " ".join(argv))
                s.send(bytes(" ".join(argv),'UTF-8'))

                running = True
                while running:
                        received = s.recv(2048).decode('UTF-8')
                        #key = getkey(blocking=False)
                        logger.info(received)
                        print(received)
                        if argv[1] != "inputs":
                                running = False
                        elif received == "stop":
                                running = False
                                s.send(bytes("stopped",'UTF-8'))
                        
                s.close()
        else:
                logger.error("NO Arument !!!")

def init_logger(logger, formatter, logFileName):
        file_handler = RotatingFileHandler(logFileName, 'a', 1000000, 1)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
                                        
        
def main(argv):
        execName = os.path.basename(argv[0])

        if "-h" in argv:
                usage(execName)
                sys.exit(0)
                
        logFileName = "/tmp/" + execName + "_" + getpass.getuser() + ".log"
        if len(argv) > 2 and argv[1] == "--conf":
                conf_file = argv[2]
                exec(open(conf_file).read())
                try:
                        log_file
                except NameError:
                        log_file = None
                if log_file is not None:
                        logFileName = log_file

        global logger
        logger =logging.getLogger()
        logger.setLevel(logging.DEBUG)
        

        formatter = logging.Formatter('CLIENT :: %(asctime)s :: %(levelname)s :: %(message)s')
        init_logger(logger, formatter, logFileName)
        logger.info("connect to server...")
        client(argv, "", 1114)

if __name__ == "__main__":
        main(sys.argv)
