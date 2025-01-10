import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoginbuttonComponent } from '../loginbutton/loginbutton.component';
import { LogoutbuttonComponent } from '../logoutbutton/logoutbutton.component';
import { AuthService } from '@auth0/auth0-angular';
import { Observable } from 'rxjs/internal/Observable';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, LoginbuttonComponent, LogoutbuttonComponent],
  templateUrl: './header.component.html',
  styleUrl: './header.component.css',
})
export class HeaderComponent {
  user$: Observable<any>;

  constructor(public auth: AuthService) {
    this.user$ = this.auth.user$; // Subscribe to the user observable
  }
}
