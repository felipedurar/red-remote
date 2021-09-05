
import configparser
import platform

global RedConfig
RedConfig = {}

def LoadConfigs():
    config = configparser.ConfigParser()
    config.read("client.conf")
    
    RedConfig["os"] = platform.system()

    RedConfig["server"] = config.get('endpoint', 'server')
    RedConfig["client_id"] = config.get('endpoint', 'client_id')
    RedConfig["password"] = config.get('endpoint', 'password')

def GetSettings():
    return RedConfig