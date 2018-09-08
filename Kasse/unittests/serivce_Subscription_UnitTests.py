'''
Created on Aug 26, 2018

@author: sedlmeier
'''
import unittest
import time

import unittests.db_testdata_creator as dbtd


import basarLogger
logger=basarLogger.initLogger()

import service_Subscription as subscription

class Test(unittest.TestCase):


    def setUp(self):
        dbtd.createLocalPaydesk()        


    def tearDown(self):
        pass
    
    def test_0001_receiveSubscription(self):
        stopListenerEvt = subscription.startSubscriberListener("192.168.2.255", 9892)
        time.sleep(5)
        stopUpdaterEvt = subscription.startSubscriberUpdater(9892)
        while(True):
            time.sleep(1)
        
        
                


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_0001_Start']
    unittest.main()