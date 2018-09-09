'''
Created on 07.08.2017

@author: Laptop8460
'''

#import traceback
import os
import json
import threading
from threading import Event
#import inspect
import codecs

import logging
logger = logging.getLogger('log')

#from Cart import Cart
from service_Subscription import startSubscriptionUpdateEvent
from service_Subscription import publishEvent
from syncSender import localSyncEvent
from LocalStorage import LocalStorage
from LocalStorage import debugEventLocalStorage
from webDownload import startWebDownload

#from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
#from settings import settingsInst
from Errors import RequestError

import settings

stopAllRequested=Event()



# HTTPRequestHandler class
class localRequestHandler(BaseHTTPRequestHandler): #BaseHTTPRequestHandler):
    
    # ----------------------------- 
    def __log__(self, *args, **kwargs):
        logger.info(args[0])        
        
        
    # ----------------------------- 
    def __error__(self, *args, **kwargs):
        logger.error(args[0])        
    
    # ----------------------------- 
    def getOkTextHeader(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        
    # ----------------------------- 
    def getOkJsonHeader(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    # ----------------------------- 
    def getRawData(self):
        len=int(self.headers['Content-Length'])
        retraw= self.rfile.read(len)        
        ret =str(retraw.decode())                
        return ret
    
    # ----------------------------- 
    def getCartId(self, ls):
        # get the latest open cart
        cart = ls.getOpenCart()        
        if cart==None:             
            cart = ls.createCart()
        cartId=cart[0]
        return cartId
    
    # ----------------------------- 
    def getCartResponse(self, ls, cartId=None, status='open', msg="", error=0):
        '''central response to most of the actions
        '''        
        try:
            if cartId==None:
                cart = ls.getOpenCart()
                if cart==None:
                    retDict={"id":-1, "items":[], 'status':'undef', 'msg':'no open cart', 'error':error}
                    jsonData=json.dumps(retDict)
                    return jsonData                
                else:
                    cartId=cart[0]
            if cartId!=None:            
                ret = ls.getCartItemsDetails(cartId)
                itemList=[]
                for a in ret:
                    itemList.append({'bc':a[1],'txt':a[2],'size':a[3],'price':a[4]})
                retDict={"id":cartId, "items":itemList, 'status':status, 'msg':msg, 'error':error}
        except Exception as e:
            if error==0:
                error=777            
            retDict={'msg':str(e), 'error':error}
        finally:                        
            jsonData=json.dumps(retDict)
        return jsonData       
         
    # ----------------------------- HANDLE GET COMMANDS
    def do_GET(self):
        logger.debug("LOCAL GET: %s"%self.path)

        # ------------------------------------------------------
        if self.path=="/srvStatus":
            try:
                self.getOkJsonHeader()
                jsonData={"status":"alive"}                 
                self.wfile.write(json.dumps(jsonData).encode('utf-8'))
            except Exception as e:
                logger.error(str(e))
                self.wfile.write(json.dumps({"msg":str(e),"err":1}).encode('utf-8'))
            
        # ----------------------------- provide webpages
        # ----------------------------- settings                                        
        elif self.path=="/checkIn.html":
            self.getOkTextHeader()
            with codecs.open("html/checkIn.html",'r','utf-8') as f:                
                message=f.read()
                self.wfile.write(message.encode('utf-8'))
        # ----------------------------- transfer
        elif self.path=="/transfer.html":            
            self.getOkTextHeader()
            with codecs.open("html/transfer.html",'r','utf-8') as f:
                message=f.read()
                self.wfile.write(message.encode('utf-8'))
        # ----------------------------- kasse
        elif self.path=="/kasse.html":            
            startSubscriptionUpdateEvent.set()
            self.getOkTextHeader()
            with codecs.open("html/kasse.html",'r','utf-8') as f:
                message=f.read()
                self.wfile.write(message.encode('utf-8'))
        # ----------------------------- provide jquery
        elif self.path=="/jquery.min.js":
            with codecs.open("html/jquery.min.js",'r') as f:                       
                message=f.read()
                self.wfile.write(message.encode('utf-8'))
        # ----------------------------- provide css files
        elif self.path=="/kasse.css":
            with codecs.open("html/kasse.css",'r','utf-8') as f:                       
                message=f.read()
                self.wfile.write(message.encode('utf-8'))
        # ----------------------------- provide css files
        elif self.path=="/kasse.js":
            with codecs.open("html/kasse.js",'r','utf-8') as f:                       
                message=f.read()
            self.wfile.write(message.encode('utf-8'))                
        # ----------------------------- provide jquery
        elif self.path=="/favicon.ico":
            with codecs.open("html/icon.png","r") as f:                       
                message=f.read()
                self.wfile.write(message)
        else:            
            logger.error("INVALID PATH LOCAL GET: %s"%self.path)
            self.send_response(404)
        return
 
            
    # ----------------------------- HANDLE POST COMMANDS            
    def do_POST(self):
        #print('-'*30+'\n'+"LOCAL POST: %s"%self.path)
        logger.info("LOCAL POST: %s"%self.path)
                
        # ------------------------------------------------------
        if self.path=="/barcode":
            try:                
                self.getOkJsonHeader()
                ls = LocalStorage()
                rawdata = self.getRawData()
                jsonData=json.loads(rawdata)                
                cart=ls.getOpenCart(create=True)
                openCartId=int(cart[0])                                                
                bc = str(jsonData["bc"])
                logger.debug("BARCODE RECEIVED: "+bc)
                if (bc=="99914158"):
                    cartId, msg = ls.closeCart()
                    #TODO: check for the sell at close flag                    
                    ls.sellCart(cartId)                    
                    jsonData=self.getCartResponse(ls, cartId, 'closed', msg=msg)
                    localSyncEvent.set()                   
                elif (bc=="99917159"):                # delete last item
                    cartId, msg = ls.deleteLastArticle(openCartId)                 
                    jsonData=self.getCartResponse(ls, cartId, 'open', msg=msg)
                elif (bc=="99917753"):                # delete cart
                    cartId, msg = ls.deleteArticles(openCartId)                    
                    jsonData=self.getCartResponse(ls, cartId, 'open', msg=msg)
                else:                                                                        
                    cartId, msg = ls.addToCart(int(bc))
                    jsonData=self.getCartResponse(ls, cartId, 'open', msg=msg)                        
                self.wfile.write(jsonData.encode('utf-8'))
            except RequestError as e:
                logger.error(str(e))            
                jsonData=self.getCartResponse(ls, openCartId, 'open', msg=e.msg, error=e.err)
                self.wfile.write(jsonData.encode('utf-8'))
            except Exception as e:
                logger.error(str(e))                               
                jsonData=self.getCartResponse(ls, openCartId, 'open', msg=str(e), error=1)
                self.wfile.write(jsonData.encode('utf-8'))
            finally:
                try:
                    del ls
                except: 
                    logger.error(str(e))                 

        
        # ------------------------------------------------------
        elif self.path=="/checkInUser":
            try:                
                self.getOkJsonHeader()
                rawdata = self.getRawData()
                jsonData=json.loads(rawdata)
                ls = LocalStorage()                                              
                bc = str(jsonData["barcode"])
                user_nr = bc[0:3]                
                userData ,msgUsr = ls.getUserInfo(user_nr)
                if userData==None:
                    raise(msgUsr)                
                userItemsRaw ,msgItem = ls.getUserItems(userData[0])
                if userItemsRaw==None:
                    userItemsRaw=[]
                ret=ls.addCheckIn(userData[0])
                ret = LocalStorage.getCheckInSyncInfo()
                userItems=[]
                for usit in userItemsRaw:
                    userItems.append({"pos":usit[2],"bc":usit[3],"txt":usit[4],"size":usit[5],"price":usit[6]})
                jsonData=json.dumps({"userInfo":{"user":userData, "items":userItems},"msg":"User checked In","error":0})                        
                self.wfile.write(jsonData.encode())                
            except RequestError as e:
                logger.error(str(e))            
                jsonData=self.getCartResponse(ls, openCartId, 'open', msg=e.msg, error=e.err)
                self.wfile.write(jsonData.encode('utf-8'))      
            except Exception as e:                
                logger.error(str(e))                             
                jsonData=json.dumps({"userInfo":{},"msg":str(e),"error":1})                        
                self.wfile.write(jsonData.encode('utf-8'))
            finally:
                try:
                    del ls
                except: 
                    logger.error(str(e))                  
                
                
        # ------------------------------------------------------
        elif self.path=="/startDownload":
            logger.info("Start Download")
            myset=settings.Settings()
            webid = myset.webSyncRegisterId
            url = myset.webSyncUrl
            ip = myset.webSyncIp
            startWebDownload(url,ip,webid)
            jsonData=json.dumps({"action":"runWebDownload"})                        
            self.wfile.write(jsonData.encode('utf-8'))
            
        # ------------------------------------------------------
        elif self.path=="/initiate_shutdown":
            logger.info("Initiate Shutdown !!!!!")
            stopAllRequested.set()
            jsonData=json.dumps({"action":"shutdown"})                        
            self.wfile.write(jsonData.encode())
                
                
        # ------------------------------------------------------
        elif self.path=="/removeRemotePaydesks":
            try:
                ls = LocalStorage()
                ret = ls.removeRemotePaydesks()
                jsonData=json.dumps({"action":"removeRemotePaydesks"})                        
                self.wfile.write(jsonData.encode('utf-8'))                
            except Exception as e:
                logger.error(str(e))
                jsonData=json.dumps({"action":"removeRemotePaydesks", "msg":str(e), "error":1})                        
                self.wfile.write(jsonData.encode('utf-8'))                             
            finally:                
                try:
                    del ls
                except: 
                    logger.error("Delete ls error") 
                
                
                        
        # ------------------------------------------------------
        elif self.path=="/getItemsUsersStatus":
            print("getUserItemsStatus")
            try:
                ls=LocalStorage()            
                itemsStats = ls.getItemsStats()
                usersStats = ls.getUsersStats()                
                jsonData=json.dumps({"items":itemsStats,"users":usersStats})                
                self.getOkJsonHeader()                
                self.wfile.write(jsonData.encode('utf-8'))                
            except Exception as e:
                logger.error(str(e))
                self.wfile.write(json.dumps({"msg":str(e),"err":1}).encode('utf-8'))                                
            finally:
                try:
                    del ls
                except:
                    logger.error("Delete ls error")    
            
        # ------------------------------------------------------
        elif self.path=="/update":
            try:
                self.getOkJsonHeader()
                ls = LocalStorage()                                
                cartId = self.getCartId(ls)
                jsonData=self.getCartResponse(ls, cartId)
                self.wfile.write(jsonData.encode())
            except RequestError as e:
                logger.error(str(e)) 
                self.wfile.write(json.dumps({"msg":e.msg,"err":e.err}).encode()) 
            except Exception as e:
                logger.error(str(e))
                self.wfile.write(json.dumps({"msg":str(e),"err":1}).encode()) 
            finally:                
                try:
                    del ls
                except: 
                    logger.error("Error del ls")

                
                
                
        # ------------------------------------------------------
        elif self.path=="/close":
            try:
                self.getOkJsonHeader()
                ls = LocalStorage()  
                cart=ls.getOpenCart(create=True)
                cartId=int(cart[0])
                logger.info("CLOSE: Cart ID: %s"%(str(cartId)))                    
                cartId, msg = ls.closeCart()                  
                ls.sellCart(cartId)
                jsonData=self.getCartResponse(ls, cartId, 'closed', msg=msg, error=0)
                self.wfile.write(jsonData.encode('utf-8'))
            except RequestError as e:
                logger.error(str(e))
                jsonData=self.getCartResponse(ls, cartId, 'closed', msg=e.msg, error=e.err)                 
                self.wfile.write(jsonData.encode('utf-8'))                 
            except Exception as e:
                logger.error(str(e))
                jsonData=self.getCartResponse(ls, cartId, 'closed', msg=str(e), error=1)
                self.wfile.write(jsonData.encode('utf-8'))                
            finally:                
                try:
                    del ls
                except: print("Error del ls")
                
        # ------------------------------------------------------
        elif self.path=="/sold":
            err=0
            msg=""
            try:
                ls = LocalStorage()
                self.getOkJsonHeader()
                cart=ls.getOpenCart(create=True)
                cartId=int(cart[0]) 
                logger.info("CLOSE: Cart ID: %s"%(str(cartId)))
                cartId, msg = ls.closeCart()
                #TODO: check for the sell at close flag                    
                ls.sellCart(cartId)
                jsonData=self.getCartResponse(ls, cartId, 'closed', msg=msg, error=err)                 
                self.wfile.write(jsonData.encode('utf-8'))
                localSyncEvent.set()
            except RequestError as e:
                logger.error(str(e))
                jsonData=self.getCartResponse(ls, cartId, 'closed', msg=e.msg, error=e.err)                 
                self.wfile.write(jsonData.encode('utf-8'))
            except Exception as e:
                logger.error(str(e))
                jsonData=self.getCartResponse(ls, cartId, 'closed', msg=str(e), error=1)                 
                self.wfile.write(jsonData.encode('utf-8'))                
            finally:                
                try:
                    del ls
                except: 
                    logger.error("Error del ls")
                
        # ------------------------------------------------------
        elif self.path=="/delLast":
            err=0
            msg=""
            try:                
                self.getOkJsonHeader()
                ls=LocalStorage()
                cart=ls.getOpenCart(create=True)
                cartId=int(cart[0])                                                
                cartId, msg = ls.deleteLastArticle(cartId)                 
                jsonData=self.getCartResponse(ls, cartId, 'open', msg=msg, error=err)
                self.wfile.write(jsonData.encode('utf-8'))
            except RequestError as e:
                logger.error("Error: %s"%str(e))
                jsonData=self.getCartResponse(ls, cartId, 'open', msg=e.msg, error=e.err)                 
                self.wfile.write(jsonData.encode('utf-8'))
            except Exception as e:
                logger.error(str(e))
                jsonData=self.getCartResponse(ls, cartId, 'open', msg=str(e), error=1)
                self.wfile.write(jsonData.encode('utf-8'))
            finally:
                try:    
                    del ls
                except: 
                    logger.error("Error del ls")
        
        # ------------------------------------------------------
        elif self.path=="/delCart":
            err=0
            msg=""
            try:
                self.getOkJsonHeader()
                ls=LocalStorage()
                cart=ls.getOpenCart(create=True)
                cartId=int(cart[0])              
                cartId, msg = ls.deleteArticles(cartId)                    
                jsonData=self.getCartResponse(ls, cartId, 'open', msg=msg, error=err)                
                self.wfile.write(jsonData.encode('utf-8'))
            except RequestError as e:
                logger.error(str(e))
                jsonData=self.getCartResponse(ls, cartId, 'open', msg=e.msg, error=e.err)                 
                self.wfile.write(jsonData.encode('utf-8'))
            except Exception as e:
                logger.error(str(e))
                jsonData=self.getCartResponse(ls, cartId, 'open', msg=msg, error=1)                
                self.wfile.write(jsonData.encode('utf-8'))                
            finally:
                try:    
                    del ls
                except: 
                    logger.error("Error del ls")
                
        # ----------------------------- UNKOWN POST COMMAND                                   
        else:                       
            self.send_response(404)        
        return

__intWebserverInst__=None
    
def startIntWebserver(port):
    # start webserver
    logger.info("Start Internal Webserver")    
    intWebsrvThread = threading.Thread(name="intWebsvr",target=runIntWebserver, args=[port])
    intWebsrvThread.start()
     
    logger.info('create shutdown event')
    shutdownEvent = Event()
    
    logger.info('start observer')
    intWebsrvShutdownObserver = threading.Thread(name="intWebsvrShutdown",target=runIntWebserverShutdownObserver, args=[shutdownEvent])
    intWebsrvShutdownObserver.start()
    
    return shutdownEvent

def runIntWebserverShutdownObserver(shutdownEvent):
    global __intWebserverInst__
    shutdownEvent.wait()
    __intWebserverInst__.shutdown()
    logger.info('intWebserverObserver shut down')
             
# ------------------------------------------------------
def runIntWebserver(port):
    global __intWebserverInst__
    logger.info('starting local server...')
    server_address = ('127.0.0.1', port)    #8082)
    __intWebserverInst__ = HTTPServer(server_address, localRequestHandler)
    logger.info('running local webserver...')
    __intWebserverInst__.serve_forever()
    logger.info('local webserver shut down')

    