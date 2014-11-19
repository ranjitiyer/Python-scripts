'''
Created on Jul 10, 2014

@author: ranj4711
'''

import json, urllib,httplib
import sys
import getpass

def main(argv=None):
#     # Ask for admin user name and password
#     username = raw_input("Enter user name: ")
#     password = getpass.getpass("Enter password: ")
#      
#     # Ask for server name & port
#     machine = raw_input("Enter server name: ")
#     port = raw_input("Enter server port: ")

    # Ask for admin user name and password
    username = 'admin'
    password = 'admin'
      
    # Ask for server name & port
    machine = 'winlab1'
    port = '6080'
    
    # Get a token and connect
    token = getToken(username, password, machine, port)
    
    # get all clusters
    allClusters = getAllClusters(machine,port,token)
    
    # get all machines in the site        
    allMachines = getAllMachines(machine,port,token)
    
    # get all machines in all clusters
    machinesInClusters = []
    for cluster in allClusters :
        machines = getAllMachinesInCluster(machine,port,token,cluster)
        machinesInClusters = machinesInClusters + machines        
          
    # Compute machines not in cluster
    for machineInCluster in machinesInClusters :
        allMachines.remove(machineInCluster)
    
    # What are left with            
    if len(allMachines) == 0 :
        print 'All machines in the site have already been assigned to a cluster'
    else: 
        print 'Availabe clusters'
        print '-----------------'
        for cluster in allClusters:
            print cluster
        
        print '\n'
        
        print 'Available machines'
        print '-----------------'
        for machine in allMachines:
            print machine
        
        print '\n'
            
        machineToAdd = raw_input("Enter the machine you want to add to a cluster:")
        clusterToAddTo = raw_input("Enter the cluster you want the machine added to:")        
        addMachineToCluster(machine,port,token,clusterToAddTo,machineToAdd)
        
        print 'Done'

def addMachineToCluster(machine,port,token,cluster,machineToAdd):
    addMachine = "/arcgis/admin/clusters/" + cluster + "/machines/add"
    params = urllib.urlencode({'machineNames':machineToAdd,'token':token,'f':'json'})
    response, data = postToServer(machine, port, addMachine, params)    
    if (response.status != 200 or not assertJsonSuccess(data)):
        print "Unable to add machine to cluster."
        print str(data)
        return
    
def getAllMachinesInCluster(machine,port,token,cluster):
    clustersUrl = "/arcgis/admin/clusters/" + cluster
    params = urllib.urlencode({'token':token,'f':'json'})
    response, data = postToServer(machine, port, clustersUrl, params)    
    if (response.status != 200 or not assertJsonSuccess(data)):
        print "Unable to obtain a list of machines in a cluster."
        print str(data)
        return
    
    clusterInfo = json.loads(data)
    return clusterInfo['machineNames']
    
    
def getAllClusters(machine, port, token):
    clustersUrl = "/arcgis/admin/clusters"
    params = urllib.urlencode({'token':token,'f':'json'})
    
    response, data = postToServer(machine, port, clustersUrl, params)    
    if (response.status != 200 or not assertJsonSuccess(data)):
        print "Unable to obtain a list of clusters."
        print str(data)
        return
        
    # Extract the security store type
    clusterNames = []
    clustersJson = json.loads(data)
    for clusterJson in clustersJson['clusters']:
        clusterNames.append(clusterJson["clusterName"])
        
    # Return all cluster names    
    return clusterNames
    
def getAllMachines(machine, port, token):
    clustersUrl = "/arcgis/admin/machines"
    params = urllib.urlencode({'token':token,'f':'json'})

    response, data = postToServer(machine, port, clustersUrl, params)
    
    if (response.status != 200 or not assertJsonSuccess(data)):
        print "Unable to obtain a list of machines."
        print str(data)
        return
        
    # Extract the security store type
    machineNames = []
    machinesJson = json.loads(data)
    for machineJson in machinesJson['machines']:
        machineNames.append(machineJson["machineName"])
        
    # Return all cluster names    
    return machineNames    
            
############################################################
##    Internal util functions
############################################################

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
        print "Error while fetching tokens from admin URL. Please check if the server is running and ensure that the username/password provided are correct"
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

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))