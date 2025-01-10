import { Component, OnInit } from '@angular/core';
import { AuthService } from '@auth0/auth0-angular';

@Component({
  selector: 'app-logoutbutton',
  standalone: true,
  imports: [],
  templateUrl: './logoutbutton.component.html',
  styleUrl: './logoutbutton.component.css',
})
export class LogoutbuttonComponent implements OnInit {
  constructor(public auth: AuthService) {}

  ngOnInit(): void {}

  logout(): void {
    this.auth.logout({ logoutParams: { returnTo: window.location.origin } });
  }
}
