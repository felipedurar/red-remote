import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { RemoteClientComponent } from './remote-client/remote-client.component';
import { ConnectionDialogComponent } from './connection-dialog/connection-dialog.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { LoadingModalComponent } from './loading-modal/loading-modal.component';
import { FormsModule } from '@angular/forms';

@NgModule({
  declarations: [
    AppComponent,
    RemoteClientComponent,
    ConnectionDialogComponent,
    LoadingModalComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    AppRoutingModule,
    NgbModule
  ],
  providers: [],
  bootstrap: [AppComponent],
  entryComponents: [
    LoadingModalComponent,
    ConnectionDialogComponent
  ]
})
export class AppModule { }
