import asyncio
import json
import logging
import websockets

import RedConfig
import RedClientHandler

class RedServerManager:
    def __init__(self):
        self.server = None
        self.config = RedConfig.GetSettings()
        
        self.clients = []

        return

    def start(self):
        self.server = websockets.serve(self.conn_handler, self.config["host"], self.config["port"])

        asyncio.get_event_loop().run_until_complete(self.server)
        asyncio.get_event_loop().run_forever()

        return

    async def conn_handler(self, websocket, path):
        if (path != "/redremote"):
            print("Connection Refused due to wrong path")
            websocket.close()
            return

        cClient = None
        try:
            print("Client Connected!")
            cClient = RedClientHandler.RedClientHandler(self, websocket)
            self.clients.append(cClient)

            await cClient.start()
        
        except:
            print("An error occurred to the client " + cClient.clientId)
        finally:
            await self.removeClient(cClient)
            print("Client " + cClient.clientId + " disconnected!")
        return

    async def removeClient(self, client):
        if (client.clientType == "guest"):
            if (client.viewing is not None):
                client.viewing.viewers.remove(client)
                await client.viewing.updateViewersCount()
        elif (client.clientType == "host"):
            for cViewer in client.viewers:
                cViewer.viewing = None
                cViewer.sendHostClosed()
                await cViewer.ws.close()

        self.clients.remove(client)
        print("Client " + client.clientId + " removed!")

    def getClientById(self, id):
        for cClient in self.clients:
            if (cClient.clientId == id):
                return cClient
        return None
