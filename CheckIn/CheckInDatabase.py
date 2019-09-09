'''
Created on Sep 13, 2018

@author: sedlmeier
'''

'''
Created on 08.08.2017

@author: Laptop8460
'''

import sqlite3
from sqlite3 import Error

import uuid
from datetime import datetime
import traceback
import threading
import os
import re

class BasarError(Exception):
    def __init__(self, *args, **kwargs):
        Exception(self,*args,**kwargs)
    
    
class RequestError(BasarError):
    
    def __init__(self, err, msg="unspecified Error", sys_err=None):        
        self.err=err
        self.msg=msg
        self.sys_err=sys_err
      
    def __str__(self):
        return self.msg 

from checkInLogger import logger

__conn_cnt__=0
__conn_cnt_init__=0
__conn_cnt_connect__=0
__disconn_cnt_destr__=0
__disconn_cnt_disconn__=0

localStorageLock=threading.Lock()
debugEventLocalStorage=threading.Event()

def getDatabaseFilepath():    
    return os.path.join(os.getcwd(),"../Kasse/basarDb.sqlite")

class CheckInDatabase(object):


    # -------------------------------------------------------------------------
    def __init__(self, db_file=None):
        if db_file==None:            
            self.db_file=getDatabaseFilepath()            
        else: 
            self.db_file=db_file       
        #self.__log__("LOAD DATABASE: %s"%self.db_file)
        self.paydeskArticleCnt=None        
        self.cartId=None
        self.pos=None        
        self.traceConn("INIT")
        self.paydesksInfo=None        
        self.conn =sqlite3.connect(self.db_file)            
        self.curs = self.conn.cursor()
        
        
        
    def setup(self, paydeskName, syncIp, syncPort):
        self.createTables()        
        logger.info("Check local paydesk: %s, %s:%d"%(paydeskName,syncIp,syncPort))
        paydesk=self.createLocalPaydesk(paydeskName,syncIp,syncPort)
        logger.info("Local paydesk: %s"%(str(paydesk)))
        return paydesk
            
    # -------------------------------------------------------------------------
    def traceConn(self,action):
        __debugTrace__=False
        if __debugTrace__:
            global __conn_cnt_init__
            global __conn_cnt_connect__
            global __disconn_cnt_destr__
            global __disconn_cnt_disconn__
            if action=="INIT":
                __conn_cnt_init__+=1
                __conn_cnt__+=1
                if __conn_cnt__>1:
                    logger.info("DB INSTANCE CNT: %d"%__conn_cnt__)
                    logger.debug(traceback.format_exc())             
                #print("CONN_CNT_INIT: %d"%__conn_cnt_init__)
            elif action=="CONNECT":
                __conn_cnt_connect__+=1
                #print("CONN_CNT_CONNECT: %d"%__conn_cnt_connect__)        
            elif action=="DISCONNECT":
                __disconn_cnt_disconn__+=1        
                #print("DISCONN_CNT_DISCONN: %d"%__disconn_cnt_disconn__)
                bcnt=(__conn_cnt_init__+__conn_cnt_connect__)-(__disconn_cnt_destr__+__disconn_cnt_disconn__)
                #print("BALANCE: %d"%bcnt)
            elif action=="DESTR":
                __conn_cnt__-=1
                __disconn_cnt_destr__+=1
                #print("DISCONN_CNT_DESTR: %d"%__disconn_cnt_destr__)
                #bcnt=(__conn_cnt_init__+__conn_cnt_connect__)-(__disconn_cnt_destr__+__disconn_cnt_disconn__)
                #print("BALANCE: %d"%bcnt)
                
    # -------------------------------------------------------------------------
    def __log__(self, *args, **kwargs):    
        try:
            logger.debug(args[0])                        
        except:
            pass
        
    # -------------------------------------------------------------------------    
    def dbQueryOne(self,stmt):
        try:
            self.__log__(stmt)
            self.curs.execute(stmt)
            ret = self.curs.fetchone()
            #self.__log__("FETCHONE: "+str(ret))
            return ret
        finally:
            pass
        return None
            
    # -------------------------------------------------------------------------    
    def dbQueryAll(self,stmt):
        try:            
            self.__log__(stmt)
            self.curs.execute(stmt)
            ret = self.curs.fetchall()
            #self.__log__("FETCHALL: "+str(ret))
            return ret
        finally:
            pass
            
    # -------------------------------------------------------------------------        
    def dbWrite(self,stmt):
        try:
            self.__log__(stmt)
            self.curs.execute(stmt)
            self.conn.commit()            
        finally:
            pass
    
    # -------------------------------------------------------------------------        
    def dbWriteMultiple(self,stmtList):
        try:
            self.conn =sqlite3.connect(self.db_file)            
            self.curs = self.conn.cursor()
            for stmt in stmtList:                                    
                try:
                    if type(stmt) in [tuple,list]:
                        self.curs.execute(stmt[0],stmt[1])
                    else:
                        self.curs.execute(stmt)
                except:
                    try: 
                        self.__log__(stmt)
                    except:                        
                        self.__log__(traceback.format_exc())                
            self.conn.commit()            
        finally:
            pass
        
    def requestDbAccessInt(self):
        pass
    
    def releaseDbAccessInt(self):
        #self.disconnect()
        pass
        
    def requestDbAccessExt(self):
        #self.connect()
        pass
        
    def releaseDbAccessExt(self):
        #self.disconnect()
        pass
            

    # -------------------------------------------------------------------------    
    def connect(self):        
        try:
            localStorageLock.acquire()            
            self.traceConn("CONNECT")            
            self.conn =sqlite3.connect(self.db_file)            
            self.curs = self.conn.cursor()
        except Error as e:
            self.__log__(str(e))
            raise e
        finally:
            pass
            
    # -------------------------------------------------------------------------    
    def execute(self,stmt):
        self.__log__("EXECUTE:"+stmt)
        self.curs.execute(stmt)         
        
    # -------------------------------------------------------------------------    
    def disconnect(self):
        try:        
            localStorageLock.release()
        except: pass
        self.traceConn("DISCONNECT")
        self.conn.close()
    
    # -------------------------------------------------------------------------    
    def __del__(self):             
        self.traceConn("DESTR")   
        try:
            self.conn.close()
        except:
            logger.error("Error at closing")
            logger.error(traceback.format_exc())             
        try:
            
            localStorageLock.release()
        except:
            pass        
     
    # -------------------------------------------------------------------------
    def createTables(self):
        try:
            #r"I:\Eclipse\basar\workspace\Database\test6.sqlitedb"
            #if not os.path.exists(self.db_file):
            #    os.makedirs(os.path.basename(self.db_file))
            logger.info("Create/Connect to database "+self.db_file)
            #self.conn =sqlite3.connect(self.db_file)
            #self.curs=self.conn.cursor()
            
            self.createPaydeskTable()
            
            self.createCartsTable()
                   
            self.createArticleTable()
            
            self.createSoldTable()
                                    
            self.createSettingsTable()
            
            self.createCheckInTable()
            
        except Exception as e:
            self.__log__(e)
            self.__log__(traceback.format_exc())
            raise e
        #finally:
            #self.conn.close() 
    
    # -------------------------------------------------------------------------
    #
    #---- users
    #
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    def createUsersTable(self, deleteTable=False):
        if deleteTable:            
            self.curs.execute("DROP TABLE IF EXISTS users")
            
        # ['42', '157', '', 'Heller', 'Nicole', '09405961131', '2016-08-16 07:10:48', '2016-09-17 17:05:52', 'nicole.heller@hotmail.com', '86217415', '1', '15', '2.00', '30', '1', '2016-09-16 07:15:14', 'V']
        self.curs.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY,
                                                               number TEXT,
                                                               code TEXT,
                                                               vorname TEXT,
                                                               nachname TEXT,
                                                               tel TEXT,
                                                               created DATETIME ,
                                                               email TEXT                                                              
                                                                )''')
    
    # -------------------------------------------------------------------------
    def insertUserList(self, userlist):        
        stmtList=[] 
        for user in userlist:
            if not re.match("^[0-9]+",user[1]):
                logger.info("User Invalid: "+str(user))
            else:       
                stmt= "INSERT INTO users (id,number,code,nachname,vorname,tel,created,email)"
                stmt+=" VALUES (?,?,?,?,?,?,?,?)"
                para=(user[0],user[1],user[2],user[3],user[4],user[5],user[6],user[7])
                stmtList.append((stmt,para))
        ret=self.dbWriteMultiple(stmtList)
        return ret
    
    # -------------------------------------------------------------------------
    def usersDbExists(self):
        ret =self.dbQueryOne("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='users'")
        if ret[0]==1:
            return True                    
        return False
        
    # -------------------------------------------------------------------------
    def getUsersStats(self):
        retDict={}
        ret=None
        if self.usersDbExists():
            ret=self.dbQueryOne("SELECT COUNT(*), MAX(number), MAX(created) FROM users")
        if ret!=None:
            retDict={"count":ret[0], "max_number":ret[1],"max_created":ret[2]}
        else:
            retDict={"count":0, "max_number":0,"max_created":str(datetime.now())}
        return retDict
    
    # -------------------------------------------------------------------------
    def getUsers(self):
        ret=self.dbQueryAll("SELECT * from users")
        return ret
    
    # -------------------------------------------------------------------------
    def getUserInfo(self, user_nr):
        msg=""
        ret=None
        try:
            ret=self.dbQueryOne("SELECT * from users where number=%s"%user_nr)
            if ret==None:
                msg="Kein Benutzer mit der Nummer %s gefunden!"%user_nr
        except Exception as e:
            msg="Fehler bei Benutzerabfrage %s: %s"%(str(user_nr),str(e))
        return ret, msg
         
        
    
        
    
    # -------------------------------------------------------------------------
    #
    #---- Items
    #
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    def createItemsTable(self, deleteTable=False):
        if deleteTable:            
            self.curs.execute("DROP TABLE IF EXISTS items")
            
        # ['42', '157', '', 'Heller', 'Nicole', '09405961131', '2016-08-16 07:10:48', '2016-09-17 17:05:52', 'nicole.heller@hotmail.com', '86217415', '1', '15', '2.00', '30', '1', '2016-09-16 07:15:14', 'V']
        self.curs.execute('''CREATE TABLE IF NOT EXISTS items (id INTEGER  PRIMARY KEY,
                                                               user_id INTEGER,
                                                               nummer INTEGER,
                                                               barcode INTEGER,
                                                               bezeichnung TEXT,
                                                               groesse TEXT ,
                                                               preis FLOAT,
                                                               created DATETIME,
                                                               modified DATETIME
                                                                )''')
    
    # -------------------------------------------------------------------------
    def insertItemsList(self, itemslist):
        stmtList=[] 
        for item in itemslist:                       
            stmt= "INSERT INTO items (id,user_id, nummer,barcode,bezeichnung,groesse,preis,created,modified)"
            stmt+=" VALUES (?,?,?,?,?,?,?,?,?)"
            para=(item[0],item[1],item[2],item[3],item[4],item[5],item[6],item[7],item[8])
            stmtList.append((stmt,para))
        ret=self.dbWriteMultiple(stmtList)
        return ret

        
    # -------------------------------------------------------------------------
    def itemsDbExists(self):
        ret =self.dbQueryOne("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='items'")
        if ret[0]==1:
            return True                    
        return False
    
    # -------------------------------------------------------------------------
    def getItemsStats(self):
        retDict={}
        ret=None
        if self.itemsDbExists():
            ret=self.dbQueryOne("SELECT COUNT(*), MAX(nummer), MAX(created), MAX(modified) FROM items")        
        if ret!=None:
            retDict={"count":ret[0], "max_number":ret[1],"max_created":ret[2],"max_modified":ret[3]}
        else:
            retDict={"count":0, "max_number":0,"max_created":str(datetime.now()),"max_modified":str(datetime.now())} 
        return retDict
    
    def getUserItem(self, user_id):
        msg=""
        ret=None
        try:
            #id,user_id, nummer,barcode,bezeichnung,groesse,preis,created,modified
            ret=self.dbQueryOne("SELECT * FROM items WHERE user_id=%s"%(user_id))
        except Exception as e:
            msg="Fehler bei Abfrage nach Artikel von User"
        if ret==None:
            msg="Keine Artikel gefunden"
        return ret, msg
    
    def getUserItems(self, user_id):
        msg=""
        ret=None
        try:
            #id,user_id, nummer,barcode,bezeichnung,groesse,preis,created,modified
            ret=self.dbQueryAll("SELECT * FROM items WHERE user_id=%s"%(user_id))
        except Exception as e:
            msg="Fehler bei Abfrage nach Artikel von User"
        if ret==None:
            msg="Keine Artikel gefunden"
        return ret, msg
        

    
    # -------------------------------------------------------------------------
    #
    #---- CheckIn
    #
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    def createCheckInTable(self):                        
            self.curs.execute('''CREATE TABLE IF NOT EXISTS checkin ( user_id INTEGER PRIMARY KEY,
                                                                      checkInTime DATETIME                                                                      
                                                                )''')
            print("CHECKIN: "+str(self.curs.fetchone()))
            
    # -------------------------------------------------------------------------
    def addCheckIn(self, user_id):
        checkInTime=str(datetime.now())
        ret = self.dbWrite("INSERT INTO checkin (user_id, checkInTime) VALUES (%s,'%s')"%(str(user_id),str(checkInTime)))
        
    def getCheckInSyncInfo(self):
        ret = self.dbQueryOne("SELECT COUNT(*), MAX(checkInTime) FROM checkin")
        
    def writeSyncRequestReceived(self, paydeskId, idx):
        ret = self.dbWrite("UPDATE paydesks SET lastSyncReqReceived='%s', lastSyncIdx=%d WHERE paydeskId='%s'"%(str(datetime.now()),idx,paydeskId))
    
    def writeSyncRequest(self,paydeskId, itemsSynced):
        ret = self.dbWrite("UPDATE paydesks SET lastFailedSyncCount=0, itemsSynced=%d WHERE paydeskId='%s'"%(itemsSynced,paydeskId))
            
    def writeFailedSyncRequest(self,paydeskId, requestTime):
        ret = self.dbWrite("UPDATE paydesks SET lastFailedSyncReq='%s', lastFailedSyncCount=lastFailedSyncCount+1 WHERE paydeskId='%s'"%(str(requestTime),paydeskId))
        
    def getStatus(self):
        
        #tblinfo = self.execute('PRAGMA table_info(paydesks)');
        #self.paydesksInfo=tblinfo  
        self.paydesksInfo=['paydeskId','name','created','updated','syncIp','syncPort','remote','lastSyn','lastSyncIdx','itemsSynced','lastFailedSyncReq','lastFailedSyncCount']
        retDict={}          
        retDict["itemsSold"]={}
        stmt = 'select count(*), sum(it.preis) from sold sl left join items it on sl.barcode=it.barcode where status="sold";'
        allSoldRaw = self.dbQueryOne(stmt)
        retDict["itemsSold"]["count"]=str(allSoldRaw[0])
        retDict["itemsSold"]["sum"]=str(allSoldRaw[1])
        
        retDict["itemsSoldByPaydesk"]={}
        stmt = 'select count(*), paydeskId from sold sl where sl.status="sold" group by sl.paydeskId;'
        allSoldPaydeskRaw = self.dbQueryAll(stmt)
        if len(allSoldPaydeskRaw)>0:
            for idx in range(0,len(allSoldPaydeskRaw)):        
                paydeskId =str(allSoldPaydeskRaw[idx][1]) 
                if not paydeskId in retDict["itemsSoldByPaydesk"]:
                    retDict["itemsSoldByPaydesk"][paydeskId]={}    
                retDict["itemsSoldByPaydesk"][paydeskId]["sold"]=str(allSoldPaydeskRaw[idx][0])
        
        stmt = "select count(*), paydeskId from sold where status='sold' and soldtime>=datetime('now','-10 min') group by paydeskId;"
        soldLast10minRaw = self.dbQueryAll(stmt)
        if len(soldLast10minRaw)>0:
            for idx in range(0,len(allSoldRaw)):
                paydeskId =str(soldLast10minRaw[idx][1]) 
                if not paydeskId in retDict["itemsSoldByPaydesk"]:
                    retDict["itemsSoldByPaydesk"][paydeskId]={}
                retDict["itemsSoldByPaydesk"][paydeskId]["sold10min"]=str(soldLast10minRaw[idx][0])                             
        
        # synced machines
        stmt="select * from paydesks"
        paydesksRaw = self.dbQueryAll(stmt)
        paydesksDict={}
        if len(paydesksRaw)>0:
                        
            for i in range(0,len(paydesksRaw)):
                innerDict = {}
                for j in range(0,len(paydesksRaw[i])):
                    try:
                        header_name = self.paydesksInfo[j]
                    except:
                        header_name="unknown(%d)"%j
                    value=paydesksRaw[i][j]
                    innerDict[header_name]=str(value)
                paydesksDict[paydesksRaw[i][0]]=innerDict
        
        retDict["paydesks"]=paydesksDict
        return retDict
    
    def getItemsCntAt(self, lastTimestamp):
        stmt = "select count(*) from sold where DATETIME(soldtime)<=DATETIME('%s')" % (lastTimestamp)
        ret = self.dbQueryOne(stmt)                                                                                                                                                                       
        return ret                                                                                                                                                                                
    
    def getItemsSince(self, lastTimestamp):
        stmt = "select cartId,barcode,soldtime from sold where DATETIME(soldtime)<=DATETIME('%s')" % (lastTimestamp)                                                                                  
        ret = self.dbQueryAll(stmt)                                                                                                                                                                       
        return ret 
    
    def getUsersCntAt(self, lastTimestamp):
        stmt = "select count(*) from checkin where DATETIME(checkInTime)<=DATETIME('%s')" % (lastTimestamp)
        ret = self.dbQueryOne(stmt)                                                                                                                                                                       
        return ret
    
    def getUsersSince(self, lastTimestamp):
        stmt = "select user_id,checkInTime from checkin where DATETIME(checkInTime)<=DATETIME('%s')" % (lastTimestamp)                                                                                  
        ret = self.dbQueryAll(stmt)                                                                                                                                                                       
        return ret 
                                     
                     

                