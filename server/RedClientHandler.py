
import asyncio
import json
import logging
import websockets
import threading
import time

class RedClientHandler:
    def __init__(self, serverMgr, ws):
        self.ws = ws
        self.serverMgr = serverMgr

        self.running = True
        self.behaviorHandlerThread = threading.Thread(target = self.behaviorHandler, args=())

        self.handshakeCompleted = False
        self.clientId = ""
        self.clientType = "none"

        # == For host ==
        self.viewers = []
        # Viewport info
        self.vpWidth = 0
        self.vpHeight = 0
        self.vpMonitorCount = 0
        self.vpCurrentMonitor = 0

        # == For Guest ==
        self.viewing = None
        self.targetClientId = ""



        dir(ws)
        return

    async def start(self):
        self.behaviorHandlerThread.start()

        async for message in self.ws:
            data = json.loads(message)
            #print("data received")
            await self.processPacket(data)
        return

    async def processPacket(self, pkt):
        if (pkt["type"] == "handshake"):
            self.clientId = pkt["client_id"]
            self.clientType = pkt["client_type"]
            self.handshakeCompleted = True
            print("Client " + self.clientType + " ID " + self.clientId + " connected!")

            if (self.clientType == "guest"):
                self.targetClientId = pkt["target_client_id"]
                hostClient = self.serverMgr.getClientById(self.targetClientId)
                if (hostClient is None):
                    print("Client " + self.clientType + " ID " + self.clientId + " removed because the target client id doesn't exists!")
                    self.ws.close()
                    return
                
                if (not hostClient.handshakeCompleted):
                    print("Client " + self.clientType + " ID " + self.clientId + " removed because the target client doesn't finished the handshake!")
                    self.ws.close()
                    return
                
                hostClient.viewers.append(self)
                self.viewing = hostClient

                await hostClient.updateViewersCount()
                await self.sendViewportInfoToGuest()

        if (pkt["type"] == "viewportinfo"):
            if (self.clientType == "host"):
                print("Viewport Info Received from host")
                self.vpWidth = pkt["width"]
                self.vpHeight = pkt["height"]
                self.vpMonitorCount = pkt["monitor_count"]
                self.vpCurrentMonitor = pkt["current_monitor"]

                # Resend to viewers to update the viewport
                for cClient in self.viewers:
                    await cClient.sendPacket(pkt)
            else:
                print("Invalid Packet Type for a client if type " + self.clientType)
                self.ws.close()
                return


        if (pkt["type"] == "framesegment"):
            if (self.clientType != "host"):
                print("Error, only host can send framesegment packets!")
                self.ws.close()

            for cViewer in self.viewers:
                await cViewer.sendPacket(pkt)
        
        if (pkt["type"] == "hid"):
            if (self.clientType != "guest"):
                print("Error, only guest can send hid packets!")
                self.ws.close()
            await self.viewing.sendPacket(pkt);

        return

    async def sendPacket(self, packet):
        packetJson = json.dumps(packet)
        await self.ws.send(packetJson)
        return

    def behaviorHandler(self):
        while (self.running):
            time.sleep(0.1)


        return

    async def updateViewersCount(self):
        viewerCountPkt = {}
        viewerCountPkt["type"] = "viewercount"
        viewerCountPkt["amount"] = len(self.viewers)
        await self.sendPacket(viewerCountPkt)
    
    async def sendViewportInfoToGuest(self):
        viewportInfoPkt = {}
        viewportInfoPkt["type"] = "viewportinfo"
        viewportInfoPkt["monitor_count"] = self.viewing.vpMonitorCount
        viewportInfoPkt["current_monitor"] = self.viewing.vpCurrentMonitor
        viewportInfoPkt["width"] = self.viewing.vpWidth
        viewportInfoPkt["height"] = self.viewing.vpHeight
        await self.sendPacket(viewportInfoPkt)

