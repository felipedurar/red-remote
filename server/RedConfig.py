
import configparser
import platform

global RedConfig
RedConfig = {}

def LoadConfigs():
    config = configparser.ConfigParser()
    config.read("client.conf")
    
    RedConfig["os"] = platform.system()

    RedConfig["host"] = config.get('endpoint', 'host')
    RedConfig["port"] = int(config.get('endpoint', 'port'))

def GetSettings():
    return RedConfig