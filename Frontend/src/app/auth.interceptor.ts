import { inject } from '@angular/core';
import { HttpInterceptorFn } from '@angular/common/http';
import { AuthService } from '@auth0/auth0-angular';
import { from } from 'rxjs';
import { switchMap } from 'rxjs/operators';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService); // Use inject() for AuthService

  return from(auth.getAccessTokenSilently()).pipe(
    switchMap((token) => {
      if (token) {
        const clonedReq = req.clone({
          setHeaders: {
            Authorization: `Bearer ${token}`,
          },
        });
        return next(clonedReq);
      }
      // Proceed without modification if no token is available
      return next(req);
    })
  );
};
