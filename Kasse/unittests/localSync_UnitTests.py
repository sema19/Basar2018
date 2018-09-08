'''
Created on Aug 25, 2018

@author: sedlmeier
'''
import unittest
import time
import threading

from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

import syncSender
import syncReceiver

import basarLogger
logger=basarLogger.initLogger()

from LocalStorage import LocalStorage
from LocalStorage import getDatabaseFilepath

import uuid
from datetime import datetime

class testRequestHandler(BaseHTTPRequestHandler):
    
    def getOkTextHeader(self):
        self.send_response(200,'OK')
        self.send_header('Content-type','text/html')
        self.end_headers()
        
    def getOkJsonHeader(self):
        self.send_response(200,'OK')
        self.send_header('Content-type', 'application/json')
        self.end_headers()    
            
    def do_GET(self):
        print("GET: %s"%self.path)
        # ----------------------------- infos                                        
        if self.path=="/info.html":
            self.getOkTextHeader()
        else:            
            self.send_response(404)    
            
    def do_POST(self):
        print("POST: %s"%self.path)
        if self.path=="/update":            
            self.getOkTextHeader()
        else:
            self.send_response(404)
                

class Test(unittest.TestCase):


    def setUp(self):
        pass

    def setUpDatabase(self):
        ls=LocalStorage(getDatabaseFilepath())
        paydeskName="Kasse123"        
        syncIp="127.0.0.1"
        syncPort=9798
        ls.setup(paydeskName,syncIp,syncPort)
        
    def prepareDatabase(self):
        ls=LocalStorage(getDatabaseFilepath())
        tnow=str(datetime.now())
        ret = ls.getRemotePaydesks()
        if ret==[] or ret==None:                
            paydeskId=uuid.uuid4()      
            ls.createRemotePaydesk(paydeskId,
                                   "TestRemoteKasse",
                                   tnow,
                                   tnow,
                                   "127.0.0.1",
                                   9798)
        
        

    def tearDown(self):
        pass


    def test_0001_StartStopSyncThread(self):
        self.setUpDatabase()
        self.prepareDatabase()
        syncSvrStopEvent = syncReceiver.startSyncWebserver("192.168.2.115", 9797)
        evt = syncSender.startLocalSync()
        time.sleep(5)
        syncSender.triggerLocalSync()
        time.sleep(30)
        syncSender.stopLocalSync()        
        syncSvrStopEvent.set()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()