import { Component } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-new-farm-form',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './new-farm-form.component.html',
  styleUrls: ['./new-farm-form.component.css'],
})
export class NewFarmFormComponent {
  form: FormGroup;

  constructor(private fb: FormBuilder, private apiService: ApiService) {
    this.form = this.fb.group({
      farmName: [''],
      location: [''],
    });
  }

  onSubmit() {
    if (this.form.valid) {
      const formData = this.form.value; // Get the form data
      this.apiService.postData('createfarm', formData).subscribe({
        next: (response) => {
          console.log('Response from API:', response);
          console.log(response);
          this.form.reset(); // Reset the form after submission
        },
        error: (error) => {
          console.error('Error posting form data:', error);
          console.log(error);
        },
      });
    } else {
      alert('Form is invalid. Please check the fields.');
    }
  }
}
