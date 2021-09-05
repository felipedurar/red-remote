import { Component, Input, OnInit } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-loading-modal',
  templateUrl: './loading-modal.component.html',
  styleUrls: ['./loading-modal.component.scss']
})
export class LoadingModalComponent implements OnInit {
  @Input("text") text: string;
  @Input("showSpinner") showSpinner: boolean = true;

  constructor(public activeModal: NgbActiveModal) { }

  ngOnInit() {
  }

}
