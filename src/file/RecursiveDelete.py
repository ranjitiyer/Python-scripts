'''
Created on Feb 20, 2012

@author: ranj4711
'''
'''
Created on Feb 11, 2012

@author: ranj4711
'''

import os
import os.path
import pprint
import shutil
from types import *

strings = os.listdir("c:\\arcgisserver\\directories\\system")
if isinstance(strings, ListType):
    print len(strings)
    
index = 0

somestr = "Some string" + str(index)
print somestr

olddir = "c:\\arcgisserver\\directories\\system\\mysystem"
newdir = "c:\\arcgisserver\\directories\\system\\mysystem"
origdir = "c:\\arcgisserver\\directories\\system\\mysystem"
while len(os.listdir(newdir)) != 0:
    index = index + 1
    newdir = origdir + str(index)
    shutil.move (olddir + "\\mysystem", newdir)
    print 'Deleting' + olddir    
    shutil.rmtree(olddir)
    olddir = newdir


#shutil.move("c:\\arcgisserver\\directories\\system\\mysystem2\\mysystem", "c:\\arcgisserver\\directories\\system\\mysystem3")
#shutil.rmtree("c:\\arcgisserver\\directories\\system\\mysystem2")

print 'done'

#def visit(arg, dirname, names):
#    #print dirname, arg
#    for name in names:
#        subname = os.path.join(dirname, name)
#        if os.path.isdir(subname):
#            print '  %s/' % name 
#        else:            
#            os.unlink(os.path.join(dirname, name))             
#    print    
#os.path.walk('c:/arcgisserver/directories/system/mysystem', visit, '(User data)')
               


