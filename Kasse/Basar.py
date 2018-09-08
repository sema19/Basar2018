'''
Created on 07.08.2017

@author: Laptop8460
'''

import threading
import os
import time
import webbrowser
import subprocess
import re
from pprint import pformat
import sys
import signal



from basarLogger import logger


from LocalStorage import LocalStorage
from LocalStorage import getDatabaseFilepath

import IntWebserver
from ExtWebserver import runExtWebserver
import service_Subscription
#import runWebSync
#from service_Subscription import startSubscriberListener
#from service_Subscription import startSubscriberUpdater
#from service_Subscription import subscriberSenderStopEvent
#from service_Subscription import subscriberListenerStopEvent
#from service_Subscription import publishEvent
#from runWebSync import runWebSync
#from runWebSync import runWebDownload
import syncSender
import syncReceiver
#from localSync import localSyncEvent
from settings import settingsInst
import requests
from LocalStorage import debugEventLocalStorage
from IntWebserver import stopAllRequested
from ExtWebserver import extWebserverShutdownEvent

stopAllEvent = threading.Event()

threadsRunning={}


#def signal_handler(signal, frame):
#    print("\nprogram exiting gracefully")
#    stopAllEvent.set()
    
#signal.signal(signal.SIGINT, signal_handler)


'''    
def startWebSync():   
    webSyncThread = threading.Thread(name="websync",target=runWebSync)
    webSyncThread.start()
    threadsRunning["webSyncThread"]={"id":webSyncThread}
        
    webDownloadThread = threading.Thread(name="webDownload",target=runWebDownload)
    webDownloadThread.start()
    threadsRunning["webDownloadThread"]={"id":webDownloadThread}
'''     

'''    
def startExternalWebserver(settings):
    # start webserver
    extWebserverPort=settings.getExtWebserverPort()
    ethAdapterIP=settings.extWebserverIp    
    extWebsrvThread = threading.Thread(name="extWebsvr",target=runExtWebserver, args=[ethAdapterIP, extWebserverPort])
    extWebsrvThread.start()
    return extWebsrvThread
'''
    
    
if __name__ == '__main__':
    logger.info("RUN BASAR IN %s"%os.getcwd())    
    
    pid = os.getpid()
    logger.info("RUN AS PID: %s"%str(pid))    
    
    # load settings
    settings=settingsInst        
    
    server_is_running=False
    url = "http://127.0.0.1:8082/srvStatus"    
    headers={'content-type':u'application/json'}
    '''
    try:
        r=requests.get(url=url, headers=headers)
        if r.status_code==200:
            logger.info("SERVER IS RUNNING: "+str(r.text))
            server_is_running=True            
    except Exception as e:
        logger.error("SERVER TEST REQUEST ERROR: %s"%str(e))
    '''

    ethAdapterIP=settings.extWebserverIp
    broadcast_port=settings.getBroadcastPort()
    intWebserverPort=settings.getIntWebserverPort()
    
    logger.info("setup the database")
    ls=LocalStorage(getDatabaseFilepath())
    ls.setup(settings.paydeskName,
             settings.localSyncIp,       # sync ip
             settings.localSyncPort)     # sync port
                
    # start register interface
    logger.info("start subscriber listener")
    service_Subscription.startSubscriberListener(settings.broadcastIp,broadcast_port)
                            
    # start webserver
    logger.info("Start Internal Webserver")
    IntWebserver.startIntWebserver(intWebserverPort)
    
    # wait for others to subscribe
    logger.info("start subscriber updater (subscribe to others)")
    service_Subscription.startSubscriberUpdater(broadcast_port)    
    
    logger.info("start local sync")
    localSyncStopSend = syncSender.startLocalSync()
    localSyncStopRecv = syncReceiver.startSyncWebserver(settings.localSyncIp,settings.localSyncPort)
     
    # start browser    
    logger.info("open webbrowser")
    intWebserverPort=settings.getIntWebserverPort()
    webbrowser.open("http://%s:%d/%s"%(settings.intWebserverIp,
                                       settings.intWebserverPort, 
                                       settings.startpage))    
    
    '''
    while(1):
        
        
        
        stopAllEvent.clear()
        if evtOccured:                      # event set
            logger.info("WAIT FOR SHUTDOWN, TIMEOUT 20 sec ...")
            for t in threadsRunning.keys():
                try:
                    if "stop" in threadsRunning[t].keys():
                        threadsRunning[t]["stop"].set()
                    if "trigger" in threadsRunning[t].keys():
                        threadsRunning[t]["trigger"].set()
                except Exception as e:
                    logger.error(str(e))
                                        
            allDone=False
            tstart=time.time()
            while(allDone==False):
                if time.time()-tstart>20:
                    print("END DUE TO 20 sec TIMEOUT. Threads still running:")
                    for t in threadsRunning.keys():                    
                        if threadsRunning[t]["id"].is_alive():
                            logger.info("Thread %s alive"%(str(t)))
                    break 
                allDone=True
                for t in threadsRunning.keys():                    
                    if threadsRunning[t]["id"].is_alive():
                        allDone=False                        
                        logger.info("Thread %s alive"%(str(t)))
                        continue            
        else:           # timeout
            if stopAllRequested.isSet():
                stopAllEvent.set()
                continue
            for t in threadsRunning.keys():
                if not threadsRunning[t]["id"].is_alive():                                        
                    logger.info("Thread %s NOT alive"%(str(t)))
        '''
    stopAllEvent.wait()
    logger.info("GOODBYE!!!")
    sys.exit(0)
        

    #sys.exit(0)
    