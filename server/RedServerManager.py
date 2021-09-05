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

        finally:
            self.clients.remove(cClient)
            print("Client " + cClient.clientId + " disconnected!")
        return

    def getClientById(self, id):
        for cClient in self.clients:
            if (cClient.clientId == id):
                return cClient
        return None


#logging.basicConfig()

# STATE = {"value": 0}

# USERS = set()


# def state_event():
#     return json.dumps({"type": "state", **STATE})


# def users_event():
#     return json.dumps({"type": "users", "count": len(USERS)})


# async def notify_state():
#     if USERS:  # asyncio.wait doesn't accept an empty list
#         message = state_event()
#         await asyncio.wait([user.send(message) for user in USERS])


# async def notify_users():
#     if USERS:  # asyncio.wait doesn't accept an empty list
#         message = users_event()
#         await asyncio.wait([user.send(message) for user in USERS])

################################################################################################
# async def register(websocket):
#     USERS.add(websocket)
#     # await notify_users()


# async def unregister(websocket):
#     USERS.remove(websocket)
#     # wait notify_users()


# async def client_handler(websocket, path):
#     print(path)
#     # register(websocket) sends user_event() to websocket
#     await register(websocket)
#     try:
#         #await websocket.send(state_event())
#         async for message in websocket:
#             data = json.loads(message)
#             #print(data)
#             # if data["action"] == "minus":
#             #     STATE["value"] -= 1
#             #     await notify_state()
#             # elif data["action"] == "plus":
#             #     STATE["value"] += 1
#             #     await notify_state()
#             # else:
#             #     logging.error("unsupported event: %s", data)
#     finally:
#         await unregister(websocket)


# start_server = websockets.serve(client_handler, "localhost", 8080)

# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()