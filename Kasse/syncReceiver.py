'''
Created on Aug 26, 2018

@author: sedlmeier
'''

import json
import threading
from LocalStorage import LocalStorage
import traceback

import webpageBuilder as wp
import codecs


from threading import Event
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

from syncLogger import synclogger as logger


# HTTPRequestHandler class
class syncRequestHandler(BaseHTTPRequestHandler):
    
    def log_message(self, *args):        
        pass
        
    def getOkJsonHeader(self):
        self.send_response(200,'OK')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
            
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
            with codecs.open("html/jquery.min.js",'r') as f:                       
                message=f.read()
                self.wfile.write(message.encode('utf-8'))
        # ----------------------------- provide css files
        elif self.path=="/status.css":
            with codecs.open("html/status.css") as f:                       
                message=f.read()
                self.wfile.write(message.encode('utf-8'))
        # ----------------------------- provide java script
        elif self.path=="/status.js":
            with codecs.open("html/kasse.js") as f:                       
                message=f.read()
                self.wfile.write(message.encode('utf-8'))        
        # ----------------------------- provide jquery
        elif self.path=="/favicon.ico":
            self.send_response(200)
            
        elif self.path=="/status.json":
            self.getOkJsonHeader()
            ls=LocalStorage()
            statusDict=ls.getStatus()
            jsonData=json.dumps(statusDict)
            self.wfile.write(jsonData.encode('utf-8'))
        else:          
            self.send_response(404)
        return
    
    def getRawData(self):
        len=int(self.headers['Content-Length'])
        retraw= self.rfile.read(len).decode()        
        ret =str(retraw)                
        return ret    
            
    def do_POST(self):
        #logger.debug("POST: %s"%self.path)
        if self.path=="/sync":
            jsonStr=""
            try:
                self.getOkJsonHeader()
                jsonStr = self.getRawData()                
                jsonDataIn=json.loads(jsonStr)                
                paydeskId=jsonDataIn['paydeskId']
                idx=jsonDataIn['idx']
                cnt=jsonDataIn['cnt']
                if 'source' in jsonDataIn:
                    sourcePaydeskId = jsonDataIn['source']
                else:
                    sourcePaydeskId=paydeskId
                ls=LocalStorage()
                # add sync request to sync db
                ls.writeSyncRequestReceived(sourcePaydeskId,idx)
                paydeskIdRef = ls.getLocalPaydesk()[0]                
                items=ls.getSoldItems(paydeskId, idx, cnt)
                logger.debug("Sync sold items: %s",items)
                jsonData=json.dumps(items)
                self.wfile.write(jsonData.encode('utf-8'))
            except json.JSONDecodeError as e:
                logger.error("Invalid json string: %s causes error: %s"%(str(jsonStr),str(e)))
                self.send_response(404)
            except Exception as e:
                print("Error: %s"%str(e))
                print(traceback.format_exc())
                self.send_response(404)
        else:
            self.send_response(404)     
        return

__syncServer__ = None
stopEvent = threading.Event()

def startSyncWebserver(ip,port):
    stopEvent.clear()
    syncWebserverThread = threading.Thread(name="syncWebserver", target=runSyncWebserver, args=[ip,port])
    syncWebserverThread.start()
    return stopEvent
    
def syncWebserverObserver():
    stopEvent.wait()
    __syncServer__.shutdown()
    
def runSyncWebserver(ip, port):    
    logger.info('start sync server at %s:%d...'%(ip,port))     
    # Choose port 8080, for port 80, which is normally used for a http server, you need root access    
    __syncServer__ = HTTPServer((ip,port), syncRequestHandler)
    logger.info('running sync webserver...')
    __syncServer__.serve_forever()
    logger.info('shutdown sync webserver, closing thread...')