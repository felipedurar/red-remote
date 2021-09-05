# Red Remote
# Copyright (C) Durar 2021

import platform
from art import *

import RedConfig
import RedServerManager

# define a main function
def main():
    tprint("RedRemote")
    print(" == Red Remote Access Server ==")
    print(" == Copyright (C) Durar 2020 ==")

    RedConfig.LoadConfigs()
    
    host = RedConfig.GetSettings()["host"]
    port = RedConfig.GetSettings()["port"]
    operatingSystem = RedConfig.GetSettings()["os"]

    print(" Hosting: " + host + ":" + str(port))
    print(" OS: " + operatingSystem)

    redServer = RedServerManager.RedServerManager()
    redServer.start()


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()
