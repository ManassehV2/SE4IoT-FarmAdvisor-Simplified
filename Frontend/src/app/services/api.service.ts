import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { FieldDashboardModel } from '../models';

export interface FieldDetail {
  FieldId: string;
  FieldName: string;
  CurrentGDD: number;
  OptimalCuttingDate: string | null;
}

export interface FarmDashboard {
  FarmId: string;
  FarmName: string;
  FarmFields: FieldDetail[];
}

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private baseUrl = 'http://localhost:8000';
  constructor(private http: HttpClient) {}

  getData(endpoint: string): Observable<any> {
    return this.http.get(`${this.baseUrl}`);
  }

  postData(endpoint: string, payload: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/${endpoint}`, payload);
  }
  putData(endpoint: string, payload: any): Observable<any> {
    return this.http.put(`${this.baseUrl}/${endpoint}`, payload);
  }

  deleteData(endpoint: string): Observable<any> {
    return this.http.delete(`${this.baseUrl}/${endpoint}`);
  }

  getFarms(endpoint: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/${endpoint}`);
  }

  // Add a method for fetching the farm dashboard
  getFarmDashboard(): Observable<FarmDashboard[]> {
    return this.http.get<FarmDashboard[]>(
      `${this.baseUrl}/farms/farmdashboard`
    );
  }
  getFieldDashboard(fieldId: string): Observable<FieldDashboardModel> {
    return this.http
      .get(`${this.baseUrl}/fields/fielddashboard${fieldId}`)
      .pipe(map((data) => new FieldDashboardModel(data)));
  }
}
