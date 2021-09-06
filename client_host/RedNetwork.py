
import threading
import time
import json
import platform
import websocket
import base64

import RedConfig

class RedNetwork:
    def __init__(self, client):
        self.socketEvtHandlerThread = threading.Thread(target = self.socketEvtHandler, args=())
        self.senderThread = threading.Thread(target = self.sender, args=())

        self.config = RedConfig.GetSettings()
    
        self.server = ""
        self.client_id = ""

        self.socket = None
        self.startTime = 0
        self.error = False

        self.running = True
        self.frameQueue = []

        self.client = client

        return

    def start(self):
        self.startTime = time.time()

        self.server = self.config["server"]
        self.client_id = self.config["client_id"]

        self.socketEvtHandlerThread.start()

        return

    def socketEvtHandler(self):

        self.socket = websocket.WebSocketApp(self.server,
                                on_message = self.on_message,
                                on_error = self.on_error,
                                on_close = self.on_close)
        self.socket.on_open = self.on_open
        self.socket.run_forever()
        
        return

    def sendPacket(self, packet):
        packetJson = json.dumps(packet)
        self.socket.send(packetJson)
        return

    def on_open(self, a):
        self.senderThread.start()
        return
    
    def sender(self):
        self.sendHandshake()
        self.sendViewportInfo()
        
        while (self.running):
            # Send a frame
            if (len(self.frameQueue) > 0):
                framePacket = self.frameQueue.pop(0)
                self.sendPacket(framePacket)
            
            # Send Events
            time.sleep(0.01)


        # for i in range(30000):
        #     time.sleep(1)
        #     ws.send("Hello %d" % i)
        # time.sleep(1)
        # ws.close()
        # print "thread terminating..."

        return

    def sendHandshake(self):
        startPacket = {}
        startPacket["type"] = "handshake"
        startPacket["client_type"] = "host"
        startPacket["client_version"] = "1"
        startPacket["client_id"] = self.client_id
        startPacket["start_time"] = self.startTime
        startPacket["os"] = platform.system()
        self.sendPacket(startPacket)
        return

    def sendViewportInfo(self):
        startPacket = {}
        startPacket["type"] = "viewportinfo"
        startPacket["monitor_count"] = 1
        startPacket["current_monitor"] = 0
        startPacket["width"] = self.client.screenResolution[0]
        startPacket["height"] = self.client.screenResolution[1]
        self.sendPacket(startPacket)
        return

    def enqueueFrameSegment(self, rect, frameBytes):
        packet = {}
        b64Str = base64.b64encode(frameBytes.getvalue()).decode()
        packet["type"] = "framesegment"
        packet["data"] = b64Str
        packet["rect"] = {}
        packet["rect"]["left"] = rect[0]
        packet["rect"]["upper"] = rect[1]
        packet["rect"]["right"] = rect[2]
        packet["rect"]["bottom"] = rect[3]
        self.frameQueue.append(packet)
        return

    def on_message(self, ws, message):
        pktObj = json.loads(message)
        self.client.handlePacket(pktObj)
        return

    def on_error(self, ws, error):
        #print(error)
        #self.error = True
        return

    def on_close(self, a, b, c):

        return


