'''
Created on 11.09.2017

@author: Laptop8460
''' 
from distutils.core import setup
import sys, os
import py2exe


sys.argv.append('py2exe')
    
def runSetup():
    #setup my option for single file output
    '''
    py2exe_options = dict( ascii=True,  # Exclude encodings
                           excludes=['_ssl',  # Exclude _ssl
                                     'pyreadline', 'difflib', 'doctest', 'locale',
                                     'optparse', 'pickle', 'calendar', 'pbd', 'unittest', 'inspect'],  # Exclude standard library
                           dll_excludes=['msvcr71.dll', 'w9xpopen.exe',
                                         'API-MS-Win-Core-LocalRegistry-L1-1-0.dll',
                                         'API-MS-Win-Core-ProcessThreads-L1-1-0.dll',
                                         'API-MS-Win-Security-Base-L1-1-0.dll',
                                         'KERNELBASE.dll',
                                         'POWRPROF.dll',
                                         ],
                           #compressed=None,  # Compress library.zip
                           bundle_files = 1,
                           optimize = 2                        
                           )
    
    '''
    setup(options={'py2exe':{}},
          console=[{"script":"Basar.py"}])
'''            
setup(
    options = {'py2exe': {'bundle_files': 1, 'compressed': True}},
    windows = [{'script': "Basar.py"}],
    zipfile = None,
)
'''

if __name__ == '__main__':
    print("RUN SETUP IN %s"%os.getcwd())
    runSetup()


