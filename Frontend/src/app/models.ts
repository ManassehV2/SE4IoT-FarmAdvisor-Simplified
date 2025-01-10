export class FieldDashboardModel {
  FieldName: string;
  Altitude: number;
  CurrentGDD: number;
  OptimalGDD: number;
  CuttingDateCalculated: Date;
  FieldSensors: SensorModel[];
  SevenDayTempForecast: ForecastData[];
  SevenDayGDDForecast: ForecastData[];
  SevenDayHumidityForecast: ForecastData[];

  constructor(data: any) {
    this.FieldName = data.FieldName;
    this.Altitude = data.Altitude;
    this.CurrentGDD = data.CurrentGDD;
    this.OptimalGDD = data.OptimalGDD;
    this.CuttingDateCalculated = data.CuttingDateCalculated;
    this.FieldSensors = data.FieldSensors.map(
      (sensor: any) => new SensorModel(sensor)
    );
    this.SevenDayTempForecast = data.SevenDayTempForecast.map(
      (forecast: any) => new ForecastData(forecast)
    );
    this.SevenDayGDDForecast = data.SevenDayGDDForecast.map(
      (forecast: any) => new ForecastData(forecast)
    );
    this.SevenDayHumidityForecast = data.SevenDayHumidityForecast.map(
      (forecast: any) => new ForecastData(forecast)
    );
  }
}

export class SensorModel {
  SensorId: string;
  SerialNo: string;
  OptimalGDD: number;
  SensorResetDate: Date;
  State: string;

  constructor(data: any) {
    this.SensorId = data.SensorId;
    this.SerialNo = data.SerialNo;
    this.OptimalGDD = data.OptimalGDD;
    this.SensorResetDate = data.SensorResetDate;
    this.State = data.State;
  }
}

export class ForecastData {
  date: string;
  value: number;

  constructor(data: any) {
    this.date = data.date;
    this.value = data.value;
  }
}
