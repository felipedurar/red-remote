# Red Remote
# Copyright (C) Durar 2021

import configparser
from art import *

import client_linux
import RedConfig
import RedClientHost

# define a main function
def main():
    tprint("RedRemote")
    print(" == Red Remote Access Client ==")
    print(" == Copyright (C) Durar 2020 ==")

    RedConfig.LoadConfigs()
    
    server = RedConfig.GetSettings()["server"]
    client_id = RedConfig.GetSettings()["client_id"]
    operatingSystem = RedConfig.GetSettings()["os"]

    print(" Server: " + server)
    print(" Client Id: " + client_id)
    print(" OS: " + operatingSystem)

    if (operatingSystem == "Windows"):
        redClient = RedClientHost.RedClientHost()
        redClient.start()
    elif (operatingSystem == "Linux"):
        print("")
    elif (operatingSystem == "Darwin"):
        print("")


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()