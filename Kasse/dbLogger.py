'''
Created on Sep 6, 2018

@author: sedlmeier
'''

import logging
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


