'''
Created on Sep 12, 2018

@author: sedlmeier
'''

import threading
import signal

from basarLogger import logger


def signal_handler(signal, frame):
    logger.info("\nprogram exiting gracefully")
    Stop()
    
    
signal.signal(signal.SIGINT, signal_handler)


byeEvent=threading.Event()
stopAllEvent = threading.Event()
shutdownEventList=[]

def AddShutdownEvent(ev):
    logger.info("add Shutdown Event (%d)"%(len(shutdownEventList)))
    shutdownEventList.append(ev)    

def mainShutdownObserverThread():
    logger.info("wait for Shutdown Event")
    stopAllEvent.wait()
    logger.info("Shutdown initiated: %d Events"%(len(shutdownEventList)))
    for shutdownEvt in shutdownEventList:        
        shutdownEvt.set()
    #byeEvent.set()
    
        
def Stop():
    logger.info("Stop Event Set")
    stopAllEvent.set()
    
def WaitForBye(t):
    logger.info("wait for bye")
    byeEvent.wait(t)
            
mainShutdownThread = threading.Thread(name="mainShutdownThread", target=mainShutdownObserverThread)
mainShutdownThread.start()  