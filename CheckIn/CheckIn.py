'''
Created on Sep 4, 2018

@author: sedlmeier
'''

import CheckInWebserver
import upsyncCheckIn
import configparser
import webbrowser

from checkInLogger import logger
    
if __name__ == '__main__':

    # start webserver
    logger.info("Start Internal Webserver")
    
    cfg = configparser.ConfigParser()
    cfg.read('checkin.cfg')
    
    port=cfg.getint("ExtWebserver","Port")
    url=cfg.get("WebSync","Url")
    ip = cfg.get("WebSync","AdapterIp")
    regid=cfg.get("WebSync","RegisterId")
    
    
    CheckInWebserver.startWebserver(port)
    #upsyncCheckIn.startUpsyncThread(url, ip, regid)
    
    webbrowser.open("http://%s:%d/%s"%("127.0.0.1",
                                       port, 
                                       "checkin.html"))
    
    while(1):
        pass
    