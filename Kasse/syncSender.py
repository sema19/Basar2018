'''
Created on Aug 26, 2018

@author: sedlmeier
'''

import requests
import json
import threading
from LocalStorage import LocalStorage
import traceback


from threading import Event
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

import logging
logger = logging.getLogger('sync')
logger.setLevel(logging.INFO)

localSyncEvent = threading.Event()
localSyncStopEvent = threading.Event()


# ---------------------------------------------------------------------------  
def updatePaydesk(ls,paydesk):
    ''' Update sold items with all sold items of other playdesks    
    '''
    logger.debug("Update Paydesk:"+str(paydesk))
    paydeskId=paydesk[0].strip("\n\r\t ")
    syncIp=paydesk[4].strip("\n\r\t ")
    syncPort=paydesk[5]
    paydeskCnt=ls.getSoldPaydeskCnt(paydeskId)        
    url = "http://%s:%d/sync"%(syncIp,int(syncPort))    #/?idx=%d'''%(ip,port,idx)
    params=json.dumps({'paydeskId':paydeskId,'idx':paydeskCnt,'cnt':50}).encode()
    headers={'content-type':u'application/json'}
    logger.debug("URL: "+str(url)+", Data: "+str(params))
    try:
        r=requests.post(url, data=params, headers=headers)        
        logger.debug(str(r.status_code)+", "+str(r.reason)+", "+str(r.text))
        items=json.loads(r.text)         # r.text holds the payload data                        
        ls.addRemoteSoldItems(items)
    except requests.exceptions.ConnectionError as e:
        logger.debug("Connection refused to %s:%s Error:%s"%(str(syncIp),str(syncPort),str(e)))                     
    except Exception as e:
        logger.error(e)

# ---------------------------------------------------------------------------
def startLocalSync():
    global localSyncEvent
    global localSyncStopEvent    
    
    localSyncThread = threading.Thread(name="localSync",target=runLocalSync,
                                       args=[localSyncEvent,localSyncStopEvent])
    localSyncThread.start()    
    return localSyncStopEvent
        
# ---------------------------------------------------------------------------        
def runLocalSync(syncEvent, stopEvent):    
    ''' Run through remote paydesks and get the latest articles
    '''    
    logger.info("start local sync thread")
    localSyncStopEvent.clear()
    remotePaydesksCnt=0
    while(1):
        ev = localSyncEvent.wait(10)
        logger.debug("local sync")
        localSyncEvent.clear()
        if localSyncStopEvent.isSet():
            localSyncStopEvent.clear()
            logger.info("local sync stop")
            break
        
        ls = LocalStorage()
        try:
            # get items                    
            paydesks=ls.getRemotePaydesks()
            
            if paydesks==None:
                raise Exception("no paydesks found")
            
            if remotePaydesksCnt!= len(paydesks):
                for paydesk in paydesks:
                    logger.info('-'*40+" paydesk change detected")
                    logger.info(str(paydesk))
            remotePaydesksCnt=len(paydesks)            
            
            logger.debug("iterate through remote paydesks (%d)"%remotePaydesksCnt)        
            for paydesk in paydesks:
                try:
                    updatePaydesk(ls,paydesk)
                except:
                    logger.error(traceback.format_exc())
        except Exception as e:
            logger.error(e)
        finally:
            del ls
        
            
        
# ---------------------------------------------------------------------------
def triggerLocalSync():
    global localSyncEvent
    logger.debug("trigger local sync event")
    localSyncEvent.set()
    
# ---------------------------------------------------------------------------
def stopLocalSync():
    global localSyncEvent
    global localStopEvent
    logger.info("set stop local sync event")
    localSyncStopEvent.set()
    localSyncEvent.set()  
    
    

