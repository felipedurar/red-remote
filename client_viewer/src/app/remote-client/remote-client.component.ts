import { ChangeDetectorRef, Component, ElementRef, Input, OnInit, ViewChild } from '@angular/core';
import { RedClient } from '../red-remote-client/red-client';
import { RedConnectionInfo } from '../red-remote-client/red-connection-info';
import { ConnectionStatusService } from '../services/connection-status.service';

@Component({
  selector: 'app-remote-client',
  templateUrl: './remote-client.component.html',
  styleUrls: ['./remote-client.component.scss']
})
export class RemoteClientComponent implements OnInit {
  @ViewChild('viewport', { static: false }) viewportEle: ElementRef;

  public connInfo: RedConnectionInfo;
  public redClient: RedClient;

  public currentStatus = 1;
  public viewport;
  public viewportCtx;

  public currentCanvasSize = { width: 800, height: 600 }
  public lastCalculatedBounds = { x: 0, y: 0, w: 1, h: 1 }

  constructor(private connStatus: ConnectionStatusService, private _elementRef: ElementRef, private cdr: ChangeDetectorRef) { }

  ngOnInit() {
    this.detachContextMenu();
    this.setupEvents();
  }

  setupEvents() {
    this.connStatus.connect.subscribe(this.startConnection.bind(this));
    window.addEventListener('resize', this.onResize.bind(this), false);

    // All events handler
    // From: https://stackoverflow.com/questions/27321672/listen-for-all-events-in-javascript/48388878
    Object.keys(window).forEach(key => {
      if (/^on/.test(key)) {
        window.addEventListener(key.slice(2), event => {
          this.eventHandler(key, event);
        });
      }
    });
  }

  startConnection(connInfo: RedConnectionInfo) {
    this.connInfo = connInfo;
    this.currentStatus = 10;
    //this.cdr.detectChanges();

    setTimeout(() => {
      this.viewport = this.viewportEle.nativeElement;
      this.viewport.style.width = window.innerWidth;
      this.viewport.style.height = window.innerHeight;
      this.currentCanvasSize = { width: window.innerWidth, height: window.innerHeight }
      this.viewportCtx = this.viewport.getContext('2d');

      this.redClient = new RedClient();
      this.redClient.errorCallback = this.onError.bind(this);
      this.redClient.drawCallback = this.onDraw.bind(this);
      this.redClient.connect(this.connInfo);
    }, 1000);


  }

  onResize() {
    if (!!this.viewport) {
      this.viewport.width = window.innerWidth;
      this.viewport.height = window.innerHeight;
      this.currentCanvasSize = { width: window.innerWidth, height: window.innerHeight }
    } else {
      console.log("NULL VP")
    }
  }

  onError() {
    console.log("CLI Error");
    this.currentStatus = 1;
  }

  onDraw() {
    if (!!this.viewportCtx) {
      this.lastCalculatedBounds.w = this.redClient.aspectRatioH * this.currentCanvasSize.height; //  this.currentCanvasSize.width;
      this.lastCalculatedBounds.h = this.currentCanvasSize.height; // this.redClient.aspectRatio * nWidth;
      if (this.lastCalculatedBounds.w > this.currentCanvasSize.width + 5) {
        this.lastCalculatedBounds.w = this.currentCanvasSize.width;
        this.lastCalculatedBounds.h = this.redClient.aspectRatioW * this.currentCanvasSize.width;
      }

      this.lastCalculatedBounds.x = (this.currentCanvasSize.width / 2.0) - (this.lastCalculatedBounds.w / 2.0);
      this.lastCalculatedBounds.y = (this.currentCanvasSize.height / 2.0) - (this.lastCalculatedBounds.h / 2.0);

      this.viewportCtx.drawImage(this.redClient.offscreenCanvas, this.lastCalculatedBounds.x, this.lastCalculatedBounds.y, this.lastCalculatedBounds.w, this.lastCalculatedBounds.h);
    }
  }

  calculateRemoteMousePos(cX, cY) {
    let rX = cX - this.lastCalculatedBounds.x;
    let rY = cY - this.lastCalculatedBounds.y;
    rX = ((rX * 1.0) * (this.redClient.viewport.width * 1.0)) / (this.lastCalculatedBounds.w * 1.0);
    rY = ((rY * 1.0) * (this.redClient.viewport.height * 1.0)) / (this.lastCalculatedBounds.h * 1.0);
    return { x: rX, y: rY };
  }

  eventHandler(key, event) {
    if (!this.redClient) return;

    //console.log(key, event);
    if (key == "onmousemove") {
      let remotePos = this.calculateRemoteMousePos(event.x, event.y);
      //console.log(remotePos);

      if (this.redClient.isInViewportBounds(remotePos.x, remotePos.y))
        this.redClient.sendMouseMove(remotePos.x, remotePos.y);
      
      event.preventDefault();
    }
    
    if (key == "onmouseout") {}
    if (key == "onmouseover") {}
    if (key == "onmousedown") {
      let remotePos = this.calculateRemoteMousePos(event.x, event.y);

      if (this.redClient.isInViewportBounds(remotePos.x, remotePos.y))
        this.redClient.sendMouseButton(remotePos.x, remotePos.y, event.button, true);
      
      event.preventDefault();
    }
    if (key == "onmouseup") {
      let remotePos = this.calculateRemoteMousePos(event.x, event.y);
      
      if (this.redClient.isInViewportBounds(remotePos.x, remotePos.y))
        this.redClient.sendMouseButton(remotePos.x, remotePos.y, event.button, false);
      
      event.preventDefault();
    }
    if (key == "onwheel") {
      let remotePos = this.calculateRemoteMousePos(event.x, event.y);
      let deltaScroll = { deltaX: event.deltaX / 100.0, deltaY: -(event.deltaY / 100.0) }
      
      if (this.redClient.isInViewportBounds(remotePos.x, remotePos.y))
        this.redClient.sendMouseWheel(remotePos.x, remotePos.y, deltaScroll.deltaX, deltaScroll.deltaY);
    }
    if (key == "onclick") {
      let cX = event.x;
      let cY = event.y;
      let btn = event.button;
    }
    if (key == "onkeydown") {
      let code = event.code;  // "KeyG"
      let keyCode = event.keyCode;  // 71
      let key = event.key;  // "g"
      this.redClient.sendKeyboardKey(key, true);
      event.preventDefault();
    }
    if (key == "onkeyup") {
      let code = event.code;  // "KeyG"
      let keyCode = event.keyCode;  // 71
      let key = event.key;  // "g"
      this.redClient.sendKeyboardKey(key, false);
      event.preventDefault();
    }
  }

  detachContextMenu() {
    // Based On Radek Benkel's and dota2pro's answear:
    // https://stackoverflow.com/questions/4909167/how-to-add-a-custom-right-click-menu-to-a-webpage
    if (document.addEventListener) {
      document.addEventListener('contextmenu', function (e) {
        //component.eventHandler("cfContextMenu", e, true);
        e.preventDefault();
      }, false);
    } else {
      if ((document as any).attachEvent) {
        (document as any).attachEvent('oncontextmenu', function (e) {
          //component.eventHandler("cfContextMenu", e, true);
          window.event.returnValue = false;
        });
      }
    }
  }

}
