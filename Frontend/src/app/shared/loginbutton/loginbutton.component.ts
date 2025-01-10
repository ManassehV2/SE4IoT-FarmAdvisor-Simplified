import { Component, OnInit } from '@angular/core';
import { AuthService } from '@auth0/auth0-angular';

@Component({
  selector: 'app-loginbutton',
  standalone: true,
  imports: [],
  templateUrl: './loginbutton.component.html',
  styleUrl: './loginbutton.component.css',
})
export class LoginbuttonComponent implements OnInit {
  constructor(public auth: AuthService) {}
  ngOnInit(): void {}

  loginWithRedirect(): void {
    this.auth.loginWithRedirect();
  }
}
