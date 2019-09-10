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

from Errors import RequestError

from dbLogger import logger

__conn_cnt__=0
__conn_cnt_init__=0
__conn_cnt_connect__=0
__disconn_cnt_destr__=0
__disconn_cnt_disconn__=0

localStorageLock=threading.Lock()
debugEventLocalStorage=threading.Event()

def getDatabaseFilepath():    
    return os.path.join(os.getcwd(),"basarDb.sqlite")

class LocalStorage(object):


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
                                                               gedruckt INTEGER,
                                                               alt INTEGER,
                                                               created DATETIME,
                                                               modified DATETIME
                                                                )''')
    
    # -------------------------------------------------------------------------
    def insertItemsList(self, itemslist):
        stmtList=[] 
        for item in itemslist:                       
            stmt= "INSERT INTO items (id,user_id, nummer,barcode,bezeichnung,groesse,preis,gedruckt,alt,created,modified)"
            stmt+=" VALUES (?,?,?,?,?,?,?,?,?,?,?)"
            para=(item[0],item[1],item[2],item[3],item[4],item[5],item[6],item[7],item[8],item[9],item[10])
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
    #---- Paydesk
    #
    # -------------------------------------------------------------------------
    
    def createPaydeskTable(self):
        self.paydesksInfo=['paydeskId','name','created','updated','syncIp','syncPort','remote','lastSyncReqReceived',
                           'lastSyncIdx','itemsSynced','lastFailedSyncReq','lastFailedSyncCount']
        self.curs.execute('''CREATE TABLE IF NOT EXISTS paydesks ( paydeskId TEXT PRIMARY KEY,
                                                                      name TEXT,
                                                                      created DATETIME,
                                                                      updated DATETIME,                                                                  
                                                                      syncIp TEXT,
                                                                      syncPort INTEGER,
                                                                      remote BOOL,
                                                                      lastSyncReqReceived DATETIME,
                                                                      lastSyncIdx INTEGER DEFAULT 0,
                                                                      itemsSynced INTEGER DEFAULT 0,
                                                                      lastFailedSyncReq DATETIME DEFAULT CURRENT_TIMESTAMP,
                                                                      lastFailedSyncCount INTEGER DEFAULT 0
                                                                )''')
        
        print("PAYDESKS: "+str(self.curs.fetchone()))
        
        #self.conn.commit()
                     
    # -------------------------------------------------------------------------
    def createLocalPaydesk(self, name, syncIp, syncPort):        
        try:
            self.requestDbAccessInt()
            ret=self.dbQueryOne("SELECT * from 'paydesks' WHERE remote=0")            
            if ret==None:
                self.releaseDbAccessInt()
                tnow=str(datetime.now())                
                paydeskId=uuid.uuid4()                           
                self.requestDbAccessInt()
                self.execute("SELECT * from paydesks WHERE paydeskId='%s'"%paydeskId)
                ret=self.curs.fetchone()        
                if ret==None:
                    logger.info("Create Local Paydesk %s, %s:%d"%(name,syncIp,syncPort))            
                    stmt="INSERT INTO paydesks ('paydeskId', 'name', 'created', 'updated', 'syncIp', 'syncPort', 'remote') "
                    stmt+="VALUES ('%s','%s','%s','%s','%s',%d,%d)"%(paydeskId,name,tnow,tnow,syncIp,syncPort,0)
                    self.dbWrite(stmt)
            else:
                if name!=ret[1] or syncIp!=ret[4] or syncPort!=ret[5]:
                    logger.info("Update Local Paydesk %s, %s:%d"%(name,syncIp,syncPort))            
                    stmt="UPDATE paydesks SET 'name'='%s', 'updated'='%s', 'syncIp'='%s', 'syncPort'=%d where remote=0"%(name,datetime.now(),syncIp,syncPort)
                    self.dbWrite(stmt)
                else:                    
                    logger.info("Local Paydesk already exists: %s"%str(ret))                                               
        finally:
            self.releaseDbAccessInt()
    
    # -------------------------------------------------------------------------
    def getLocalPaydesk(self):
        try:
            ret = self.dbQueryOne("SELECT * from paydesks WHERE remote=0")
            return ret                        
        except Exception as e:
            logger.error("Local paydesk query failed: %s"%(str(e)))
            self.__log__(traceback.format_exc())
            return None            
    
    # -------------------------------------------------------------------------
    def createRemotePaydesk(self, paydeskId, name, created,updated, syncIp, syncPort):
        try:
            ret =self.dbQueryOne("SELECT * from paydesks WHERE paydeskId='%s'"%paydeskId)
            if ret==None:
                stmt="INSERT INTO paydesks ('paydeskId', 'name', 'created', 'updated', 'syncIp', 'syncPort', 'remote') "
                stmt+="VALUES ('%s','%s','%s','%s','%s',%d,%d)"%(paydeskId, name, created, updated, syncIp, syncPort, 1)
                ret = self.dbWrite(stmt)
                return self.dbQueryOne("SELECT * from paydesks WHERE paydeskId='%s'"%paydeskId)
            else:
                if name!=ret[1] or syncIp!=ret[4] or syncPort!=ret[5] or updated!=ret[3]:
                    logger.info("Update Remote Paydesk %s, %s:%d"%(name,syncIp,syncPort))            
                    stmt="UPDATE paydesks SET 'name'='%s', 'updated'='%s', 'syncIp'='%s', 'syncPort'=%d where paydeskId='%s'"%(name,datetime.now(),syncIp,syncPort,paydeskId)
                    self.dbWrite(stmt)
        except Exception as e:
            self.__log__(traceback.format_exc())
            return None            
                
    # -------------------------------------------------------------------------
    def getRemotePaydesks(self):
        try:
            ret =self.dbQueryAll("SELECT * from paydesks WHERE remote=1")
            return ret                
        except Exception as e:
            self.__log__(traceback.format_exc())
            return None
        
    # -------------------------------------------------------------------------
    def removeRemotePaydesks(self):
        try:
            ret =self.dbWrite("DELETE * from paydesks WHERE remote=1")
            return ret                
        except Exception as e:
            self.__log__(traceback.format_exc())
            return None
        
    # -------------------------------------------------------------------------
    def getPaydesk(self, paydeskId):
        try:
            ret = self.dbQueryOne("SELECT * from paydesks WHERE paydeskId='%s'"%(paydeskId))
            return ret
        except Exception as e:            
            self.__log__(traceback.format_exc())
            return None        
    
    
    # -------------------------------------------------------------------------
    #
    #---- Cart
    #
    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    def createCartsTable(self):
        self.curs.execute('''CREATE TABLE IF NOT EXISTS carts ( cartId INTEGER not null,                                                               
                                                                   status TEXT,
                                                                   soldtime DATETIME,
                                                                   PRIMARY KEY (cartId) 
                                                                )''')
        print("CARTS: "+str(self.curs.fetchone()))
        
    # -------------------------------------------------------------------------
    def getCart(self, cartId ):
        return self.dbQueryOne("SELECT * from carts WHERE cartId=%d"%(cartId))                
    
    # -------------------------------------------------------------------------
    def getOpenCart(self, create=False):                
        ret=self.dbQueryOne("SELECT * from carts WHERE status='open' ORDER BY cartId DESC")
        if ret==None and create:
            ret=self.createCart()           
        return ret
            
    # -------------------------------------------------------------------------
    def getLastClosedCart(self):
        return self.dbQueryOne("SELECT * from carts WHERE status='closed' ORDER BY cartId DESC")                        
    
    # -------------------------------------------------------------------------
    def createCart(self):
        try:
            mxret = self.dbQueryOne("SELECT MAX(cartId) from carts")                        
            if mxret[0]==None:
                self.__log__("Start with first cart")
                cnt=0
            else:
                cnt=mxret[0]            
            cartId=cnt+1
            self.__log__("Create cart with number: %s"%str(cartId))
            self.dbWrite("INSERT INTO carts (cartId, status) VALUES (%d,'%s')"%(cartId, 'open'))              
            return self.getCart(cartId)
        except Exception as e:
            self.__log__(traceback.format_exc())
            raise RequestError(9999,"Fehler beim anlegen eines Warenkorbs",e)            
        
    # -------------------------------------------------------------------------
    def setCartStatus(self, cartStatus='closed'):
        cartId=-1
        cart=None
        try:
            cart = self.getOpenCart()        
            if cart==None:
                raise RequestError(9999,"Kein Warenkorb offen um in Status %s zu setzen"%str(cartStatus))
            cartId=cart[0]
            ret = self.dbWrite("UPDATE carts SET status='%s' WHERE cartId=%d "%(cartStatus, cartId))
        except RequestError as e:
            raise e
        except Exception as e:
            raise RequestError(9999,"Kann Warenkorb nicht in Status %s setzen"%str(cartStatus))
        return cartId, "Cart %s"%(str(cartStatus))
        
    # -------------------------------------------------------------------------
    #
    #---- Article
    #
    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    def createArticleTable(self):
        self.curs.execute('''CREATE TABLE IF NOT EXISTS articles ( barcode INTEGER,
                                                                       cartId INTEGER,
                                                                       pos INTEGER,                                                                   
                                                                       status TEXT,
                                                                       PRIMARY KEY (barcode, cartId)
                                                                )''')
        print("ARTICLES: "+str(self.curs.fetchone()))
    
    # -------------------------------------------------------------------------
    def addArticle(self, barcode, cartId, pos):
        stmt="SELECT barcode,bezeichnung,groesse,preis FROM items WHERE barcode=%s AND alt=0"%(barcode)
        print(stmt)
        self.curs.execute(stmt)
        items = self.curs.fetchall()
        if len(items)>1:
            raise RequestError(1030,"Verdaechtiger Artikel %s"%(str(barcode)))                
        elif len(items)==0:
            raise RequestError(1040,"Artikel %s nicht gefunden"%(str(barcode)))                
        else:
            item=items[0]        
        stmt="INSERT INTO articles ('barcode', 'cartId', 'pos', 'status')"
        stmt+= "VALUES (%d,'%s',%d, %d, %d, '%s')"%(barcode, cartId, pos, "placed")
        print(stmt)                
        self.curs.execute(stmt)
        self.conn.commit()
        msg="Artikel %d %s hinzugefuegt"%(barcode, item[1])
        return msg
        

    # -------------------------------------------------------------------------    
    def deleteLastArticle(self, cartId):        
        try:
            stmt="SELECT * FROM articles WHERE status='placed' and cartId=%s ORDER BY pos DESC LIMIT 1"%(cartId)            
            ret=self.dbQueryOne(stmt)
            if ret!=None:
                barcode=ret[0]                        
                stmt="SELECT barcode,bezeichnung FROM items WHERE barcode=%s and alt=0"%(str(barcode))
                delInfo=self.dbQueryOne(stmt)            
                stmt="DELETE FROM articles WHERE status='placed' and cartId=%s and barcode=%s"%(str(cartId),str(barcode))
                self.dbWrite(stmt)                
                msg="Loesche Artikel %s mit Barcode %s vom Warenkorb"%(delInfo[1], delInfo[0])
            else:
                msg="Kein Artikel im Warenkorb"                
        except:
            raise
        finally:
            pass         
        return cartId, msg
        
    # -------------------------------------------------------------------------
    def deleteArticles(self, cartId):        
        stmt="DELETE FROM articles WHERE cartId=%s"%(str(cartId))        
        print(stmt)
        self.curs.execute(stmt)
        self.conn.commit()
        msg="Artikel im Warenkorb geloescht"
        return cartId, msg                
    
    # -------------------------------------------------------------------------
    def setArticlesStatus(self, cartId, articleStatus="closed"):        
        stmt="UPDATE articles SET status='%s' WHERE cartId=%d "%(articleStatus, cartId)
        print(stmt)
        self.curs.execute(stmt)
        self.conn.commit()        
    
    
    
    
    
    
    # -------------------------------------------------------------------------
    def addToCart(self, barcode):
        msg=""
        
        items = self.dbQueryAll("SELECT barcode,bezeichnung,groesse,preis FROM items WHERE barcode=%s AND alt=0"%(barcode))            
        if len(items)>1:
            raise RequestError(1030,"Artikel  %s kommt mehrfach vor"%(str(barcode)))                
        elif len(items)==0:
            raise RequestError(1040,"Artikel %s nicht gefunden"%(str(barcode)))                
        else:
            item=items[0]
                
        ret = self.getOpenCart(create=True)
        cartId=ret[0]
        
        if cartId!=None:
            # check cart            
            ret = self.dbQueryAll("SELECT cartId, status FROM articles WHERE barcode=%s ORDER BY cartId DESC"%(barcode))           
            if ret!=None:
                if len(ret)==1:
                    artCartId=ret[0][0]
                    artStatus=ret[0][1]
                    if artCartId==cartId and artStatus in ["closed","sold","placed"]:
                        raise RequestError(1010,"Artikel %d bereits im Warenkorb"%barcode)
                    elif artCartId!=cartId and artStatus in ["closed","sold","placed"]:
                        raise RequestError(1020,"Artikel %d wurde bereits an dieser Kasse verkauft"%barcode)
                    elif artStatus not in ["deleted"]:
                        pass
                    else:
                        raise RequestError(1010,"Artikel %d konnte nicht im Warenkorb plaziert werden"%barcode)
                elif len(ret)>1:
                    raise RequestError(1010,"Artikel %d ist mehrfach (%d x) im Warenkorb vorhanden"%(barcode,len(ret)))
            
            # check sold items (all paydesks)
            ret = self.dbQueryAll("SELECT paydeskId, cartId, status FROM sold WHERE barcode=%s and status='sold'"%(barcode))
            if ret!=None:
                if len(ret)==1:
                    raise RequestError(1010,"Artikel %d wurde bereits verkauft"%(barcode))                    
              
            ret = self.dbQueryOne("SELECT MAX(pos) FROM articles WHERE cartId=%d"%cartId)
            pos=ret[0]
            if pos==None:
                pos=0
            else:
                pos=int(ret[0])+1
            
            stmt="INSERT INTO articles ('cartId', 'pos', 'barcode', 'status')"
            stmt+= "VALUES (%d,%d, %d,'%s')"%(cartId, pos, barcode, "placed")
            ret=self.dbWrite(stmt)                
            msg="Artikel %d, %s hinzugefuegt"%(barcode, item[1])
        return cartId, msg
    
    
    # -------------------------------------------------------------------------
    def closeCart(self):
        msg=""
        cartId=None
        ret=self.dbQueryOne("SELECT * from carts WHERE status='open' ORDER BY cartId DESC")
        if ret!=None:                 
            cartId=ret[0]        
            if cartId!=None:               
                ret = self.dbQueryOne("SELECT COUNT(*) FROM articles WHERE cartId=%s"%str(cartId))
                articleCnt=ret[0]
                if articleCnt==0:
                    msg="Warenkorb ist leer"
                else:            
                    self.setArticlesStatus(cartId=cartId, articleStatus='closed')
                    self.setCartStatus(cartStatus='closed')
                    msg="Warenkorb geschlossen"
            else:
                raise RequestError(9999,"Ungueltiger Warenkorb")
        else:
            raise RequestError(9999,"Kein Warenkorb gefunden")
        return cartId, msg
    
    # -------------------------------------------------------------------------
    def sellCart(self, cartId=None):
        msg=""   
        found=False        
        ret=self.dbQueryAll("SELECT * from carts WHERE status='closed' ORDER BY cartId DESC")
        if len(ret)==1 and cartId==None:
            found=True
            cartId = ret[0][0]            
        else:
            for cart in ret:
                if cartId==cart[0]:
                    found=True
                    break
        if found:            
            if cartId!=None:
                soldtime=str(datetime.now())            
                self.addSoldItems(cartId=cartId, soldtime=soldtime)
                stmtList=["UPDATE articles SET status='sold' WHERE cartId=%s "%(str(cartId)),
                          "UPDATE carts SET status='sold', soldtime='%s' WHERE cartId=%s "%(soldtime,str(cartId))]
                self.dbWriteMultiple(stmtList)
                msg="Warenkorb verkauft"            
            return cartId, msg
        else:
            if cartId!=None:
                raise RequestError(1101,"Kein Warenkorb geoeffent")
            else:
                raise RequestError(1102,"Ungueltiger Warenkorb")
        return cartId, msg
                
    #------------------------------- internal webserver response -------------------------------            
            
    # -------------------------------------------------------------------------
    def getCartItemsDetails(self, cartId):
        # find cart id
        ret=[]
        try:
            stmt="SELECT ta.pos, ti.barcode,ti.bezeichnung,ti.groesse,ti.preis from articles ta join items ti on ta.barcode=ti.barcode "
            stmt+="WHERE ta.cartId=%d ORDER BY ta.pos"%(cartId)
            #print(stmt)
            self.curs.execute(stmt)
            ret = self.curs.fetchall()  
            #print(ret)
        except:
            print(traceback.format_exc())      
        return ret    

    # -------------------------------------------------------------------------
    '''
    def setSold(self, cart):
        # write cart
        stmt="INSERT INTO cart ('cartId', 'paydeskId', 'soldtime') VALUES (%d,%d,'%s')"%(cart.id, cart.paydeskId, cart.soldtime)
        print(stmt)
        self.curs.execute(stmt)
        #write items        
        for key in cart.items:
            stmt="INSERT INTO sold ('barcode', 'cartId', 'paydeskId') VALUES ('%s',%d,%d)"%(cart.items[key].barcode, cart.id, cart.paydeskId)        
            print(stmt)
            self.curs.execute(stmt)                
        self.conn.commit()
        return
    '''
    
    # -------------------------------------------------------------------------
    def subscribePaydesk(self, remotePaydesk):
        paydesk=None        
        # find the paydesk
        stmt="SELECT * FROM paydesks WHERE 'paydeskId'=%s"+remotePaydesk.id
        #print(stmt)
        self.curs.execute(stmt)
        res = self.curs.fetchall()
        if len(res)==1:        
            paydesk = res[0]
                                
        if paydesk==None:
            stmt="INSERT INTO paydesks ('paydeskId', 'firstConnect', 'lastConnect', 'cartId', 'ip', 'port', 'portWebserver') "
            stmt+="VALUES (%d, %s,'%s, %d, %s, %d, %d')"%(remotePaydesk.id, str(datetime.now()), str(datetime.now()), remotePaydesk.cartId, remotePaydesk.port, remotePaydesk.portWebserver)
            #print(stmt)
            ret = self.curs.execute(stmt)
            print(ret)        
        else:       
            stmt="UPDATE ('paydeskId', 'lastConnect') FROM paydesks "
            stmt+="VALUES (%d,%s)"%(remotePaydesk.id, str(datetime.now()))        
            #print(stmt)
            ret = self.curs.execute(stmt)
            print(ret)
        self.conn.commit()
        return
    

    
    # -------------------------------------------------------------------------
    #
    #---- SOLD
    #
    # -------------------------------------------------------------------------
    
    def createSoldTable(self):
        self.curs.execute('''CREATE TABLE IF NOT EXISTS sold (  paydeskCnt INTEGER,
                                                                    paydeskId TEXT,
                                                                    cartId INTEGER,                                                                                                                                    
                                                                    barcode INTEGER,
                                                                    status TEXT,
                                                                    soldtime DATETIME,
                                                                    PRIMARY KEY (paydeskCnt, paydeskId)
                                                                )''')
        print("SOLD: "+str(self.curs.fetchone()))
        
    # -------------------------------------------------------------------------    
    def getSoldPaydeskCnt(self, paydeskId):        
        paydeskCnt = self.dbQueryOne("SELECT MAX(paydeskCnt) FROM sold WHERE paydeskId='%s'"%paydeskId)
        if paydeskCnt[0]==None:
            ret=0
        else:
            ret=paydeskCnt[0]        
        return ret
    
    # -------------------------------------------------------------------------
    def addSoldItems(self, cartId, soldtime=None):
        bcList=[]       
        ret=self.getLocalPaydesk()        
        paydeskId=ret[0]        
        paydeskCnt = self.getSoldPaydeskCnt(paydeskId)
        if soldtime==None:
            soldtime=datetime.now()
        #get the articles in the cart
        ret = self.dbQueryAll("SELECT * FROM articles WHERE cartId=%s"%(str(cartId)))
        if len(ret)>0:               
            stmtList=[]
            
            for article in ret:
                paydeskCnt+=1
                #barcode, cartId, pos, status
                barcode=article[0]
                bcList.append(str(soldtime)+","+str(barcode))
                try:
                    cartId=article[1]            
                    stmt="INSERT INTO sold (paydeskCnt, paydeskId, cartId, barcode, status, soldtime) "
                    stmt+="VALUES (%d,'%s',%d,%d,'%s','%s')"%(paydeskCnt, paydeskId, cartId, barcode, "sold",soldtime)
                    stmtList.append(stmt)
                except:
                    pass
            self.dbWriteMultiple(stmtList)
            try:
                if len(bcList)>0:
                    with open("sold.txt", "a") as f:
                        f.write('\n'.join(bcList))
            except Exception as e:
                print(str(e))
                pass
                
            
    # -------------------------------------------------------------------------
    def addRemoteSoldItems(self, itemsList):                       
        #get the articles in the cart        
        if len(itemsList)>0:               
            stmtList=[]
            for item in itemsList:
                paydeskCnt=item[0]
                paydeskId=item[1]                
                cartId=item[2]
                barcode=item[3]                            
                status=item[4]
                soldtime=item[5]
                stmt="INSERT INTO sold (paydeskCnt, paydeskId, cartId, barcode, status, soldtime) "
                stmt+="VALUES (%d,'%s',%d,%d,'%s','%s')"%(paydeskCnt, paydeskId, cartId, barcode, status, soldtime)
                stmtList.append(stmt)
            self.dbWriteMultiple(stmtList)    
            
    # -------------------------------------------------------------------------
    def getSoldItems(self, paydeskId, idx, cnt=1):
        stmt="SELECT * from sold WHERE paydeskId='%s' AND paydeskCnt>%d ORDER BY paydeskCnt ASC LIMIT %d"%(paydeskId,idx, cnt)
        ret =self.dbQueryAll(stmt)
        return ret
    
    # -------------------------------------------------------------------------
    '''
    def getSoldPaydesks(self):
        lpd=self.getLocalPaydesk()
        lpdId=lpd[0]
        stmt="SELECT DISTINCT paydeskId from sold WHERE paydeskId!=%s"%lpdID
        remotePaydesks =self.dbQueryAll(stmt)
        for pd in remotePaydesks:
            stmt="SELECT MAX(paydeskCnt) FROM sold WHERE paydeskId=%s"%pd[0]            
        return ret
    '''
   
    def getUserSold(self, userid):
        stmt="SELECT * FROM items join sold on items.barcode=sold.barcode WHERE items.nummer=%s"%userid
        ret=self.dbQueryAll(stmt)
        return ret
    
    
    def getUserNotSold(self, userid):
        stmt="SELECT * FROM items WHERE items.nummber=%s and items.barcode NOT IN (SELECT sold.barcode FROM sold)"
        ret=self.dbQueryAll(stmt)
        return ret
        

    
    # -------------------------------------------------------------------------
    #
    #---- Settings
    #
    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    def createSettingsTable(self):
        self.curs.execute('''CREATE TABLE IF NOT EXISTS settings (headline TEXT,
                                                                      enableWebSync BOOL,
                                                                      webSyncUrl TEXT,
                                                                      webSyncIp TEXT,
                                                                      webSyncRegisterId INTEGER,
                                                                      enableLocalSync BOOL,                                                                      
                                                                      localSyncIp TEXT,
                                                                      localSyncPort INTEGER,
                                                                      setSoldOnClose BOOL,
                                                                      enableRemoteSellPoint BOOL
                                                                )''')
        print("SETTINGS: "+str(self.curs.fetchone()))
            
    # -------------------------------------------------------------------------
    def getSettings(self):
        stmt = "SELECT * FROM settings ORDER BY rowid DESC LIMIT 1"
        ret =self.dbQueryOne(stmt)
        return ret
            
    # -------------------------------------------------------------------------
    def writeSettings(self, settings):
        try:        
            values =[]
            values.append("'"+str(settings.headline)+"'")
            values.append("'"+str(settings.enableWebSync)+"'")
            values.append("'"+str(settings.webSyncUrl)+"'")
            values.append("'"+str(settings.webSyncIp)+"'")
            values.append("'"+str(settings.webSyncRegisterId)+"'")
            values.append("'"+str(settings.enableLocalSync)+"'")
            values.append("'"+str(settings.localSyncIp)+"'")
            values.append("'"+str(settings.extWebserverPort)+"'")
            values.append("'"+str(settings.setSoldOnClose)+"'")      #setSoldOnClose
            values.append("'"+str(settings.enableRemoteSellPoint)+"'")
            #values.append("'"+str(settings.get("default",int(default)))+"'")
            stmt="INSERT INTO settings (headline, enableWebSync, webSyncUrl, webSyncIp,webSyncRegisterId, enableLocalSync, localSyncIp, localSyncPort, setSoldOnClose, enableRemoteSellPoint)"
            stmt+=" VALUES ("+','.join(values)+")"
            self.execute(stmt)            
            self.conn.commit()            
        except Exception as e:
            print(traceback.format_exc())            
            return False, "Fehler beim Schreiben der Einstellungen: %s"%(str(e))
        
        return True, "Einstellungen gespeichert"
    
    
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
                     

        
