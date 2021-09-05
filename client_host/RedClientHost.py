
import threading
import time
import math
import json
import base64

import PIL.ImageGrab
import PIL.ImageChops
from io import BytesIO
import PIL.Image

import RedNetwork

import pynput

class RedClientHost:
    def __init__(self):
        self.screenCaptureThread = threading.Thread(target = self.screenCapture, args=())
        self.screenCaptureLock = threading.Lock()

        self.evtHandlerThread = threading.Thread(target = self.evtHandler, args=())

        self.network = RedNetwork.RedNetwork(self)

        self.running = True
        self.capturing = False
        self.lastTimeStamp = 0
        self.lastTimeStampMs = 0
        self.frameCounter = 0
        self.byteCounter = 0
        self.maxFps = 100

        self.currentFps = 0
        self.currentKbps = 0

        self.screenResolution = (1920, 1080)
        self.wChunks = math.ceil(self.screenResolution[0] / 50)
        self.hChunks = math.ceil(self.screenResolution[1] / 50)
        self.chunkSize = (50, 50)

        self.previousFrame = PIL.Image.new("RGB", self.screenResolution)

        self.mouse = pynput.mouse.Controller()
        self.keyboard = pynput.keyboard.Controller()
        return
    
    def start(self):
        self.network.start()

        self.screenCaptureThread.start()
        self.evtHandlerThread.start()

        return
    
    def screenCapture(self):

        while (self.running):
            if (not self.capturing):
                time.sleep(0.5)
                continue
            
            startTime = time.time()

            # Get the Frame
            im = PIL.ImageGrab.grab()

            diffImg = PIL.ImageChops.difference(self.previousFrame, im)
            diffRect = diffImg.getbbox()

            if (diffRect is not None):
                diffImgCropped = im.crop(diffRect)
                #diffImgCropped = diffImgCropped.point(lambda x: int(x/17)*17)

                diffData = BytesIO()
                diffImgCropped.save(diffData, "JPEG", quality=80)
                #im.save(diffData, "JPEG", quality=50)

                self.byteCounter += diffData.getbuffer().nbytes

                self.screenCaptureLock.acquire()

                # Create the  object to be sent
                packet = {}

                b64Str = base64.b64encode(diffData.getvalue()).decode()
                packet["type"] = "framesegment"
                packet["data"] = b64Str
                packet["rect"] = {}
                packet["rect"]["left"] = diffRect[0]
                packet["rect"]["upper"] = diffRect[1]
                packet["rect"]["right"] = diffRect[2]
                packet["rect"]["bottom"] = diffRect[3]
                self.network.frameQueue.append(packet)

                # Set as previous Frame
                self.previousFrame = im

                #print("CAP")

                self.screenCaptureLock.release()

            # Calculate Frame Rate
            currentSec = round(time.time())
            currentMs = round(time.time() * 1000)
            if (self.lastTimeStamp != currentSec):
                self.currentFps = self.frameCounter             # print("FPS: " + str(self.frameCounter))
                self.currentKbps = self.byteCounter / 1024      # print("Kbps: " + str(self.byteCounter / 1024))
                self.frameCounter = 0
                self.byteCounter = 0
            else:
                self.frameCounter += 1
                #self.byteCounter += toAddData.getbuffer().nbytes # + toSubData.getbuffer().nbytes;

            if ((currentMs - self.lastTimeStampMs) < (1000 / self.maxFps)):
                time.sleep((1000 / self.maxFps) / 1000)

            self.lastTimeStamp = currentSec
            self.lastTimeStampMs = currentMs


            #time.sleep(0.01)
        return

    def evtHandler(self):
        while (self.running):
            if (self.network.error):
                self.running = False
            
            time.sleep(0.5)

    def handlePacket(self, pkt):
        if (pkt["type"] == "viewercount"):
            if (pkt["amount"] > 0):
                self.capturing = True
                print("Started Capturing the Screen since there are viewers")
            else:
                print("Stopped Capturing the Screen since there are no viewers")

        if (pkt["type"] == "hid"):
            self.handleHid(pkt)


        return

    def handleHid(self, pkt):
        # type: "hid",
        # input: "mouse",
        # evType: "mousemove",
        # x: cX,
        # y: cY
        if (pkt["input"] == "mouse"):
            self.handleMouseHidPacket(pkt)
        elif (pkt["input"] == "keyboard"):
            self.handleKeyboardHidPacket(pkt)
        
        return

    def handleMouseHidPacket(self, pkt):
        if (pkt["evType"] == "mousemove"):
            cX = pkt["x"]
            cY = pkt["y"]
            self.mouse.position = (cX, cY)
            pass

        if (pkt["evType"] == "mousedown" or pkt["evType"] == "mouseup"):
            cX = pkt["x"]
            cY = pkt["y"]
            btnCode = pkt["btn"]

            btnVal = None
            if (btnCode == 0): btnVal = pynput.mouse.Button.left
            if (btnCode == 1): btnVal = pynput.mouse.Button.middle
            if (btnCode == 2): btnVal = pynput.mouse.Button.right
            
            self.mouse.position = (cX, cY)
            if (pkt["evType"] == "mousedown"):
                self.mouse.press(btnVal)
            elif (pkt["evType"] == "mouseup"):
                self.mouse.release(btnVal)
        
        if (pkt["evType"] == "mousewheel"):
            cX = pkt["x"]
            cY = pkt["y"]
            deltaX = pkt["deltaX"]
            deltaY = pkt["deltaY"]

            self.mouse.position = (cX, cY)
            self.mouse.scroll(deltaX, deltaY)

        return

    def handleKeyboardHidPacket(self, pkt):
        if (pkt["evType"] == "keypress"):
            nKey = self.resolveKey(pkt["keycode"])
            if (nKey is None):
                return
                
            self.keyboard.press(nKey);  # pynput.keyboard.Key.space);

        if (pkt["evType"] == "keyrelease"):
            nKey = self.resolveKey(pkt["keycode"])
            if (nKey is None):
                return

            self.keyboard.release(nKey) # pynput.keyboard.Key.space);
            # type: "hid",
            # input: "keyboard",
            # evType: press ? "keypress" : "keyrelease",
            # keycode: keycode

        return

    def resolveKey(self, incomingKey):
        if (len(incomingKey) == 1):
            return incomingKey
        else:
            if (incomingKey == "Backspace"): return pynput.keyboard.Key.backspace
            elif (incomingKey == "Space"): return pynput.keyboard.Key.space
            elif (incomingKey == "Enter"): return pynput.keyboard.Key.enter
            elif (incomingKey == "Shift"): return pynput.keyboard.Key.shift
            elif (incomingKey == "Control"): return pynput.keyboard.Key.control
            elif (incomingKey == "ArrowLeft"): return pynput.keyboard.Key.left
            elif (incomingKey == "ArrowRight"): return pynput.keyboard.Key.right
            elif (incomingKey == "ArrowUp"): return pynput.keyboard.Key.up
            elif (incomingKey == "ArrowDown"): return pynput.keyboard.Key.down
            elif (incomingKey == "CapsLock"): return pynput.keyboard.Key.caps_lock
            elif (incomingKey == "Home"): return pynput.keyboard.Key.home
            elif (incomingKey == "End"): return pynput.keyboard.Key.end
            elif (incomingKey == "Insert"): return pynput.keyboard.Key.insert
            elif (incomingKey == "Delete"): return pynput.keyboard.Key.delete
            elif (incomingKey == "Escape"): return pynput.keyboard.Key.esc
            elif (incomingKey == "Tab"): return pynput.keyboard.Key.tab
            elif (incomingKey == "PageDown"): return pynput.keyboard.Key.page_down 
            elif (incomingKey == "PageUp"): return pynput.keyboard.Key.page_up
            elif (incomingKey == "Pause"): return pynput.keyboard.Key.pause
            elif (incomingKey == "ScrollLock"): return pynput.keyboard.Key.scroll_lock
            elif (incomingKey == "PrintScreen"): return pynput.keyboard.Key.print_screen 
            elif (incomingKey == "F1"): return pynput.keyboard.Key.f1
            elif (incomingKey == "F2"): return pynput.keyboard.Key.f2
            elif (incomingKey == "F3"): return pynput.keyboard.Key.f3
            elif (incomingKey == "F4"): return pynput.keyboard.Key.f4
            elif (incomingKey == "F5"): return pynput.keyboard.Key.f5
            elif (incomingKey == "F6"): return pynput.keyboard.Key.f6
            elif (incomingKey == "F7"): return pynput.keyboard.Key.f7
            elif (incomingKey == "F8"): return pynput.keyboard.Key.f8
            elif (incomingKey == "F9"): return pynput.keyboard.Key.f9
            elif (incomingKey == "F10"): return pynput.keyboard.Key.f10
            elif (incomingKey == "F11"): return pynput.keyboard.Key.f11
            elif (incomingKey == "F12"): return pynput.keyboard.Key.f12
            elif (incomingKey == "F13"): return pynput.keyboard.Key.f13
            elif (incomingKey == "F14"): return pynput.keyboard.Key.f14
            elif (incomingKey == "F15"): return pynput.keyboard.Key.f15
            elif (incomingKey == "F16"): return pynput.keyboard.Key.f16
            elif (incomingKey == "F17"): return pynput.keyboard.Key.f17
            elif (incomingKey == "F18"): return pynput.keyboard.Key.f18
            elif (incomingKey == "F19"): return pynput.keyboard.Key.f19
            elif (incomingKey == "F20"): return pynput.keyboard.Key.f20
            else:
                print("Unmapped Key was pressed")
                return None

