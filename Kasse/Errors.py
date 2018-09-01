'''
Created on 15.09.2017

@author: markus.sedlmeier
'''

class BasarError(Exception):
    def __init__(self, *args, **kwargs):
        Exception(self,*args,**kwargs)
    
    
class RequestError(BasarError):
    
    def __init__(self, err, msg="unspecified Error", sys_err=None):        
        self.err=err
        self.msg=msg
        self.sys_err=sys_err
      
    def __str__(self):
        return self.msg  