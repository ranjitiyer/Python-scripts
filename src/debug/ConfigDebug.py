'''
Created on Feb 8, 2012

@author: ranj4711
'''

import zipfile
import os
import sys
from xml.etree.ElementTree import ElementTree

AGSSERVER = os.getenv("AGSSERVER")

if sys.argv[1] == 'disable':
    enable = False
else:
    enable = True

if enable:
    nodeagentSearchText = '"%ARCGIS_JAVA_HOME%\bin\java"'
    nodeagentReplaceText = '"%ARCGIS_JAVA_HOME%\bin\java" -Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=6000'
    
    tomcatSearchText = 'set JAVA_OPTS=%JAVA_OPTS% %TOMCAT_HEAP_SIZE%'
    tomcatReplaceText = 'set JAVA_OPTS=-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=7000 %TOMCAT_HEAP_SIZE%'
    
    geronimoSearchText = 'set ARCGIS_JAVA_OPTS=%GERONIMO_HEAP_SIZE% -XX:MaxPermSize=256m -Dfile.encoding=UTF8'
    geronimoReplaceText = 'set ARCGIS_JAVA_OPTS=%GERONIMO_HEAP_SIZE% -XX:MaxPermSize=256m -Dfile.encoding=UTF8 -Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=8000'
else:
    nodeagentSearchText = '"%ARCGIS_JAVA_HOME%\bin\java" -Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=6000'
    nodeagentReplaceText = '"%ARCGIS_JAVA_HOME%\bin\java"'
    
    tomcatSearchText = 'set JAVA_OPTS=-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=7000 %TOMCAT_HEAP_SIZE%'
    tomcatReplaceText = 'set JAVA_OPTS=%JAVA_OPTS% %TOMCAT_HEAP_SIZE%'
    
    geronimoSearchText = 'set ARCGIS_JAVA_OPTS=%GERONIMO_HEAP_SIZE% -XX:MaxPermSize=256m -Dfile.encoding=UTF8 -Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=8000'
    geronimoReplaceText = 'set ARCGIS_JAVA_OPTS=%GERONIMO_HEAP_SIZE% -XX:MaxPermSize=256m -Dfile.encoding=UTF8'    
        
#Update startserver.bat
string = open(os.path.join(AGSSERVER, "framework", "etc", "scripts", "startserver.bat")).read().replace(geronimoSearchText, geronimoReplaceText)
print string
file = open(os.path.join(AGSSERVER, "framework", "etc", "scripts", "startserver.bat"), "w")
file.write(string)
file.flush()
file.close()
print 'Added debug info to geronimo.bat'        
        
#Update catalina.bat        
string = open(os.path.join(AGSSERVER, "framework", "runtime", "tomcat", "bin", "catalina.bat")).read().replace(tomcatSearchText,tomcatReplaceText)
file = open(os.path.join(AGSSERVER, "framework", "runtime", "tomcat", "bin", "catalina.bat"), "w")
file.write(string)
file.flush()
file.close()
print 'Added debug info to catalina.bat'

#Update geronimo.bat
string = open(os.path.join(AGSSERVER, "geronimo", "bin", "geronimo.bat")).read().replace(geronimoSearchText, geronimoReplaceText)
file = open(os.path.join(AGSSERVER, "geronimo", "bin", "geronimo.bat"), "w")
file.write(string)
file.flush()
file.close()
print 'Added debug info to geronimo.bat'

# Update properties.json
if os.path.exists(os.path.join(AGSSERVER, "framework", "etc", "config-store-connection.xml")):
    # If site is configured then setup Java debug ports
    tree = ElementTree()
    tree.parse(os.path.join(AGSSERVER, "framework", "etc", "config-store-connection.xml"))
    entries = tree.findall("entry")
    for entry in entries:
        if entry.get("key") == "connectionString":
            # if file does not exist or if it is empty
            if (not os.path.exists(os.path.join(entry.text, "system", "properties.json"))) or (open(os.path.join(entry.text, "system", "properties.json"), "r").read().find("{}") != -1):
                props = "{\"suspendServiceAtStartup\":true, \"suspendDuration\": 10000, \"javaExtsBeginPort\": 10000, \"javaExtsEndPort\": 10010}"                 
                file = open(os.path.join(entry.text, "system", "properties.json"), "w")
                file.write(props)
                file.flush()
                file.close()
else:
    # else configure admin to setup Java debug ports during create site
    zin = zipfile.ZipFile (os.path.join(AGSSERVER, "framework", "lib", "server", "arcgis-admin.jar"), 'r')
    zout = zipfile.ZipFile (os.path.join(AGSSERVER, "framework", "lib", "server", "arcgis-admin-temp.jar"), 'w')
    
    props = zin.read("admin.properties")
    zipinfo = zin.getinfo("admin.properties")

    if props.find("DEBUG_CREATE_SITE=true") == -1:
        if enable:
            props += "\nDEBUG_CREATE_SITE=true"
        else:
            print 'disabling...'
    else:
        if not enable:
            props.replace("DEBUG_CREATE_SITE=true", "DEBUG_CREATE_SITE=false")
        
    for item in zin.infolist():
        buffer = zin.read(item.filename)
        if (item.filename != 'admin.properties'):
            zout.writestr(item, buffer)
    
    zout.writestr(zipinfo, props)
    zout.close()
    zin.close()
    
    os.unlink(os.path.join(AGSSERVER, "framework", "lib", "server", "arcgis-admin.jar"))
    os.rename(os.path.join(AGSSERVER, "framework", "lib", "server", "arcgis-admin-temp.jar"), os.path.join(AGSSERVER, "framework", "lib", "server", "arcgis-admin.jar"))

print 'Done'