'''
Created on Jul 10, 2014

@author: ranj4711
'''

import sys
import urllib
import httplib
import json
import threading
import Queue
import time
import mimetypes
import random
import urllib2

uploaderSemaphore   = threading.Semaphore(10)
publisherSempahore  = threading.Semaphore(3)

uploadsQueue = Queue.Queue()
resultsQueue = Queue.Queue()

machine = ''
port = ''
token = ''

folders = []

class ServiceInfo:
    def __init__(self,sd,folder,service,cluster):        
        self.sd = sd
        self.folder = folder
        self.service = service
        self.cluster = cluster
        self.uploadid = ''        

class Result:
    def __init__(self, sd, timeout, error):
        self.sd = sd
        self.timeout = False
        self.error = error                

class Uploader(threading.Thread):    
    def __init__(self, serviceInfo):
        threading.Thread.__init__(self)
        self.serviceInfo = serviceInfo
        
    def run(self):
        # Grab semaphore
        uploaderSemaphore.acquire()
        
        uploadurl = 'http://'+ machine + ':' + port + '/arcgis/admin/uploads/upload'

        # Read the sd file        
        with open(self.serviceInfo.sd, "rb") as sdfile :
            data = sdfile.read()
         
        # multi-part upload 
        fields = {'f': 'json', 'token' : token}
        files = {'itemFile': {'filename': 'mobile_bv.sd', 'content': data}}        
        data, headers = encode_multipart(fields, files)
                        
        request = urllib2.Request(uploadurl, data=data, headers=headers)
        f = urllib2.urlopen(request)
        
        # Extract the itemID
        responsejson = json.loads(f.read())        
        itemid = responsejson['item']['itemID']
        
        # Set the uploadid and enqueue result
        self.serviceInfo.uploadid = itemid
        uploadsQueue.put(self.serviceInfo)
                
        # Release semaphore
        uploaderSemaphore.release()
        
class Publisher(threading.Thread):    
    def __init__(self, serviceInfo):
        threading.Thread.__init__(self)
        self.serviceInfo = serviceInfo
        
    def run(self):
        # Grab semaphore
        publisherSempahore.acquire()
        
        # get default service config 
        serviceconfigurl = "/arcgis/admin/uploads/" + self.serviceInfo.uploadid + "/serviceconfiguration.json"
        params = urllib.urlencode({'token': token, 'f': 'json'})        
        (_, data) = postToServer(machine,port,serviceconfigurl,params)
        servicejson = json.loads(data)
        
        # Edit it
        servicejson['serviceName'] = self.serviceInfo.service
        servicejson['clusterName'] = self.serviceInfo.cluster
        servicejson['folderName']  = self.serviceInfo.folder         
         
        # Submit publishing job
        submitjoburl = "/arcgis/rest/services/System/PublishingTools/GPServer/Publish Service Definition/submitJob"
        params = urllib.urlencode({'token': token, 'f': 'json', 'in_sdp_id':self.serviceInfo.uploadid, 'in_config_overwrite':json.dumps(servicejson)})
        (_, data) = postToServer(machine,port,submitjoburl,params)        
        submitjobjson = json.loads(data)
        
        # Sleep before polling again
        time.sleep(5)
        
        jobid = submitjobjson['jobId']
        status = 'esriJobSubmitted'
        response = ''        
        timeout = time.time() + 60 * 5
        
        # Timeout after 5 mins        
        while time.time() < timeout :
            # Get job status
            statusurl = '/arcgis/rest/services/System/PublishingTools/GPServer/Publish Service Definition/jobs/'+jobid+'/status'    
            params = urllib.urlencode({'token': token, 'f': 'json'})
            (_,data) = postToServer(machine,port,statusurl,params)
            response = json.loads(data)
            status = response['jobStatus']
            
            # Check if we have a result
            if status != 'esriJobSubmitted' and status != 'esriJobExecuting':
                break;
            
            # Sleep in between iterations
            time.sleep(5)
        
        # Timed out        
        if status == 'esriJobSubmitted' or status == 'esriJobExecuting':
            result = Result(self.serviceInfo.sd,True,'')
        else:
            # Errored
            if status == 'esriJobSucceeded':
                result = Result(self.serviceInfo.sd,False,'')
            # Succeeded    
            else:                
                result = Result(self.serviceInfo.sd,False,response)  
        
        # Put it in the results queue
        resultsQueue.put(result)
        
        # Release semaphore
        publisherSempahore.release()        
                
