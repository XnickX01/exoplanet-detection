import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule, HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    HttpClientModule
  ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  predictions: any;
  selectedFile: File | null = null;
  imageUrl: string | null = null;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {}

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length) {
      this.selectedFile = input.files[0];
      console.log('Selected file:', this.selectedFile.name);
      this.imageUrl = URL.createObjectURL(this.selectedFile);
      console.log('Image URL:', this.imageUrl);
    }
  }

  onUpload() {
    if (!this.selectedFile) {
      console.error('No file selected.');
      return;
    }

    // Example: read file as text or array buffer
    const reader = new FileReader();
    reader.onload = () => {
      // Here you would parse the file content and produce a numeric array
      // that matches your model's expected shape, e.g., (batch, 128, 128, 1).
      // This example just sends a dummy array.
      const inputData = [
        // One "image" of size 128x128 with 1 channel, filled with zeros
        Array.from({ length: 128 }, () =>
          Array.from({ length: 128 }, () => [0])
        )
      ];

      // Post to the API
      this.http.post<any>('http://localhost:8000/predict', { data: inputData })
      .subscribe({
        next: (response) => {
          console.log('Server Response:', response);
          const rawValue = response.predictions[0][0]; // e.g., 0.921805202960968
          const percentage = (rawValue * 100).toFixed(2) + '%'; // "92.18%"
          this.predictions = percentage;
        },
        error: (err) => {
          console.error('Error:', err);
        }
      });
    };
    // Read the file; pick the read mode you actually need
    reader.readAsArrayBuffer(this.selectedFile);
  }
}