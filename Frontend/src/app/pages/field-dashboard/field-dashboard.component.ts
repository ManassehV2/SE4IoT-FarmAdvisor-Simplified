import {
  Component,
  OnInit,
  AfterViewInit,
  ChangeDetectorRef,
} from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { FieldDashboardModel, SensorModel } from '../../models';
import { Chart, registerables } from 'chart.js';
import annotationPlugin from 'chartjs-plugin-annotation';
import { CommonModule } from '@angular/common';
import * as bootstrap from 'bootstrap';
import { FormsModule, NgForm } from '@angular/forms';

@Component({
  selector: 'app-field-dashboard',
  standalone: true,
  templateUrl: './field-dashboard.component.html',
  styleUrls: ['./field-dashboard.component.css'],
  providers: [ApiService],
  imports: [CommonModule, FormsModule],
})
export class FieldDashboardComponent implements OnInit, AfterViewInit {
  fieldData: FieldDashboardModel | null = null;
  daysToCutting: number = 0;
  newSensor = {
    SerialNo: '',
    OptimalGDD: 0,
    Long: 0,
    Lat: 0,
  };

  private weatherChartInstance: Chart | null = null;
  private humidityChartInstance: Chart | null = null;
  selectedSensor: SensorModel | null = null;
  selectedResetDate: string | null = null;
  today: string = new Date().toISOString().split('T')[0];

  constructor(
    private apiService: ApiService,
    private route: ActivatedRoute,
    private cdr: ChangeDetectorRef
  ) {
    Chart.register(...registerables, annotationPlugin);
  }

  ngOnInit(): void {
    const fieldId = this.route.snapshot.paramMap.get('fieldId');
    if (fieldId) {
      this.fetchFieldDashboard(fieldId);
    }
  }

  ngAfterViewInit(): void {
    if (
      this.fieldData &&
      this.fieldData.FieldSensors &&
      this.fieldData.FieldSensors.length > 0
    ) {
      this.renderChart();
    }
  }

  fetchFieldDashboard(fieldId: string): void {
    this.apiService.getFieldDashboard(fieldId).subscribe(
      (data) => {
        this.fieldData = new FieldDashboardModel(data);
        this.calculateDaysToCutting();
        this.cdr.detectChanges();
        this.renderChart();
      },
      (error: any) => {
        console.error('Error fetching field dashboard data:', error);
      }
    );
  }

  createSensor(sensorForm: NgForm): void {
    // Check if the form is valid
    if (sensorForm.invalid) {
      sensorForm.form.markAllAsTouched(); // Highlight all invalid fields
      return;
    }

    const fieldId = this.route.snapshot.paramMap.get('fieldId');
    if (!fieldId) {
      console.error('No Field ID provided.');
      return;
    }

    const payload = {
      FieldId: fieldId,
      ...this.newSensor,
    };

    this.apiService.postData('fields/newsensor', payload).subscribe({
      next: () => {
        console.log('Sensor created successfully.');
        this.closeSensorModal();
        this.fetchFieldDashboard(fieldId); // Refresh the dashboard data
      },
      error: (error: any) => {
        console.error('Error creating sensor:', error);
      },
    });
  }

  openSensorModal(): void {
    const modalElement = document.getElementById(
      'newSensorModal'
    ) as HTMLElement;
    const modalInstance = new bootstrap.Modal(modalElement);
    modalInstance.show();
  }

  closeSensorModal(): void {
    // Reset the form and sensor data
    this.newSensor = {
      SerialNo: '',
      OptimalGDD: 0,
      Long: 0,
      Lat: 0,
    };

    const modalElement = document.getElementById(
      'newSensorModal'
    ) as HTMLElement;
    const modalInstance = bootstrap.Modal.getInstance(modalElement);
    if (modalInstance) {
      modalInstance.hide();
    }
  }

