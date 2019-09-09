'''
Created on Sep 13, 2018

@author: sedlmeier
'''

import logging
logger = logging.getLogger('checkin')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("log/checkin.log")
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
dbf = logging.Formatter("%(threadName)s %(asctime)s  %(levelname)s: %(message)s","%H:%M:%S")
fh.setFormatter(dbf)
ch.setFormatter(dbf)
logger.addHandler(fh)
logger.addHandler(ch)