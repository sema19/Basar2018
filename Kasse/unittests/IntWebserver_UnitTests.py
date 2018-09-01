'''
Created on Aug 24, 2018

@author: sedlmeier
'''
import unittest

import IntWebserver
import time
import requests

import initLogger
logger=initLogger.initLogger()

class Test(unittest.TestCase):


    def setUp(self):
        # create database
        pass
        
    def tearDown(self):
        # tear down database
        pass
                


    def test_0001_StartStopWebserver(self):
        evt = IntWebserver.startIntWebserver(8082)
        time.sleep(10)
        evt.set()
        time.sleep(10)

        
        
    
    def test_0101_Request(self):
        evt = IntWebserver.startIntWebserver(8082)
        time.sleep(1)
        r=requests.get('http://127.0.0.1:8082/srvStatus')
        jsoninfo=r.json()
        logger.info(jsoninfo)
        evt.set()
        time.sleep(1)
        
    def test_0201_clear(self):
        pass
        
            
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()