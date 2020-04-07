import requests, re, sys, logging

def getSessionID(servername:str,username:str,password:str)->requests.Session:
    sessionRequest = requests.Session()
    try :
        result = sessionRequest.post(servername + "/j_security_check",
                                 data={"j_username": username, "j_password": password})
        rdPrintOut(returncode=result.status_code,stdout=result.content,error=result.content)
    except requests.exceptions.ConnectionError as err:
        dmLogging.logging.error(err)
        sys.exit(1)
    if re.search('r/error', result.url, re.IGNORECASE):
        dmLogging.logging.error("Invalid UserName or Password ")
        sys.exit(1)
    return sessionRequest


def downloadRDJob(sessionID,serverName,  fileName):
    result = sessionID.get("" + serverName + "/api/5/jobs/export?project=<ProjectName>&groupPath=" + fileName + "",
                           headers={'Accept': 'application/xml'})
    return result.content, result.status_code, result.headers


def uploadRDJob(sessionID, serverName, fileName):
    file = {'xmlBatch': open(fileName, 'rb')}
    result = sessionID.post("" + serverName + "/api/5/jobs/import", files=file,
                            data={"project": "<ProjectName>", "format": "xml", "dupeOption": "update"})
    return result.content, result.status_code, result.headers


def getNodeInfo(sessionID, serverName, hostname, user):
    result = sessionID.get("" + serverName + "/api/5/resources",
                           params={"project": "<ProjectName>", "name": hostname + "-" + user},
                           headers={'Accept': 'application/xml'})
    return result.content, result.status_code, result.headers

def getTagsInfo(sessionID, serverName, tags):
    result = sessionID.get("" + serverName + "/api/5/resources",
                           params={"project": "<ProjectName>", "tags": tags + ".*"},
                           headers={'Accept': 'application/xml'})
    return result.content, result.status_code, result.headers

def updateNodeInfo(serverName,sessionID, nodename, tags, jobID):
    result = sessionID.post(
        "" + serverName + "/api/5/job/" + jobID + "/run?argString=\" -nodename " + nodename + " -tags '" + tags + "'\"")
    return result.content, result.status_code, result.headers

def getRDJobStatus(serverName, sessionID, id):
    result = sessionID.get("" + serverName + "/api/5/execution/" + id + "")
    return result.content, result.status_code, result.headers

def createRundeckACL(serverName, sessionID, jobID,jobGroup,ldapGroup):
    result = sessionID.post(""+serverName+ "/api/5/job/" + jobID + "/run?argString=\" -jobgroup " +jobGroup+ " -ldapgroup " + ldapGroup)
    return result.content, result.status_code, result.headers

def rdPrintOut(returncode,stdout,error):
    if returncode != 200 :
        logging.logging.error(error.decode())
        sys.exit(1)
    else:
        logging.logging.debug(stdout.decode())
