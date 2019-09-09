'''
Created on Sep 13, 2018

@author: sedlmeier
'''

import requests
import json
import threading

from CheckInDatabase import CheckInDatabase
from checkInLogger import logger


upsyncEvent=threading.Event()

# -------------------------------------------------------------------------
def requestLastModified(url, ip, regid, tblList=["items","users"]):    
    #url = '''https://K2:54746688@int.basar-teugn.de/kasse'''
    #data={'modus':'lastmodified','ip':'192.168.2.10','registerid':12,'table':["items","users"]}
    data={'modus':'lastmodified','ip':ip,'registerid':regid,'table':tblList}
    #params = '''modus=lastmodified&ip=192.168.2.10&registerid=10&table=["items","users"]'''
    headers = {u'content-type': u'application/x-www-form-urlencoded'}   
    #r=requests.request('GET', url=url, headers=headers, auth=('admin','adMIN16gs'))
    r=requests.post(url=url, headers=headers, data=data)
    logger.info(str(r.status_code)+"\n"+str(r.reason))
    logger.info(r.text)
    items=json.loads(r.text)         # r.text holds the payload data
    '''
    {"message":"Wiederholter Sync erfolgreich.","modified":{"items":"2017-08-16 08:01:40","users":"2017-08-17 07:20:44"}}
    '''
    return items


def startUpsyncThread(url,ip,regid):
    upsyncThreadId = threading.Thread(name="upsync",target=upsyncThread, args=[url,ip,regid])
    upsyncThreadId.start()


def upsyncThread(url,ip,regid):
    while(1):
        upsyncEvent.wait(10)
        lastMod = requestLastModified(url,ip,regid,["items"])
        modDict = lastMod["modified"]
        lastTimestamp = modDict["items"]
             
        bdb=CheckInDatabase()
        try:
            oldscans = bdb.getUsersCntAt(lastTimestamp)[0]
            itemsRaw = bdb.getUsersSince(lastTimestamp)
            scans=[]
            for idx in range(0,len(itemsRaw)):
                cartId='1';
                barcode=itemsRaw[idx][0]+"10080" 
                timestamp=itemsRaw[idx][1]            
                scan=['1','%d'%cartId,'%d'%barcode,'0','%s'%timestamp,'%d'%oldscans]
                scans.append(scan)
                
            # registerid, id des scans, barcode, art (0=checkin, 1=verkauf (geht aber noch nicht)), 
            # Zeitstempel oldscans ist die Anzahl der Scans                
            # get items from database
            data={'modus':'upsync','ip':ip,'registerid':regid,'scans':scans,'oldscans':oldscans}
            dataJson=json.dumps(data).encode('utf-8')
            #params = '''modus=lastmodified&ip=192.168.2.10&registerid=10&table=["items","users"]'''
            headers = {u'content-type': u'application/x-www-form-urlencoded'}   
            #r=requests.request('GET', url=url, headers=headers, auth=('admin','adMIN16gs'))
            #if "SCHARFSCHALTEN"=="JA":
            r=requests.post(url=url, headers=headers, data=dataJson)
            #else:
            logger.info(str(data))        
        except Exception as e:
            logger.error(str(e))
            pass
