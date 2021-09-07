
import threading
import time
import math
import json
import hashlib

from io import BytesIO

import pynput

import PIL.ImageGrab
import PIL.ImageChops
import PIL.Image
from mss import mss

import RedNetwork
import RedConfig

class RedClientHost:
    def __init__(self):
        self.config = RedConfig.GetSettings()

        self.screenCaptureThread = threading.Thread(target = self.screenCapture, args=())
        self.screenCaptureLock = threading.Lock()

        self.evtHandlerThread = threading.Thread(target = self.evtHandler, args=())

        self.network = RedNetwork.RedNetwork(self)

        self.running = True
        self.capturing = False
        self.lastTimeStamp = 0
        self.lastTimeStampMs = 0
        self.frameCounter = 0
        self.maxFps = 100

        self.currentFps = 0
        self.currentKbps = 0

        self.screenResolution = (1920, 1080)
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
            currentFrame = self.capture_screenshot() # PIL.ImageGrab.grab()

            diffImg = PIL.ImageChops.difference(self.previousFrame, currentFrame)
            diffRect = diffImg.getbbox()

            if (diffRect is not None):
                diffImgCropped = currentFrame.crop(diffRect)


                if (self.config["reduce_pixel_depth"] == "1"):
                    diffImgCropped = diffImgCropped.point(lambda x: int(x/17)*17)

                diffData = BytesIO()
                diffImgCropped.save(diffData, "JPEG", quality=80)

                #self.byteCounter += diffData.getbuffer().nbytes

                self.screenCaptureLock.acquire()

                self.network.enqueueFrameSegment(diffRect, diffData)

                self.previousFrame = currentFrame

                self.screenCaptureLock.release()

            deltaTime = time.time() - startTime

            # Calculate Frame Rate
            currentSec = round(time.time())
            currentMs = round(time.time() * 1000)
            if (self.lastTimeStamp != currentSec):
                self.currentFps = self.frameCounter
                self.frameCounter = 0
            else:
                self.frameCounter += 1

            if ((currentMs - self.lastTimeStampMs) < (1000 / self.maxFps)):
                timeToWait = ((1000 / self.maxFps) / 1000) - spentTime
                if (timeToWait > 0):
                    time.sleep(timeToWait)

            self.lastTimeStamp = currentSec
            self.lastTimeStampMs = currentMs

        return

    def capture_screenshot(self):
        # Capture entire screen
        with mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            # Convert to PIL/Pillow Image
            return PIL.Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')

    def evtHandler(self):
        while (self.running):
            if (self.network.error):
                self.running = False
            
            time.sleep(0.5)

    def handlePacket(self, pkt):
        if (pkt["type"] == "ready"):
            pass

        if (pkt["type"] == "authcheck"):
            incomingHashpass = pkt["hashpass"]
            incomingClientId = pkt["guest_client_id"]

            password = self.config["password"]
            hashPass = hashlib.sha256(password.encode('utf-8')).hexdigest()

            if (hashPass == incomingHashpass):
                self.network.sendAuthAccept(incomingClientId)
            else:
                self.network.sendAuthDeny(incomingClientId, "Wrong Password")

        if (pkt["type"] == "viewercount"):
            if (pkt["amount"] > 0):
                self.capturing = True
                print("Started Capturing the Screen since there are viewers")
            else:
                self.capturing = False
                print("Stopped Capturing the Screen since there are no viewers")

        if (pkt["type"] == "hid"):
            self.handleHid(pkt)

        return

    def handleHid(self, pkt):
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
                
            self.keyboard.press(nKey);

        if (pkt["evType"] == "keyrelease"):
            nKey = self.resolveKey(pkt["keycode"])
            if (nKey is None):
                return

            self.keyboard.release(nKey)
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

