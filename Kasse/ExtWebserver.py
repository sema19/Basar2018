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
from threading import Event
#from urllib.parse import urlparse
#from http.server import BaseHTTPRequestHandler, HTTPServer
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from LocalStorage import LocalStorage



extWebserverShutdownEvent = Event()
__intWebserverInst__ = None
def extWebserverShutdownObserver():
    global __extWebserverInst__
    extWebserverShutdownEvent.wait()
    __extWebserverInst__.shutdown()


# HTTPRequestHandler class
class requestHandler(BaseHTTPRequestHandler):
    
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
        print("GET: %s"%self.path)
        # ----------------------------- infos                                        
        if self.path=="/info.html":
            self.getOkTextHeader()
            with open("html/info.html",'r') as f:                
                message=f.read()
                self.wfile.write(message)
        # ----------------------------- provide jquery
        elif self.path=="/jquery.min.js":
            with open("html/jquery.min.js") as f:                       
                message=f.read()
                self.wfile.write(message)
        # ----------------------------- provide css files
        elif self.path=="/kasse.css":
            with open("html/kasse.css") as f:                       
                message=f.read()
                self.wfile.write(message)        
        # ----------------------------- provide jquery
        elif self.path=="/favicon.ico":
            self.send_response(200)                    
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

    
def runExtWebserver(ip, port):
    global __intWebserverInst__
    print('starting external server...') 
    # Server settings
    # Choose port 8080, for port 80, which is normally used for a http server, you need root access
    server_address = (ip,port)  #'192.168.2.106', 8080)
    __intWebserverInst__ = HTTPServer(server_address, requestHandler)
    print('running webserver...')
    __intWebserverInst__.serve_forever()
    print('shutdown webserver, closing thread...')
    