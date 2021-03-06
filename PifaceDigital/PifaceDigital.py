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
inputs_com=[]
for pin in range(8):
        inputs_com.append([])

def exec_command(argv):  
        global logger
        global pfd
        global running
        
        in_out_put = argv[1]

        if in_out_put == "led" or in_out_put == "output" or in_out_put == "relay" and (pin_number == 0 or pin_number == 1):
                in_out_put = "output"
        elif in_out_put == "input" or in_out_put == "switche" and (pin_number == 0 or pin_number == 1 or pin_number == 2 or pin_number == 3):
                in_out_put = "input"
        #elif in_out_put == "stop":
                #running = False
                #return "stopped"
        else:
                error_msg = "Piface in or output name: " + in_out_put + " does not exist"
                logger.error(error_msg)
                return error_msg

        pin_number = int(argv[2])
        if not(0 <= pin_number < 8):
                error_msg = "Piface pin: " + str(pin_number) + " does not exist"
                logger.error(error_msg)
                return error_msg

        action = argv[3]

        if in_out_put == "output":
                if action == "on":
                        pfio.digital_write(pin_number, 1)
                        return ("switch on output " + str(pin_number))
                elif action == "off":
                        pfio.digital_write(pin_number, 0)
                        return("switch off output " + str(pin_number))
                elif action == "status":
                        if pfd.output_pins[pin_number].value == 1:
                                return("status of output " + str(pin_number) + ": output is on")
                        else:
                                return("status of output " + str(pin_number) + ": output is off")
                elif action == "push":
                        delayTime = 1
                        if len(argv) == 5:
                                delayTime = argv[4]
                        pfio.digital_write(pin_number, 1)
                        time.sleep(delayTime)
                        pfio.digital_write(pin_number, 0)
                        return("push led " + str(pin_number))
                else:
                        error_msg = "Error command: " + action + " does not exist for output"
                        logger.error(error_msg)
                        return(error_msg)
        elif in_out_put == "input":
                if action == "status":
                        if pfd.input_pins[pin_number].value == 1:
                                return("status input " + str(pin_number) + ": input is on")
                        else:
                                return("status input " + str(pin_number) + ": input is off")
                                                                                
                else:
                        error_msg = "Error command: " + action + " does not exist for input"
                        logger.error(error_msg)
                        return(error_msg)

write_lock = threading.Lock()

def input_handle(event):
        global logger
        state = event.chip.input_pins[event.pin_num].value
        write_lock.acquire()
        logger.info("event: " + str(event.pin_num) + " " + str(state))
        for dest in inputs_com[event.pin_num]:
                if dest is None:
                        sys.stdout.write('%s %s\n' % (event.pin_num, state))
                        sys.stdout.flush()
                else:
                        dest.send(bytes(str(event.pin_num) + " " + str(state),'UTF-8'))
        write_lock.release()
                
def server(argv):
        global logger
        global running

        pfio.init(init_board=False)
        global pfd
        pfd = pfio.PiFaceDigital(init_board=False)


        global inputs_com

        global listener
        
        if len(argv) > 1 :
                if argv[1] == "init":
                        pfio.init(init_board=True)
                elif argv[1] == "inputs":

                        listener = pfio.InputEventListener(chip=pfd)
                        for pin in range(8):
                                listener.register(pin, pfio.IODIR_BOTH, input_handle)
                        listener.activate()

                        inputs = list(map(int, sys.argv[2:]))
                        for pin in inputs:
                                inputs_com[pin].append(None)
                        input("Press Enter to stop...")
                        listener.deactivate()
                else:
                        received = exec_command(argv)
                        print(received)
                        logger.info(received)

        logger.info("done")


def init_logger(logger, formatter, logFileName):
        file_handler = RotatingFileHandler(logFileName, 'a', 1000000, 1)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
                                        
        
def main(argv):
        execName = os.path.basename(argv[0])

        pid = str(os.getpid())

        logFileName = "/tmp/" + execName + "_" + getpass.getuser() + ".log"

        global logger
        logger =logging.getLogger()
        logger.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter('COMMAND ' + pid + ' :: %(asctime)s :: %(levelname)s :: %(message)s')
        init_logger(logger, formatter, logFileName)

        logger.info("launch command " + argv[0] +" running on " + pid)
        server(argv)
                

if __name__ == "__main__":
        main(sys.argv)