  renderChart(): void {
    if (this.weatherChartInstance) {
      this.weatherChartInstance.destroy();
      this.weatherChartInstance = null;
    }
    if (this.humidityChartInstance) {
      this.humidityChartInstance.destroy();
      this.humidityChartInstance = null;
    }

    if (!this.fieldData || this.fieldData.FieldSensors.length === 0) {
      console.log('No sensors available, skipping chart rendering.');
      return;
    }

    const weatherChartCanvas = document.getElementById(
      'weatherForecastChart'
    ) as HTMLCanvasElement | null;

    const humidityChartCanvas = document.getElementById(
      'humidityForecastChart'
    ) as HTMLCanvasElement | null;

    if (!weatherChartCanvas || !humidityChartCanvas) {
      console.error('Chart canvases not found.');
      return;
    }

    const cuttingDate = this.fieldData.CuttingDateCalculated
      ? new Date(this.fieldData.CuttingDateCalculated)
      : null;

    const forecastDates = this.fieldData.SevenDayTempForecast.map(
      (d) => new Date(d.date)
    );

    const isCuttingDateInRange =
      cuttingDate &&
      cuttingDate >= forecastDates[0] &&
      cuttingDate <= forecastDates[forecastDates.length - 1];

    const cuttingDateLabel = isCuttingDateInRange
      ? cuttingDate.toLocaleDateString('en-US', { weekday: 'short' })
      : null;

    this.weatherChartInstance = new Chart(weatherChartCanvas, {
      type: 'line',
      data: {
        labels: this.fieldData.SevenDayTempForecast.map((d) =>
          new Date(d.date).toLocaleDateString('en-US', { weekday: 'short' })
        ),
        datasets: [
          {
            label: 'Temperature (°C)',
            data: this.smoothData(
              this.fieldData.SevenDayTempForecast.map((d) => d.value),
              3 // Smoothing window
            ),
            borderColor: 'red',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            yAxisID: 'y-temp',
            tension: 0.4, // Smooth curve
          },
          {
            label: 'Cumulative GDD',
            data: this.fieldData.SevenDayGDDForecast.map((d) => d.value),
            borderColor: 'green',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            yAxisID: 'y-gdd',
          },
          {
            label: 'Cutting Date', // Legend for the blue line
            data: [], // No data points, just for legend
            borderColor: 'blue',
            backgroundColor: 'rgba(0, 0, 255, 0.5)',
            borderWidth: 2,
            pointStyle: false,
            tension: 0, // No line curve
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          'y-temp': {
            type: 'linear',
            position: 'left',
            title: {
              display: true,
              text: 'Temperature (°C)',
            },
            suggestedMin: 24.5, // Start of y-axis
            suggestedMax: 26.0, // End of y-axis
          },
          'y-gdd': {
            type: 'linear',
            position: 'right',
            title: {
              display: true,
              text: 'Cumulative GDD',
            },
          },
        },
        plugins: {
          annotation: {
            annotations: cuttingDateLabel
              ? {
                  line1: {
                    type: 'line',
                    xMin: cuttingDateLabel,
                    xMax: cuttingDateLabel,
                    borderColor: 'blue',
                    borderWidth: 2,
                    label: {
                      content: 'Cutting Date',
                      position: 'end',
                      backgroundColor: 'rgba(0, 0, 255, 0.5)',
                      color: 'white',
                    },
                  },
                }
              : {},
          },
        },
      },
    });

    this.humidityChartInstance = new Chart(humidityChartCanvas, {
      type: 'bar',
      data: {
        labels: this.fieldData.SevenDayHumidityForecast.map((d) =>
          new Date(d.date).toLocaleDateString('en-US', { weekday: 'short' })
        ),
        datasets: [
          {
            label: 'Humidity (%)',
            data: this.fieldData.SevenDayHumidityForecast.map((d) => d.value),
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Humidity (%)',
            },
          },
        },
      },
    });
  }

  goBack(): void {
    window.history.back();
  }

  calculateDaysToCutting(): string {
    if (!this.fieldData?.CuttingDateCalculated) {
      return 'Relax, take it easy';
    }

    const cuttingDate = new Date(this.fieldData.CuttingDateCalculated);
    const today = new Date();

    today.setHours(0, 0, 0, 0);
    cuttingDate.setHours(0, 0, 0, 0);

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
  openResetDateModal(sensor: SensorModel): void {
    this.selectedSensor = sensor;
    this.selectedResetDate = null; // Clear previous selection
    const modalElement = document.getElementById(
      'resetDateModal'
    ) as HTMLElement;
    const modalInstance = new bootstrap.Modal(modalElement);
    modalInstance.show();
  }
  updateResetDate(): void {
    if (!this.selectedSensor || !this.selectedResetDate) {
      console.error('Sensor or Reset Date not selected.');
      return;
    }

    const payload = {
      SensorId: this.selectedSensor.SensorId,
      NewResetDate: this.selectedResetDate,
    };

    this.apiService.putData('fields/sensor/resetdate', payload).subscribe({
      next: () => {
        console.log('Sensor reset date updated successfully.');
        this.fetchFieldDashboard(this.route.snapshot.paramMap.get('fieldId')!); // Refresh the dashboard data
        const modalElement = document.getElementById(
          'resetDateModal'
        ) as HTMLElement;
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) {
          modalInstance.hide();
        }
      },
      error: (error: any) => {
        console.error('Error updating sensor reset date:', error);
      },
    });
  }
  smoothData(data: number[], windowSize: number): number[] {
    return data.map((_, index, array) => {
      const start = Math.max(0, index - Math.floor(windowSize / 2));
      const end = Math.min(array.length, index + Math.ceil(windowSize / 2));
      const subset = array.slice(start, end);
      return subset.reduce((sum, value) => sum + value, 0) / subset.length;
    });
  }
}
