import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FieldDashboardComponent } from './field-dashboard.component';

describe('FieldDashboardComponent', () => {
  let component: FieldDashboardComponent;
  let fixture: ComponentFixture<FieldDashboardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FieldDashboardComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FieldDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
