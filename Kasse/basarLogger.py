'''
Created on Aug 24, 2018

@author: sedlmeier
'''

import logging
logger = logging.getLogger('log')   
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("log/basar.log")
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(threadName)s %(asctime)s  %(levelname)s: %(message)s","%H:%M:%S")
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)





    
    