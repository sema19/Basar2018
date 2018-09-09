'''
Created on 06.09.2017

@author: Laptop8460
'''
import subprocess
import re
from LocalStorage import LocalStorage
import platform
import os

import configparser

class DB_POS:
    HEADLINE=0
    WEB_SYNC_EN=1
    WEB_SYNC_URL=2
    WEB_SYNC_IP=3
    WEB_SYNC_REG_ID=4
    LOCAL_SYNC_EN=5
    LOCAL_SYNC_IP=6
    LOCAL_SYNC_PORT=7
    SET_SOLD_ON_CLOSE=8
    ENABLE_REMOTE_SALE_POINT=9

__broadcastPort__=7888
__intWebserverPort__=8082
__extWebserverPort__=8080
__paydeskName__="Kasse"
__webSyncUrl__="https://K2:54746688@int.basar-teugn.de/kasse"
__webSyncRegisterId__="12"

class Settings(object):
    '''
    classdocs
    '''
    def __init__(self):
        
        self.cfg = configparser.ConfigParser()
        self.cfg.read('kasse.cfg')
        
        
        self.op_system=platform.system()
        self.intWebserverIp = self.cfg.get("IntWebserver","AdapterIp",fallback="127.0.0.1")        
        self.intWebserverPort=self.cfg.getint("IntWebserver","Port",fallback=__intWebserverPort__)
        
        self.startpage=self.cfg.get("UserInterface","Startpage",fallback="Kasse.html")
        self.paydeskName=self.cfg.get("UserInterface","PaydeskName",fallback=__paydeskName__)
        self.headline=self.cfg.get("UserInterface","Headline",fallback="Basar")
        
        
        self.enableLocalSync=self.cfg.getboolean("LocalSync","Enabled",fallback=True)
        self.localSyncIp = self.cfg.get("LocalSync","AdapterIp",fallback="auto")
        if self.localSyncIp=="auto":
            self.localSyncIp=self.getEthAdapterIP()
        self.localSyncPort= self.cfg.getint("LocalSync","Port",fallback="8080")
        self.broadcastIp=self.cfg.get("LocalSync","BroadcastIp",fallback="255.255.255.255")   
        self.broadcastPort=self.cfg.getint("LocalSync","BroadcastPort",fallback=__broadcastPort__)
        self.networkInfo=None
                
        self.enableWebSync=self.cfg.get("WebSync","Enabled",fallback="off")
        self.webSyncUrl=self.cfg.get("WebSync","Url",fallback=__webSyncUrl__)
        self.webSyncIp = self.cfg.get("WebSync","AdapterIp",fallback="auto")
        if self.webSyncIp=="auto":
            self.webSyncIp=self.getEthAdapterIP()        
        self.webSyncRegisterId=self.cfg.get("WebSync","RegisterId",fallback=__webSyncRegisterId__)
        
        self.extWebserverEnabled = self.cfg.getboolean("ExtWebserver","Enabled",fallback=False)
        self.extWebserverIp = self.cfg.get("ExtWebserver","AdapterIp",fallback="auto")
        if self.extWebserverIp=="auto":
            self.extWebserverIp=self.getEthAdapterIP()
        self.extWebserverPort=self.cfg.getint("ExtWebserver","Port",fallback=__intWebserverPort__)
                
        self.setSoldOnClose=self.cfg.getboolean("Advanced","SoldOnClose",fallback=True)        
        self.enableRemoteSellPoint=self.cfg.getboolean("Advanced","EnableRemoteSellPoint",fallback=False)
                        
        self.dbSettings=None
            
    def getHeadline(self):
        return self.headline        
        
    def updateNetworkInfo(self):
        raise "No network info"
        #self.networkInfo=self._getNetworkInfo()
        
    def getEthAdapterIP(self):        
        if self.networkInfo==None:
            self.updateNetworkInfo()
        for adapt in self.networkInfo.keys():
            return self.networkInfo[adapt]["ip"]
        return None
    
    def getIntWebserverPort(self):
        return int(self.intWebserverPort)
    
    def getExtWebserverPort(self):
        return int(self.extWebserverPort)
    
    def getBroadcastPort(self):
        return self.broadcastPort
    
    def getSyncIp(self):
        return self.localSyncIp
    
    def getPaydeskName(self):
        return self.paydeskName       
        
    def isWebSynEnabled(self):
        val=False
        if self.dbSettings!=None:
            if self.dbSettings[DB_POS.WEB_SYNC_EN]=="on":
                val=True        
        return val
    
    def getWebSyncUrl(self):
        return self.webSyncUrl
    
    def getWebSyncIP(self):
        val=""
        if self.dbSettings!=None:
            val=self.dbSettings[DB_POS.WEB_SYNC_IP]                        
        return val
    
    def getWebSyncRegisterdId(self):
        return self.webSyncRegisterId
            


settingsInst=Settings()