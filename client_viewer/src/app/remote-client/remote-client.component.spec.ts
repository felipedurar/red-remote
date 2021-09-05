import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RemoteClientComponent } from './remote-client.component';

describe('RemoteClientComponent', () => {
  let component: RemoteClientComponent;
  let fixture: ComponentFixture<RemoteClientComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RemoteClientComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RemoteClientComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
