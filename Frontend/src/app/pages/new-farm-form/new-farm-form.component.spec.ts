import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NewFarmFormComponent } from './new-farm-form.component';

describe('NewFarmFormComponent', () => {
  let component: NewFarmFormComponent;
  let fixture: ComponentFixture<NewFarmFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NewFarmFormComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NewFarmFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
