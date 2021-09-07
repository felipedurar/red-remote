
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
    RedConfig["auth_required"] = config.get('authentication', 'auth_required')
    RedConfig["password"] = config.get('authentication', 'password')

    RedConfig["reduce_pixel_depth"] = config.get('stream', 'reduce_pixel_depth')

def GetSettings():
    return RedConfig