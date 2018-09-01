'''
Created on Aug 25, 2018

@author: sedlmeier
'''
'''
Created on 21.08.2017

@author: Laptop8460
'''

import requests
import json
import threading
from LocalStorage import LocalStorage

webDownloadEvent =threading.Event()

# -------------------------------------------------------------------------
def requestLastModified(url, ip, regid, tblList=["items","users"]):    
    #url = '''https://K2:54746688@int.basar-teugn.de/kasse'''
    #data={'modus':'lastmodified','ip':'192.168.2.10','registerid':12,'table':["items","users"]}
    data={'modus':'lastmodified','ip':ip,'registerid':regid,'table':tblList}
    #params = '''modus=lastmodified&ip=192.168.2.10&registerid=10&table=["items","users"]'''
    headers = {u'content-type': u'application/x-www-form-urlencoded'}   
    #r=requests.request('GET', url=url, headers=headers, auth=('admin','adMIN16gs'))
    r=requests.post(url=url, headers=headers, data=data)
    print(r.status_code,r.reason)
    print(r.text)
    items=json.loads(r.text)         # r.text holds the payload data
    '''
    {"message":"Wiederholter Sync erfolgreich.","modified":{"items":"2017-08-16 08:01:40","users":"2017-08-17 07:20:44"}}
    '''
    return items    

# -------------------------------------------------------------------------
def requestInit(url, ip, regid, mxid, cnt):
    #url = '''https://K2:54746688@int.basar-teugn.de/kasse'''
    data={'modus':'init','ip':ip,'registerid':regid,'table':'items',"maxid":mxid,"maxanzahl":cnt}
    headers = {u'content-type': u'application/x-www-form-urlencoded'}
    r=requests.post(url,headers=headers,data=data)
    print(r.status_code,r.reason)
    items=json.loads(r.text)         # r.text holds the payload data
    '''
    {"items":{"insert":[["4391","11","1","10310168","Schneeanzug einteilig","92","10.00","2016-08-15 18:37:46","2016-08-15 18:38:37"],["4392","11","2","10310267","Winterjacke gef\u00c3\u00bcttert","92","10.00","2016-08-15 18:39:28","2016-08-16 10:27:42"],["4394","43","1","14010163","Winnie the Pooh Rucksack","","4.00","2016-08-16 07:44:25","2017-06-09 17:35:28"]]},"message":"Wiederholter Sync erfolgreich."}
    '''
    return items

# -------------------------------------------------------------------------
def requestUsers(url, ip, regid, mxid, cnt):
    #url = '''https://K2:54746688@int.basar-teugn.de/kasse'''
    data={'modus':'init','ip':ip,'registerid':regid,'table':'users',"maxid":mxid,"maxanzahl":cnt}
    headers = {u'content-type': u'application/x-www-form-urlencoded'}
    r=requests.post(url,headers=headers,data=data)
    print(r.status_code,r.reason)
    users=json.loads(r.text)         # r.text holds the payload data
    
    return users

# -------------------------------------------------------------------------
def requestUpdate(url, ip, regid):
    #url='''https://K2:54746688@int.basar-teugn.de/kasse'''    
    #data={'modus':'update','ip':'192.168.2.10','registerid':12,'table':'items','maxwerte':{"users":"2018-06-09 21:21:21","items":"2017-06-09 19:35:28"}}
    data={'modus':'update','ip':ip,'registerid':regid,'maxwerte':json.dumps({"users":"2018-06-09 21:21:21","items":"2017-06-09 19:35:28"})}
    headers = {u'content-type': u'application/x-www-form-urlencoded'}
    r=requests.post(url,headers=headers,data=data)
    print(r.status_code,r.reason)
    items=json.loads(r.text)         # r.text holds the payload data
    '''
    {"users":{"insert":[],"update":[]},"items":{"insert":[["10900","9","1","1021001175","Test","24","13.50","2017-07-20 18:03:14","2017-07-20 18:09:19"],["10901","9","2","1021102179","Test2","ad","14.00","2017-07-20 18:14:39","2017-07-20 18:14:39"],["10902","9","3","1020903173","adfasdf","","1.00","2017-07-20 18:14:48","2017-07-20 18:14:48"],["10903","9","4","1020804173","ddasf","","0.50","2017-07-20 18:14:56","2017-07-20 18:14:56"]],"update":[["4400","43","7","14010767","Marienk\u00c3\u00a4ferkost\u00c3\u00bcm","104\/110","4.00","2016-08-16 08:01:40","2017-08-16 08:01:40"]]},"message":"Wiederholter Sync erfolgreich.","lastscan":0}
    '''
    return items
 
# -------------------------------------------------------------------------
def usersDownload(ls, url, ip, regid, deleteOld=True):
    lastMod =requestLastModified(url,ip,regid, tblList="users")
    maxid=0
    cnt=100
    print("-"*30)
    usersLeft=True    
    ls.createUsersTable(deleteTable=deleteOld)
    while(usersLeft):
        print("REQUEST USERS MaxID: %d, CNT: %d"%(maxid,cnt))
        usersRespDict = requestUsers(url,ip,regid,maxid,cnt)
        userslist=usersRespDict.get("users",{}).get("insert",[])        
        print("GOT USERS FROM %s TO %s, CNT: %d"%(str(userslist[0][0]),str(userslist[-1][0]),len(userslist)))
        ls.insertUserList(userslist)            
        if len(userslist)>=cnt:
            maxid+=int(userslist[-1][0])            
        else:
            usersLeft=False
    print("-"*30)

# -------------------------------------------------------------------------    
def itemsDownload(ls, url, ip, regid,deleteOld=True):            
    lastMod =requestLastModified(url,ip,regid,tblList="items")
    maxid=0
    cnt=200
    itemsLeft=True
    ls.createItemsTable(deleteTable=deleteOld)
    while(itemsLeft):
        print("REQUEST ITEMS MaxID: %d, CNT: %d"%(maxid,cnt))
        itemsRespDict = requestInit(url,ip,regid,maxid,cnt)
        itemslist=itemsRespDict.get("items",{}).get("insert",[])
        ls.insertItemsList(itemslist)        
        print("GOT ITEMS FROM %s TO %s, CNT: %d"%(str(itemslist[0][0]),str(itemslist[-1][0]),len(itemslist)))
        if len(itemslist)>=cnt:
            maxid=int(itemslist[-1][0])
        else:
            itemsLeft=False        
    print("-"*30+"DONE ITEMS DOWNLOAD")


# -------------------------------------------------------------------------
def startWebDownload(url,ip,regid):       
    webDownloadThread = threading.Thread(name="webDownload",
                                         target=runWebDownload,
                                         args=[url, ip, regid])
    webDownloadThread.start()    

# -------------------------------------------------------------------------                 
def runWebDownload(url,ip,regid):
    ls=LocalStorage()    
    print("-"*30)
    usersDownload(ls,url,ip,regid)        
    print("-"*30)
    print("-"*30)
    itemsDownload(ls,url,ip,regid)        
    print("-"*30)
    del ls



        
       
    

    