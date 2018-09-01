'''
Created on Aug 24, 2018

@author: sedlmeier
'''

import logging
logger = logging.getLogger('log')
def initLogger():    
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("basar.log")
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(threadName)s %(asctime)s  %(levelname)s: %(message)s","%H:%M:%S")
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


synclogger = logging.getLogger('sync')
synclogger.setLevel(logging.INFO)
syncfh = logging.FileHandler("sync.log")
syncfh.setLevel(logging.DEBUG)
syncch = logging.StreamHandler()
syncch.setLevel(logging.DEBUG)
syncformatter = logging.Formatter("%(threadName)s %(asctime)s  %(levelname)s: %(message)s","%H:%M:%S")
syncch.setFormatter(syncformatter)
synclogger.addHandler(syncfh)
synclogger.addHandler(syncch)


dblogger = logging.getLogger('db')
dblogger.setLevel(logging.INFO)
dbfh = logging.FileHandler("db.log")
dbfh.setLevel(logging.DEBUG)
dbch = logging.StreamHandler()
dbch.setLevel(logging.DEBUG)
dbformatter = logging.Formatter("%(threadName)s %(asctime)s  %(levelname)s: %(message)s","%H:%M:%S")
dbch.setFormatter(dbformatter)
dblogger.addHandler(dbfh)
dblogger.addHandler(dbch)




    
    