'''
Created on Feb 20, 2012

@author: ranj4711
'''

import subprocess
import types
import string
import os
import shutil
import sys
from shutil import ignore_patterns

merge = False

if len(sys.argv) == 1:
    print "Usage: CodeMergeReview.py [merge|review]"
    exit()    

if len(sys.argv) > 1 and sys.argv[1] == 'merge':
    merge = True    

#Programs
command     = 'C:/Program Files (x86)/Borland/StarTeam Cross-Platform Client 2009/stcmd'
winmerge    = 'C:/Program Files (x86)/WinMerge/WinMergeU.exe'

#Commands
list        = 'list'
checkout    = 'co'

#Directories
starteamdir     = '/ArcGIS/Gold/Discovery'
workingdir      = 'C:\\ArcGIS\\Discovery'
codereviewdir   = 'C:\\shared\\CodeReview\\Discovery'
mergedir        = 'C:\\Merge'

starteamdirs        = [starteamdir + '/Admin/Agsadmin', 
                       starteamdir + '/Admin/AgsadminRest',
                       starteamdir + '/Admin/NodeAgent',
                       starteamdir + '/Catalog',
                       starteamdir + '/Common',
                       starteamdir + '/Ejb',
                       starteamdir + '/Security', 
                       starteamdir + '/ServiceLib']
buildfile   = "\\\\archive\\10Builds_64\\DebugOK.txt"

# The current build number
if not os.path.exists(buildfile):
    print 'Unable to determine the build number. ' + buildfile + 'does not exist.'
    exit()
    
buildnum    = open(buildfile).read()

# Visitor that deletes files
def visit(arg, dirname, names):
    for name in names:
        subname = os.path.join(dirname, name)
        if not os.path.isdir(subname):            
            os.unlink(subname)

if merge:
    # List of files to be merged
    tomerge = []

    # Delete merge folder
    if (os.path.exists(mergedir)):
        os.path.walk(mergedir, visit, '(User data)')
        shutil.rmtree(mergedir)
    
    try:
        for dir in starteamdirs:            
            # Check out all OUT OF DATE and MISSING files 
            print 'Checking out out of date and missing files from ' + dir
            subprocess.check_call([command, checkout, '-o', '-filter', 'OI', '-is', 
                                       '-cfgl', '10.1.0.' + buildnum, '-pwdfile', 'c:/pwd.txt', '-p', 'ranj4711:pwd@starteamsrv.esri.com:49201' + dir, '>NUL'], shell=True);                                                              
        
            # List all the files that must be merged
            print 'Getting a list of files that need to be merged in '+ dir
            f = subprocess.check_output([command, list, '-short', '-filter', 'G', '-is', 
                                       '-cfgl', '10.1.0.' + buildnum, '-pwdfile', 'c:/pwd.txt', '-p', 'ranj4711:pwd@starteamsrv.esri.com:49201' + dir], shell=True);
    
            # Back up the local file to be merged                                   
            print 'Backing up files that need to be merged to location ' + mergedir
            lines = string.split(f, '\n')
            for line in lines:
                if (string.find(line, 'G ' + workingdir) != -1):                
                    filename = string.split(line, ' ')[1]
                    tomerge.append(filename)
                    shutil.copy(filename, mergedir)
            
            # Force check out the files to be merged
            print 'Force checking out files to be merged in ' + dir            
            subprocess.check_call([command, checkout, '-o', '-filter', 'G', '-is', 
                                       '-cfgl', '10.1.0.' + buildnum, '-pwdfile', 'c:/pwd.txt', '-p', 'ranj4711:pwd@starteamsrv.esri.com:49201' + dir, '>NUL'], shell=True);       
            
        # Open Winmerge for each file to be merged
        if (len(tomerge) == 0):
            print 'There are no files to merge in ' + dir        
        
        for filetomerge in tomerge:
            tomergewith = os.path.basename(filetomerge)
            subprocess.call([winmerge,filetomerge, tomergewith])
            
    except subprocess.CalledProcessError, e:
        print "Error ", e.output
else:
    # List of files to be reviewed    
    toreview = []
    
    # Delete old code review folder
    print 'Deleting the old directory tree at ' + codereviewdir
    if (os.path.exists(codereviewdir)):    
        os.path.walk(codereviewdir, visit, '(User data)')
        shutil.rmtree(codereviewdir, True)
    
    # Copy directory structure
    print 'Creating the Discovery directory structure at ' + codereviewdir 
    shutil.copytree(workingdir, codereviewdir, ignore=ignore_patterns('*.class','buildoutput*','bin*','buildscripts','.git*','.classpath','.project', '.settings*'))
    
    # Delete all files
    os.path.walk(codereviewdir, visit, '(User data)')
    
    for dir in starteamdirs:
        print 'Processing ' + dir    
        # List files that have been Modified locally
        f= subprocess.check_output([command, list, '-short', '-filter', 'M', '-is', 
                                   '-cfgl', '10.1.0.' + buildnum, '-pwdfile', 'c:/pwd.txt', '-p', 'ranj4711:pwd@starteamsrv.esri.com:49201' + dir], shell=True);

        # Make a list of those files                                   
        lines = string.split(f, '\n')
        for line in lines: 
            if (string.find(line, 'M ' + workingdir) != -1):                
                filename = string.split(line, ' ')[1].strip()                
                toreview.append(filename)

    # Copy each file for code review
    for file in toreview:
        shutil.copy(file, os.path.dirname(string.replace(file, workingdir, codereviewdir)))        
print 'Done...'    