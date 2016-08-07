import socket
import sys
import time
from fileListener import FileListenerThread
from listener import ListenerThread
import logging
from Queue import Queue
sys.path.insert(0, '../gui')
from ColorLogger import initializeLogger 
import gui

marsPort = 1337
debugLog = 1338
telemLog = 1339
filePort = 1340

killCommand = 'exit'

sys.argv.pop(0)

serverAddr = 'localhost'
if len(sys.argv) == 1:
    serverAddr = sys.argv[0]
logger = initializeLogger('./', logging.DEBUG, 'mars_logging', sout = True, colors = True)
logger.info('Using server address:', serverAddr)

#Queues responsible for communicating between GUI and this socket client
guiTelemetryInput = Queue()
guiLoggingInput = Queue()
guiOutput = Queue()

#sockets that continuously receive data from server and
#pipe to the user
telemThread = ListenerThread(guiTelemetryInput, serverAddr, telemLog, 'Telemetry Receive', displayInConsole = False)
debugThread = ListenerThread(guiLoggingInput, serverAddr, debugLog, 'Logging Receive')
fileListenerThread = FileListenerThread(serverAddr, filePort)

telemThread.start()
debugThread.start()
fileListenerThread.start()

#socket that will send data to the server
sock = socket.create_connection((serverAddr, marsPort))

try:    
    # Send configuration data
    with open('config.json', 'r') as content_file:
        message = content_file.read().replace('\n','').replace(' ', '')
    sock.sendall(message)
    
    # start gui
    #gui.start(guiOutput, guiLoggingInput, guiTelemetryInput,serverAddr)

    while True:
        command = raw_input('\n')
        sock.sendall(command)
        if command == killCommand:
            time.sleep(2)#lets all messages be displayed from listener
            sock.close()
            telemThread.stop()
            debugThread.stop()
            fileListenerThread.stop()
            break
    
except KeyboardInterrupt:
    logger.warning('Closing socket')
    sock.close()