def main(argv=None):
    global machine
    machine = raw_input("Enter server name: ")
    global port
    port = '6080'
    
    user = 'admin'
    password = 'admin'
    inputfile = 'C:/Users/ranj4711/workspace/pytools/src/demo/publish/services.txt'
   
    start_time = time.time()
   
    global token
    token = getToken(user,password,machine,port)
    
    serviceinfos = []
    with open(inputfile, 'r') as thefile:
        lines = thefile.readlines()
        for line in lines :
            line.rstrip('\n')
            tokens  = line.split('|')
            sd      = tokens[0].split('=')[1]
            folder  = tokens[1].split('=')[1]
            service = tokens[2].split('=')[1]
            cluster = tokens[3].split('=')[1]
            serviceinfos.append(ServiceInfo(sd,folder,service,cluster))
            
            # Create the folder if it doesn't exist
            global folders
            if not folder in folders:
                createfolderurl = "/arcgis/admin/services/createFolder"
                params = urllib.urlencode({'token':token,'f':'json','folderName':folder})
                (_,data) = postToServer(machine,port,createfolderurl,params)
                respjson = json.loads(data)
                if 'status' in respjson:
                    if respjson['status'] == 'success':
                        print 'Successfully created folder ' + folder
    
    # Spawn uploaders
    for serviceinfo in serviceinfos :
        uploader = Uploader(serviceinfo)
        uploader.start()               
    
    # Spawn publishers    
    for serviceinfo in serviceinfos :
        uploadedServiceInfo = uploadsQueue.get()        
        publisher = Publisher(uploadedServiceInfo)
        publisher.start()
        
    # Wait for results
    for serviceinfo in serviceinfos:
        result = resultsQueue.get()
        
        if result.timeout is True:
            print 'Publishing failed due to timeout ' + result.sd
            continue  
         
        if result.error != '':
            print 'Published failed due to errors ' + result.sd
            continue
        
        print 'Publishing succeeded ' + result.sd
     
    print("--- %s seconds ---" % (time.time() - start_time))        
 
def getAllFolders():
    (_,data) = postToServer(machine,port,"/arcgis/admin/services", 
                            urllib.urlencode({'token':token,'f':'json'}))
    global folders    
    folders = json.loads(data)['folders']
    print folders     
      
#########################################
##    
##        Internal functions
##
#########################################

# A function that checks that the JSON response received from the server does not contain an error   
def assertJsonSuccess(data):
    obj = json.loads(data)
    if 'status' in obj and obj['status'] == "error":
        return False
    else:
        return True


def getToken(username, password, serverName, serverPort):
    tokenURL = "/arcgis/admin/generateToken"
    
    params = urllib.urlencode({'username': username, 'password': password,'client': 'requestip', 'f': 'json'})
    
    response, data = postToServer(serverName, serverPort, tokenURL, params)
        
    if (response.status != 200 or not assertJsonSuccess(data)):
        print "Error while fetching tokens from admin URL. Please check if the server is \
            running and ensure that the username/password provided are correct"
        print str(data)
        return ""
    else: 
        # Extract the token from it
        token = json.loads(data)   
        return token['token']
    
# A function that will post HTTP POST request to the server
def postToServer(serverName, serverPort, url, params):    
    httpConn = httplib.HTTPConnection(serverName, serverPort)
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    # URL encode the resource URL
    url = urllib.quote(url.encode('utf-8'))
    
    # Build the connection to add the roles to the server
    httpConn.request("POST", url, params, headers)

    response = httpConn.getresponse()
    data = response.read()
    httpConn.close()

    return (response, data)    

def encode_multipart(fields, files, boundary=None):
    def escape_quote(s):
        return s.replace('"', '\\"')

    _BOUNDARY_CHARS = '----------ThIs_Is_tHe_bouNdaRY_$'
    if boundary is None:
        boundary = ''.join(random.choice(_BOUNDARY_CHARS) for i in range(30))
    lines = []

    for name, value in fields.items():
        lines.extend((
            '--{0}'.format(boundary),
            'Content-Disposition: form-data; name="{0}"'.format(escape_quote(name)),
            '',
            str(value),
        ))

    for name, value in files.items():
        filename = value['filename']
        if 'mimetype' in value:
            mimetype = value['mimetype']
        else:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        lines.extend((
            '--{0}'.format(boundary),
            'Content-Disposition: form-data; name="{0}"; filename="{1}"'.format(
                    escape_quote(name), escape_quote(filename)),
            'Content-Type: {0}'.format(mimetype),
            '',
            value['content'],
        ))

    lines.extend((
        '--{0}--'.format(boundary),
        '',
    ))
    body = '\r\n'.join(lines)

    headers = {
        'Content-Type': 'multipart/form-data; boundary={0}'.format(boundary),
        'Content-Length': str(len(body)),
    }

    return (body, headers)

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))