'''
Created on 21.08.2017

@author: Laptop8460
'''

import requests
import json
import pprint
import sqlite3
import threading
import time
from LocalStorage import LocalStorage

import webDownload 

webSyncEvent = threading.Event()
webSyncEndEvent=threading.Event()
blockWebSync=threading.Event()



# -------------------------------------------------------------------------
def startWebSync():
       
    webSyncThread = threading.Thread(name="websync",target=runWebSync)
    webSyncThread.start()
     
    '''
    webDownloadThread = threading.Thread(name="webDownload",target=runWebDownload)
    webDownloadThread.start()
    '''          
# -------------------------------------------------------------------------
def runWebSync():
    while(1):                
        ev = webSyncEvent.wait()
        webSyncEvent.clear()        
        ls=LocalStorage()
        settings = ls.getSettings()
        url=settings[2]
        ip=settings[3]
        regid=settings[4]
        lastMod =webDownload.requestLastModified(url,ip,regid)
        lastModUsers=0
        lastModItems=0
        ls.lastModifiedUsers()
        ls.lastModifiedItems()
        maxid=0
        cnt=10
        print("-"*30)        
        usersRespDict = webDownload.requestUpdate(url,ip,regid,maxid,cnt)            
        userslist=usersRespDict.get("users",{}).get("insert",[])
        for usr in userslist:
            print(usr)
        if len(usersRespDict)>=cnt:
            maxid+=cnt
        else:
            break
                
        print("-"*30)
        maxid=0
        cnt=20
        itemsRespDict = webDownload.requestInit(url,ip,regid,maxid,cnt)
        itemslist=itemsRespDict.get("items",{}).get("insert",[])
        for item in itemslist:
            print(item)
        if len(itemslist)>=cnt:
            maxid+=cnt        
        print("-"*30)
        
        webSyncEndEvent.set()
        if webSyncEndEvent.is_set():
            break
        
