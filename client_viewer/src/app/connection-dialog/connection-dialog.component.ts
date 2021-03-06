import { Component, Input, OnInit } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { RedConnectionInfo } from '../red-remote-client/red-connection-info';

@Component({
  selector: 'app-connection-dialog',
  templateUrl: './connection-dialog.component.html',
  styleUrls: ['./connection-dialog.component.scss']
})
export class ConnectionDialogComponent implements OnInit {

  @Input("connInfo") connInfo: RedConnectionInfo = new RedConnectionInfo();
  @Input("reqPassword") reqPassword: boolean = false;
  @Input("errorText") errorText: string = "";

  public showServerUrl: boolean = true;
  public showClientId: boolean = true;
  public showPassword: boolean = true;

  constructor(public activeModal: NgbActiveModal) {

  }

  ngOnInit() {
    if (this.reqPassword) {
      this.showServerUrl = false;
      this.showClientId = false;
      this.showPassword = true;
    } else {
      this.showServerUrl = !this.connInfo.server;
      this.showClientId = !this.connInfo.targetClientId;
      this.showPassword = false;
    }
  }

}
