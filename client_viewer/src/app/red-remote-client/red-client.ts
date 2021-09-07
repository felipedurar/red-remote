import { RedConnectionInfo } from "./red-connection-info";
import { ViewportInfo } from "./red-viewport";
import * as CryptoJS from "crypto-js";

export class RedClient {
    
    public socket: WebSocket = null;
    public errorCallback: Function = null;

    public connInfo: RedConnectionInfo;

    public offscreenCanvas;
    public canvasCtx;
    public drawCallback: Function = null;
    public authReqCallback: Function = null;
    public authDenyCallback: Function = null;
    public hostClosedConnection: Function = null;
    public viewport: ViewportInfo = { width: 800, height: 600, monitorCount: 1, currentMonitor: 0 };
    public aspectRatioH: number = 800.0 / 600.0;
    public aspectRatioW: number = 600.0 / 800.0;

    public ready: boolean = false;

    constructor() {}

    public connect(connInfo: RedConnectionInfo) {
        this.connInfo = connInfo;

        this.createOffscreenCanvas();

        this.socket = new WebSocket(this.connInfo.server);
        this.socket.onopen = this.onOpen.bind(this);
        this.socket.onmessage = this.onMessage.bind(this);
        this.socket.onerror = this.onError.bind(this);
        this.socket.onclose = this.onClose.bind(this);
    }

    public createOffscreenCanvas() {
        this.offscreenCanvas = document.createElement('canvas');
        this.offscreenCanvas.width = this.viewport.width.toString();
        this.offscreenCanvas.height = this.viewport.height.toString();
        this.canvasCtx = this.offscreenCanvas.getContext('2d');
        this.canvasCtx.fillStyle = 'gray'; //set fill color
        this.canvasCtx.fillRect(0, 0, this.viewport.width, this.viewport.height);
    }

    public onOpen(event) {
        this.sendHandshake();
    }

    public onMessage(event) {
        var pktData = JSON.parse(event.data);
        console.log("Received packet type: " + pktData.type);

        if (pktData.type == "ready") {
            this.ready = true;
        }

        if (pktData.type == "reqauth") {
            if (!!this.authReqCallback)
                this.authReqCallback()
        }

        if (pktData.type == "authdeny") {
            if (!!this.authDenyCallback)
                this.authDenyCallback(pktData.reason)
        }

        if (pktData.type == "hostclosed") {
            this.ready = false;
            if (!!this.hostClosedConnection)
                this.hostClosedConnection()
        }

        // Packets below here must be handled only if this client is ready
        if (!this.ready) {
            console.log("Packet Ignored because this client isn't ready!");
            return;
        }

        if (pktData.type == "framesegment") {
            let cFragment = new Image();
            cFragment.src = 'data:image/jpeg;base64,' + pktData.data;
            cFragment.onload = () => {
                if (!!this.canvasCtx) {
                    this.canvasCtx.fillStyle = 'black'; //set fill color
                    this.canvasCtx.fillRect(pktData.rect.left, pktData.rect.upper, pktData.rect.right - pktData.rect.left, pktData.rect.bottom - pktData.rect.upper);
                    this.canvasCtx.drawImage(cFragment, pktData.rect.left, pktData.rect.upper, pktData.rect.right - pktData.rect.left, pktData.rect.bottom - pktData.rect.upper)
                    this.drawCallback();
                }
                cFragment = null;
            };
            cFragment.onerror = () => {
                console.log("Frame error");
            }

        }

        if (pktData.type == "viewportinfo") {
            this.viewport.width = pktData["width"];
            this.viewport.height = pktData["height"];
            this.viewport.monitorCount = pktData["monitor_count"];
            this.viewport.currentMonitor = pktData["current_monitor"];
            this.aspectRatioH = (this.viewport.width * 1.000) / (this.viewport.height * 1.000);
            this.aspectRatioW = (this.viewport.height * 1.000) / (this.viewport.width * 1.000);
            console.log("Viewport Info Received");

            // Recreate the canvas with the correct size
            this.createOffscreenCanvas();
        }

    }

    public sendHandshake() {
        let pkt = {
            type: "handshake",
            client_type: "guest",
            client_version: "1",
            client_id: this.connInfo.clientId,
            target_client_id: this.connInfo.targetClientId,
            start_time: new Date().getTime(),
            os: "browser"
        };
        this.socket.send(JSON.stringify(pkt));
    }

    public sendAuthCheck(password) {
        let pkt = {
            type: "authcheck",
            hashpass: CryptoJS.SHA256(password).toString()
        };
        this.socket.send(JSON.stringify(pkt));
    }

    public sendMouseMove(cX, cY) {
        let pkt = {
            type: "hid",
            input: "mouse",
            evType: "mousemove",
            x: cX,
            y: cY
        };
        this.socket.send(JSON.stringify(pkt));
    }

    public sendMouseButton(cX, cY, btn, down) {
        let pkt = {
            type: "hid",
            input: "mouse",
            evType: down ? "mousedown" : "mouseup",
            btn: btn,
            x: cX,
            y: cY
        };
        this.socket.send(JSON.stringify(pkt));
    }

    public sendMouseWheel(cX, cY, deltaX, deltaY) {
        let pkt = {
            type: "hid",
            input: "mouse",
            evType: "mousewheel",
            x: cX,
            y: cY,
            deltaX: deltaX,
            deltaY: deltaY
        };
        this.socket.send(JSON.stringify(pkt));
    }

    public sendKeyboardKey(keycode, press) {
        let pkt = {
            type: "hid",
            input: "keyboard",
            evType: press ? "keypress" : "keyrelease",
            keycode: keycode
        };
        this.socket.send(JSON.stringify(pkt));
    }

    public isInViewportBounds(cX, cY) {
        return cX >= 0 && cY >= 0 && cX < this.viewport.width && cY < this.viewport.height;
    }

    public onError(event) {
        console.log("WS Error");
        if (!!this.errorCallback) {
            this.errorCallback();
        }

    }

    public onClose(event) {
        console.log("WS Closed");
        if (!!this.errorCallback) {
            this.errorCallback();
        }

    }

}