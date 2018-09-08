'''
Created on 07.08.2017

@author: Laptop8460
'''
'''
Created on 15.07.2017

@author: Laptop8460
'''

import traceback
import os
import json
import threading
from threading import Event
#from urllib.parse import urlparse
#from http.server import BaseHTTPRequestHandler, HTTPServer
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from LocalStorage import LocalStorage

from basarLogger import logger
import webpageBuilder as wp



# HTTPRequestHandler class
class extRequestHandler(BaseHTTPRequestHandler):
    
    def getOkTextHeader(self):
        self.send_response(200,'OK')
        self.send_header('Content-type','text/html')
        self.end_headers()
        
    def getOkJsonHeader(self):
        self.send_response(200,'OK')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def getRawData(self):
        len=int(self.headers['Content-Length'])
        retraw= self.rfile.read(len)        
        ret =str(retraw)                
        return ret
            
    def do_GET(self):
        logger.debug("GET: %s"%self.path)
        
        # ----------------------------- infos                                        
        if self.path=="/status.html":
            self.getOkTextHeader()
            pg =wp.html(wp.head("status","",""),
                        wp.body(wp.header("Status"),
                                "<p>To Be Done</p>"))
            
            self.wfile.write(pg.encode())
        # ----------------------------- provide jquery
        elif self.path=="/jquery.min.js":
            with open("html/jquery.min.js") as f:                       
                message=f.read()
                self.wfile.write(message.encode())
        # ----------------------------- provide css files
        elif self.path=="/status.css":
            with open("html/status.css") as f:                       
                message=f.read()
                self.wfile.write(message.encode())
        # ----------------------------- provide java script
        elif self.path=="/status.js":
            with open("html/kasse.js") as f:                       
                message=f.read()
                self.wfile.write(message.encode())        
        # ----------------------------- provide jquery
        elif self.path=="/favicon.ico":
            self.send_response(200)
            
        elif self.path=="/status.json":
            self.getOkJsonHeader()
            ls=LocalStorage()
            statusDict=ls.getStatus()
            jsonData=json.dumps(statusDict)
            self.wfile.write(jsonData.encode())                    
        else:            
            self.send_response(404)
        return 
    
       
            
    def do_POST(self):
        print("POST: %s"%self.path)
        if self.path=="/update":
            try:
                self.getOkJsonHeader()
                ls = LocalStorage()
                cartId = self.getCartId(ls)
                print("UPDATE: Cart ID: %d"%(cartId))
                jsonData=self.getCartResponse(ls, cartId)
                ls.disconnect()        
                self.wfile.write(jsonData)
            except Exception as e:
                print("Error: %s"%str(e))
                print(traceback.format_exc())
                self.send_response(404)
                
                
        if self.path=="/status":
            try:
                self.getOkJsonHeader()                
                jsonDataIn=json.loads(self.getRawData())
                paydeskId=jsonDataIn['paydeskId']
                idx=jsonDataIn['idx']
                cnt=jsonDataIn['cnt']
                ls=LocalStorage()
                paydeskIdRef = ls.getLocalPaydesk()[0]                
                items=ls.getSoldItems(paydeskId, idx, cnt)
                jsonData=json.dumps(items)
                self.wfile.write(jsonData)
            except Exception as e:
                print("Error: %s"%str(e))
                print(traceback.format_exc())
                self.send_response(404)
        else:
            self.send_response(404)     
        return
        
        if self.path=="/sync":
            try:
                self.getOkJsonHeader()                
                jsonDataIn=json.loads(self.getRawData())
                paydeskId=jsonDataIn['paydeskId']
                idx=jsonDataIn['idx']
                cnt=jsonDataIn['cnt']
                ls=LocalStorage()
                paydeskIdRef = ls.getLocalPaydesk()[0]                
                items=ls.getSoldItems(paydeskId, idx, cnt)
                jsonData=json.dumps(items)
                self.wfile.write(jsonData)
            except Exception as e:
                print("Error: %s"%str(e))
                print(traceback.format_exc())
                self.send_response(404)
        else:
            self.send_response(404)     
        return

___extWebserverInst__=None
    
def startExtWebserver(ip, port):
    # start webserver
    logger.info("Start External Webserver on %s:%s"%(ip,str(port)))    
    extWebsrvThread = threading.Thread(name="extWebsvr",target=runExtWebserver, args=[ip, port])
    extWebsrvThread.start()
     
    logger.info('create shutdown event')
    shutdownEvent = Event()
    
    logger.info('start observer')
    extWebsrvShutdownObserver = threading.Thread(name="extWebsvrShutdown",target=runExtWebserverShutdownObserver, args=[shutdownEvent])
    extWebsrvShutdownObserver.start()
    
    return shutdownEvent

def runExtWebserverShutdownObserver(shutdownEvent):
    global __extWebserverInst__
    shutdownEvent.wait()
    __extWebserverInst__.shutdown()
    logger.info('extWebserverObserver shut down')
             
# ------------------------------------------------------
def runExtWebserver(ip, port):
    global __extWebserverInst__
    logger.info('starting local server...')
    server_address = (ip, port)    #8082)
    __extWebserverInst__ = HTTPServer(server_address, extRequestHandler)
    logger.info('running local webserver...')
    __extWebserverInst__.serve_forever()
    logger.info('local webserver shut down')