'''
Created on Sep 6, 2018

@author: sedlmeier
'''

import logging

synclogger = logging.getLogger('sync')
synclogger.setLevel(logging.DEBUG)
syncfh = logging.FileHandler("sync.log")
syncfh.setLevel(logging.DEBUG)
syncch = logging.StreamHandler()
syncch.setLevel(logging.DEBUG)
syncformatter = logging.Formatter("%(threadName)s %(asctime)s  %(levelname)s: %(message)s","%H:%M:%S")
syncch.setFormatter(syncformatter)
synclogger.addHandler(syncfh)
synclogger.addHandler(syncch)