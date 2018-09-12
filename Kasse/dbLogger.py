'''
Created on Sep 6, 2018

@author: sedlmeier
'''

import logging
logger = logging.getLogger('db')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("log/db.log")
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
dbf = logging.Formatter("%(threadName)s %(asctime)s  %(levelname)s: %(message)s","%H:%M:%S")
fh.setFormatter(dbf)
ch.setFormatter(dbf)
logger.addHandler(fh)
logger.addHandler(ch)


