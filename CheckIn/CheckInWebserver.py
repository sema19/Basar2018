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

import logging
logger = logging.getLogger('checkIn')

#from Cart import Cart

from CheckInDatabase import CheckInDatabase
#from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
#from settings import settingsInst

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
    
          
         
    # ----------------------------- HANDLE GET COMMANDS
    def do_GET(self):
        logger.info("LOCAL GET: %s"%self.path)
            
        # ----------------------------- provide webpages
        # ----------------------------- settings                                        
        if self.path=="/checkin.html":
            self.getOkTextHeader()
            with open("html/checkIn.html",'r') as f:                
                message=f.read()
                self.wfile.write(message.encode())
        
        # ----------------------------- provide jquery
        elif self.path=="/jquery.min.js":
            with open("html/jquery.min.js") as f:                       
                message=f.read()
                self.wfile.write(message.encode())
        # ----------------------------- provide css files
        elif self.path=="/checkin.css":
            with open("html/kasse.css") as f:                       
                message=f.read()
                self.wfile.write(message.encode())        
        # ----------------------------- provide css files
        elif self.path=="/checkin.js":
            with open("html/checkIn.js") as f:                       
                message=f.read()
                self.wfile.write(message.encode())
        # ----------------------------- provide jquery
        elif self.path=="/favicon.ico":
            with open("html/icon.png") as f:                       
                message=f.read()
                self.wfile.write(message)
        else:            
            self.send_response(404)
        return
 
            
    # ----------------------------- HANDLE POST COMMANDS            
    def do_POST(self):
        #print('-'*30+'\n'+"LOCAL POST: %s"%self.path)
        logger.info("LOCAL POST: %s"%self.path)
        
        # ------------------------------------------------------
        if self.path=="/checkInUser":
            try:                
                self.getOkJsonHeader()
                rawdata = self.getRawData()
                jsonData=json.loads(rawdata)
                ls = CheckInDatabase()                                              
                bc = str(jsonData["barcode"])
                user_nr = bc[0:3]                
                userData ,msgUsr = ls.getUserInfo(user_nr)
                if userData==None:
                    raise(Exception("userDataNone"))                
                userItemsRaw ,msgItem = ls.getUserItems(userData[0])
                if userItemsRaw==None:
                    userItemsRaw=[]
                ret=ls.addCheckIn(userData[0])
                userItems=[]
                for usit in userItemsRaw:
                    userItems.append({"pos":usit[2],"bc":usit[3],"txt":usit[4],"size":usit[5],"price":usit[6]})
                jsonData=json.dumps({"userInfo":{"user":userData, "items":userItems},"msg":"User checked In","error":0})                        
                self.wfile.write(jsonData.encode())      
            except Exception as e:                
                logger.error(str(e))                             
                jsonData=json.dumps({"userInfo":{},"msg":str(e),"error":1})                        
                self.wfile.write(jsonData.encode())
            finally:
                try:
                    del ls
                except: 
                    logger.error(str(e))                  
                   
        # ------------------------------------------------------
        elif self.path=="/initiate_shutdown":
            logger.info("Initiate Shutdown !!!!!")
            stopAllRequested.set()
            jsonData=json.dumps({"action":"shutdown"})                        
            self.wfile.write(jsonData.encode())
                
        # ----------------------------- UNKOWN POST COMMAND                                   
        else:                       
            self.send_response(404)        
        return

__intWebserverInst__=None
    
def startWebserver(port):
    # start webserver
    logger.info("Start Internal Webserver")    
    intWebsrvThread = threading.Thread(name="intWebsvr",target=runWebserver, args=[port])
    intWebsrvThread.start()
     
    logger.info('create shutdown event')
    shutdownEvent = Event()
    
    logger.info('start observer')
    intWebsrvShutdownObserver = threading.Thread(name="intWebsvrShutdown",target=runWebserverShutdownObserver, args=[shutdownEvent])
    intWebsrvShutdownObserver.start()
    
    return shutdownEvent

def runWebserverShutdownObserver(shutdownEvent):
    global __checkInWebserverInst__
    shutdownEvent.wait()
    __checkInWebserverInst__.shutdown()
    logger.info('checkInWebserverObserver shut down')
             
# ------------------------------------------------------
def runWebserver(port):
    global __checkInWebserverInst__
    logger.info('starting local server...')
    server_address = ('127.0.0.1', port)    #8082)
    __checkInWebserverInst__ = HTTPServer(server_address, localRequestHandler)
    logger.info('running local webserver...')
    __checkInWebserverInst__.serve_forever()
    logger.info('checkInWebserver shut down')

    