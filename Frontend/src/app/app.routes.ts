import { Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home.component';
import { NewFarmFormComponent } from './pages/new-farm-form/new-farm-form.component';
import { AuthGuard } from '@auth0/auth0-angular';
import { FieldDashboardComponent } from './pages/field-dashboard/field-dashboard.component';

export const routes: Routes = [
  { path: '', component: HomeComponent, canActivate: [AuthGuard] },
  {
    path: 'field-dashboard/:fieldId',
    component: FieldDashboardComponent,
    canActivate: [AuthGuard],
  },
  {
    path: 'new-farm',
    component: NewFarmFormComponent,
    canActivate: [AuthGuard],
  },
];
