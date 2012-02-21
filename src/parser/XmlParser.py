'''
Created on Feb 8, 2012

@author: ranj4711
'''
import os
from xml.etree.ElementTree import ElementTree
import zipfile

AGSSERVER = os.getenv("AGSSERVER")
enable = True

if os.path.exists(os.path.join(AGSSERVER, "framework", "etc", "config-store-connection.xml")):
    # If site is configured then setup Java debug ports
    tree = ElementTree()
    tree.parse(os.path.join(AGSSERVER, "framework", "etc", "config-store-connection.xml"))
    entries = tree.findall("entry")
    for entry in entries:
        if entry.get("key") == "connectionString":
            if (not os.path.exists(os.path.join(entry.text, "system", "properties.json"))) or (open(os.path.join(entry.text, "system", "properties.json"), "r").read().find("{}") != -1):
                props = "{suspendServiceAtStartup\":true, \"suspendDuration\": 10000, \"javaExtsBeginPort\": 10000, \"javaExtsEndPort\": 10010}"                 
                file = open(os.path.join(entry.text, "system", "properties.json"), "w")
                file.write(props)
                file.flush()
                file.close()
                
print 'done'
                
#zin = zipfile.ZipFile (os.path.join(AGSSERVER, "framework", "lib", "server", "arcgis-admin.jar"), 'r')
#zout = zipfile.ZipFile (os.path.join(AGSSERVER, "framework", "lib", "server", "arcgis-admin-temp.jar"), 'w')
#
#props = zin.read("admin.properties")
#zipinfo = zin.getinfo("admin.properties")
#
#if props.find("DEBUG_CREATE_SITE=true") == -1:
#    props += "\nDEBUG_CREATE_SITE=true"
#    
#for item in zin.infolist():
#    buffer = zin.read(item.filename)
#    if (item.filename != 'admin.properties'):
#        zout.writestr(item, buffer)
#
#zout.writestr(zipinfo, props)
#zout.close()
#zin.close()
#
#os.unlink(os.path.join(AGSSERVER, "framework", "lib", "server", "arcgis-admin.jar"))
#os.rename(os.path.join(AGSSERVER, "framework", "lib", "server", "arcgis-admin-temp.jar"), os.path.join(AGSSERVER, "framework", "lib", "server", "arcgis-admin.jar"))

print 'done'

#for entry in adminJar.infolist():
#    if (entry.filename == 'admin.properties'):
#        adminJar.extract(entry)                
#        adminProps = open('admin.properties', "a")
#        if enable:
#            adminProps.write("DEBUG_CREATE_SITE=true")
#        else:
#            adminProps.write("DEBUG_CREATE_SITE=false")            
#        adminProps.close()
#        adminJar.
#        adminJar.write('admin.properties')
#        adminJar.close()
        

#adminJar.extract('admin.properties')
#adminProps = open('admin.properties', "a")
#adminProps.write("DEBUG_CREATE_SITE=true")
#adminProps.close()
#adminJar.write('admin.properties')
#
#if os.path.exists(os.path.join(os.getenv("AGSSERVER"), "framework", "etc", "config-store-connection.xml")):
#    # If site is configured then setup Java debug ports
#    tree = ElementTree()
#    tree.parse(os.path.join(os.getenv("AGSSERVER"), "framework", "etc", "config-store-connection.xml"))
#    entries = tree.findall("entry")
#    for entry in entries:
#        if entry.get("key") == "connectionString":
#            if not os.path.exists(os.path.join(entry.text, "system", "properties.json")):
#                props = "\{suspendServiceAtStartup\":true, \"suspendDuration\": 10000, \"javaExtsBeginPort\": 10000, \"javaExtsEndPort\": 10010\}"                 
#                file = open(os.path.join(entry.text, "system", "properties.json"), "w")
#                file.write(props)
#                file.flush()
#                file.close()
#                print 'dumped to my props'
                                 
                

                
                
                
            
                
    

    