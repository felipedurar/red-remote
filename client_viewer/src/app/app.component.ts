import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { NgbModal, NgbModalRef } from '@ng-bootstrap/ng-bootstrap';
import { environment } from 'src/environments/environment';
import { ConnectionDialogComponent } from './connection-dialog/connection-dialog.component';
import { LoadingModalComponent } from './loading-modal/loading-modal.component';
import { RedConnectionInfo } from './red-remote-client/red-connection-info';
import { ConnectionStatusService } from './services/connection-status.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'RedClientViewer';

  public loadingModal: NgbModalRef;
  public queryParams = {};
  public lastErrorReason: string = "";

  constructor(private route: ActivatedRoute, private modalService: NgbModal, private connStatus: ConnectionStatusService) {

  }

  ngOnInit() {
    this.connStatus.authDeny.subscribe((reason) => {
      this.lastErrorReason = "Auth Denied: " + reason;
      this.reqInputs();
    });

    this.reqInputs();
  }

  reqInputs() {
    this.loadingModal = this.modalService.open(LoadingModalComponent, { centered: true, backdrop: false });
    this.loadingModal.componentInstance.text = 'Loading Setting...';
    this.loadingModal.componentInstance.showSpinner = true;

    this.route.queryParams.subscribe(params => {
      this.queryParams = params;
    });

    setTimeout(() => {
      this.resolveInputs(this.queryParams);
    }, 1000);
  }

  uuidv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  resolveInputs(queryParams) {
    let connInfo: RedConnectionInfo = new RedConnectionInfo();
    connInfo.server = environment.server;
    connInfo.clientId = environment.clientId;
    connInfo.password = environment.password;
    connInfo.targetClientId = environment.targetClientId;

    if (environment.allowFromUrl) {
      if (!!queryParams['server']) connInfo.server = queryParams['server'];
      if (!!queryParams['clientId']) connInfo.clientId = queryParams['clientId'];
      if (!!queryParams['password']) connInfo.password = queryParams['password'];
      if (!!queryParams['targetClientId']) connInfo.targetClientId = queryParams['targetClientId'];
    }

    if (!connInfo.clientId)
      connInfo.clientId = this.uuidv4();
    
    let isComplete = !!connInfo.server && !!connInfo.targetClientId && !!connInfo.password;

    this.loadingModal.close();

    if (!isComplete && environment.neverShowDialog) {
      this.loadingModal = this.modalService.open(LoadingModalComponent, { centered: true, size: 'lg', backdrop: false });
      this.loadingModal.componentInstance.text = "Error, unable to get the necessary inputs to connect to the server!";
      this.loadingModal.componentInstance.showSpinner = false;
      return;
    }

    if (!isComplete) {
      const connectionDialog = this.modalService.open(ConnectionDialogComponent, { centered: true, backdrop: false });
      connectionDialog.componentInstance.connInfo = connInfo;
      connectionDialog.componentInstance.errorText = this.lastErrorReason;
      connectionDialog.result.then((res) => {
        if (res) {
          this.connect(connInfo);
        }
      });
      return;
    }

    this.connect(connInfo);
  }

  connect(connInfo: RedConnectionInfo) {
    this.connStatus.connect.next(connInfo);
  }
}
