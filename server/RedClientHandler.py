
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

        self.clientId = ""
        self.clientType = "none"

        # == For host ==
        self.viewers = []
        # Viewport info
        self.vpWidth = 0
        self.vpHeight = 0
        self.vpMonitorCount = 0
        self.vpCurrentMonitor = 0
        # Auth
        self.auth_required = True

        # == For Guest ==
        self.viewing = None
        self.targetClientId = ""

        self.ready = False

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
            print("Client " + self.clientType + " ID " + self.clientId + " connected!")

            if (self.clientType == "guest"):
                self.targetClientId = pkt["target_client_id"]
                hostClient = self.serverMgr.getClientById(self.targetClientId)
                if (hostClient is None):
                    print("Client " + self.clientType + " ID " + self.clientId + " removed because the target client id doesn't exists!")
                    await self.ws.close()
                    return
                
                if (not hostClient.ready):
                    print("Client " + self.clientType + " ID " + self.clientId + " removed because the target client is not ready!")
                    await self.ws.close()
                    return

                if (hostClient.auth_required):
                    await self.requestAuth()
                else:
                    await self.setReady()
                    await self.setViewer(self, hostClient)           

                # hostClient.viewers.append(self)
                # self.viewing = hostClient

                # await hostClient.updateViewersCount()
                # await self.sendViewportInfoToGuest()
            elif (self.clientType == "host"):
                self.auth_required = pkt["auth_required"]
                await self.setReady()
            else:
                print("Client " + self.clientType + " ID " + self.clientId + " removed because the client type is invalid!")
                await self.ws.close()
            return

        if (pkt["type"] == "authcheck"):
            if (self.clientType != "guest"):
                print("Error, only guest can send authcheck packets!")
                await self.ws.close()
            
            hostClient = self.serverMgr.getClientById(self.targetClientId)
            if (hostClient is None):
                print("Client " + self.clientType + " ID " + self.clientId + " removed because the target client id doesn't exists!")
                await self.ws.close()
                return

            pkt["guest_client_id"] = self.clientId
            
            await hostClient.sendPacket(pkt)
            return

        if (pkt["type"] == "authaccept"):
            if (self.clientType != "host"):
                print("Error, only host can send authaccept packets!")
                await self.ws.close()
            
            guestId = pkt["guest_client_id"]
            guestClient = self.serverMgr.getClientById(guestId)
            if (guestClient is None):
                print("Client " + self.clientType + " ID " + self.clientId + " was accepted but was not found!")
                return

            await guestClient.sendPacket(pkt)
            await guestClient.setReady()
            await self.setViewer(guestClient, self)
            return

        if (pkt["type"] == "authdeny"):
            if (self.clientType != "host"):
                print("Error, only host can send authdeny packets!")
                await self.ws.close()
            
            guestId = pkt["guest_client_id"]
            guestClient = self.serverMgr.getClientById(guestId)
            if (guestClient is None):
                print("Client " + self.clientType + " ID " + self.clientId + " was denied and was not found!")
                return

            await guestClient.sendPacket(pkt)
            return

        # All packets below here must come from a ready client (handshake process is above)
        if (not self.ready):
            print("Error, client is not ready or is not sending handshake packets")
            await self.ws.close()
            return

        if (pkt["type"] == "viewportinfo"):
            if (self.clientType == "host"):
                print("Viewport Info Received from host")
                self.vpWidth = pkt["width"]
                self.vpHeight = pkt["height"]
                self.vpMonitorCount = pkt["monitor_count"]
                self.vpCurrentMonitor = pkt["current_monitor"]

                # Resend to viewers to update the viewport
                for cClient in self.viewers:
                    if (not cViewer.ready):
                        continue
                    await cClient.sendPacket(pkt)
            else:
                print("Invalid Packet Type for a client if type " + self.clientType)
                await self.ws.close()
                return
            return


        if (pkt["type"] == "framesegment"):
            if (self.clientType != "host"):
                print("Error, only host can send framesegment packets!")
                await self.ws.close()

            for cViewer in self.viewers:
                if (not cViewer.ready):
                    continue
                await cViewer.sendPacket(pkt)
            return
        
        if (pkt["type"] == "hid"):
            if (self.clientType != "guest"):
                print("Error, only guest can send hid packets!")
                await self.ws.close()
            await self.viewing.sendPacket(pkt);
            return

        return

    async def sendPacket(self, packet):
        packetJson = json.dumps(packet)
        await self.ws.send(packetJson)
        return

    async def setViewer(self, guest, host):
        host.viewers.append(guest)
        guest.viewing = host

        await host.updateViewersCount()
        await guest.sendViewportInfoToGuest()
        return

    async def requestAuth(self):
        reqAuthPkt = {}
        reqAuthPkt["type"] = "reqauth"
        await self.sendPacket(reqAuthPkt)
        return

    async def setReady(self):
        self.ready = True

        readyPkt = {}
        readyPkt["type"] = "ready"
        await self.sendPacket(readyPkt)
        return

    async def sendHostClosed(self):
        self.ready = False

        readyPkt = {}
        readyPkt["type"] = "hostclosed"
        await self.sendPacket(readyPkt)
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

