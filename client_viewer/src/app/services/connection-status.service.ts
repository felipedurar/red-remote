import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';
import { RedConnectionInfo } from '../red-remote-client/red-connection-info';

@Injectable({
  providedIn: 'root'
})
export class ConnectionStatusService {

  public connect: Subject<RedConnectionInfo> = new Subject<RedConnectionInfo>();
  public authDeny: Subject<string> = new Subject<string>();

  constructor() { }
}
