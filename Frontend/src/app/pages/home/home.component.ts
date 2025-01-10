import { Component, OnInit } from '@angular/core';
import {
  ApiService,
  FarmDashboard,
  FieldDetail,
} from '../../services/api.service';
import { Router } from '@angular/router'; // Import Router
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import * as bootstrap from 'bootstrap';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
})
export class HomeComponent implements OnInit {
  farms: FarmDashboard[] = [];
  selectedFarm: FarmDashboard | null = null;
  newFarm = {
    farmName: '',
    postcode: '',
    city: '',
    country: '',
  };

  newField = {
    Name: '',
    Altitude: null,
  };

  constructor(private apiService: ApiService, private router: Router) {} // Inject Router

  ngOnInit(): void {
    this.fetchFarmDashboard();
  }

  fetchFarmDashboard(): void {
    this.apiService.getFarmDashboard().subscribe({
      next: (data) => {
        this.farms = data;
        if (this.farms.length > 0) {
          this.selectedFarm = this.farms[0];
        }
      },
      error: (error) => {
        console.error('Error fetching farm dashboard:', error);
      },
    });
  }

  onFarmChange(event: Event): void {
    const FarmId = (event.target as HTMLSelectElement).value;
    this.selectedFarm =
      this.farms.find((farm) => farm.FarmId === FarmId) || null;
  }

  navigateToFieldDashboard(fieldId: string): void {
    this.router.navigate([`/field-dashboard/${fieldId}`]); // Navigate to Field Dashboard
  }

  calculateDaysToCutting(optimalCuttingDate: string | null): string {
    if (!optimalCuttingDate) return 'Relax, take it easy';

    const cuttingDate = new Date(optimalCuttingDate);
    const today = new Date();
    const difference = Math.ceil(
      (cuttingDate.getTime() - today.getTime()) / (1000 * 3600 * 24)
    );

    if (difference === 0) {
      return 'Today is your ideal cutting day 🚜';
    } else if (difference > 0) {
      return `Your Optimal Cutting Period is in ${difference} days`;
    } else {
      return 'The cutting period has passed ⏳';
    }
  }
  createFarm(): void {
    this.apiService.postData('farms/newfarm', this.newFarm).subscribe({
      next: (response) => {
        console.log('Farm created successfully:', response);

        // Reload the page
        window.location.reload();
      },
      error: (error) => {
        console.error('Error creating farm:', error);
      },
    });
  }
  createField(): void {
    if (!this.selectedFarm) {
      console.error('No farm selected for creating a field');
      return;
    }

    const payload = {
      Name: this.newField.Name,
      Altitude: this.newField.Altitude,
      FarmId: this.selectedFarm.FarmId,
    };

    this.apiService.postData('fields/newfield', payload).subscribe({
      next: (response) => {
        console.log('Field created successfully:', response);

        // Reset the form
        this.newField = {
          Name: '',
          Altitude: null,
        };

        // Close the modal
        const modal = document.getElementById('newFieldModal') as HTMLElement;
        const modalInstance = bootstrap.Modal.getInstance(modal);
        modalInstance?.hide();

        // Reload the page
        window.location.reload();
      },
      error: (error) => {
        console.error('Error creating field:', error);
      },
    });
  }
}
