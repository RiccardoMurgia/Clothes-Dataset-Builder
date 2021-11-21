import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DatasetViewerComponent } from './dataset-viewer.component';

describe('DatasetViewerComponent', () => {
  let component: DatasetViewerComponent;
  let fixture: ComponentFixture<DatasetViewerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DatasetViewerComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DatasetViewerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
