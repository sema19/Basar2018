'''
Created on 08.08.2017

@author: Laptop8460
'''

import threading
import time
import traceback
import socket
import json
from sys import platform

import logging
logger = logging.getLogger('sync')
logger.setLevel(logging.INFO)

from LocalStorage import LocalStorage
stopAllEvent=threading.Event()

startSubscriptionUpdateEvent=threading.Event()
publishEvent = threading.Event()
subscriberUpdaterDebug = threading.Event()
subscriberListenerDebug= threading.Event()
subscriberListenerStopEvent = threading.Event()
subscriberSenderStopEvent=threading.Event()
       
broadcastSentEvent=threading.Event()
                     
def startSubscriberUpdater(broadcastPort):    
    # wait for others to subscribe         
    subscriberSender = threading.Thread(name="subscriptionUpdater",
                                        target=runSubscriberUpdater,
                                        args=[broadcastPort])
    subscriberSender.start()

def triggerSubscriberUpdater():
    publishEvent.set()
    
def stopSubscriberUpdater():
    subscriberSenderStopEvent.set()
    publishEvent.set()
    
    
def runSubscriberUpdater(port):
    logger.info("START SUBSCRIBER UPDATER TO PORT %s"%(str(port)))
    subscriberSenderStopEvent.clear()
    broadcastSendCnt=0        
    while(True):        
        logger.debug("SUBSCRIBER UPDATER - WAIT FOR PUBLISH EVENT")
        evRet=publishEvent.wait(30)     # set publish event on new cart sold or after 30 seconds
        if evRet:
            logger.debug("publish event received")        
        publishEvent.clear()
        publish=True        
        try:
            if publish:                
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                ls = LocalStorage()
                ret = ls.getLocalPaydesk()
                if ret!=None:
                    if subscriberSenderStopEvent.isSet():
                        logger.debug("send publish broadcast bye!")
                        action="bye"
                    else:
                        logger.debug("send publish broadcast")
                        action="subscribe"                    
                    json_subscribe=json.dumps({"action":action,"paydeskId":ret[0],"name":ret[1],"created":ret[2],"updated":ret[3],"syncIp":ret[4], "syncPort":ret[5]})
                    if broadcastSendCnt%10:
                        logger.debug("Broadcast:"+str(json_subscribe))
                    broadcastSendCnt+=1
                    sock.sendto(str(json_subscribe).encode('utf-8'), ('192.168.2.255', port))     #192.168.255.255
                    broadcastSentEvent.set()
                    
                else:
                    logger.debug("subscription update failed - no paydesk received")
                del ls
        except:
            logger.error(traceback.format_exc())
        
        if subscriberSenderStopEvent.isSet():
            subscriberSenderStopEvent.clear()
            # that late to be able to say good bye with broadcast
            logger.info("STOP SUBSCRIBER UPDATER")
            break    
                




def startSubscriberListener(broadcastIp, broadcastPort):
    # start register interface
    subscriberListener = threading.Thread(name="subscriptionService",
                                          target=runSubscriberListener,
                                          args=[broadcastIp,broadcastPort])
    subscriberListener.start()

def stopSubscriberListener():
    subscriberListenerStopEvent.set()
    

def runSubscriberListener(ip,port):
    subscriberListenerStopEvent.clear()
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    if platform=="linux" or platform=="linux2":
        ipa=ip.split('.')[0:3]
        ipa.append('255')
        sock.bind(('.'.join(ipa), port))
    else:
        sock.bind((ip, port))
    logger.info("START SUBSCRIBER LISTENER AT %s:%s"%(str(ip),str(port)))    
    while True:
        # wait for message
        #logger.debug("Wait for receive")
        recv,info = sock.recvfrom(1024)
        if subscriberListenerStopEvent.isSet():
            subscriberListenerStopEvent.clear()
            logger.info("STOP SUBSCRIBER LISTENER")
            break
            
        #logger.debug("RECEIVED from %s:%s Data:%s"%(str(info[0]),str(info[1]), str(recv) ))        
        if info[0]==ip:
            # own broadcast
            #logger.debug("OWN BROADCAST RECEIVED from %s:%s Data:%s"%(str(info[0]),str(info[1]), str(recv) ))
            if not broadcastSentEvent.isSet():
                logger.error("Error: own broadcast was not received")
            broadcastSentEvent.clear()
        else:
            jsonData = json.loads(recv.decode())
            ls = LocalStorage()            
            paydeskId=jsonData["paydeskId"]
            name=jsonData["name"]
            create=jsonData["created"]
            updated=jsonData["updated"]
            syncIp=jsonData["syncIp"]
            syncPort=int(jsonData["syncPort"])
            ret=ls.createRemotePaydesk(paydeskId, name, create, updated, syncIp, syncPort)
            if ret!=None:
                logger.info("CREATED REMOTE PAYDESK FROM BROADCAST: %s at %s:%s"%(str(paydeskId),str(syncIp),str(syncPort)))
            del ls
            
        
                                    
            

        
        
