# TripIQ: Your Smart Trip Planner

TripIQ is a smart trip planner that helps you organize your travel plans efficiently. This application provides a user-friendly interface to manage your trips, destinations, and schedules.

## Features

- **Plan Your Trips**: Create and manage multiple trips with ease.
- **ESP32 Integration**: Seamlessly connects with your ESP32 device for real-time data and control.
- **User-Friendly Interface**: An intuitive and easy-to-use interface built with PyQt5.

## How to Run

### Using the Executable

1.  Navigate to the `dist` folder.
2.  Double-click on `frontend.exe` to start the application.

### From Source

1.  Ensure you have Python and the required libraries installed.
2.  Run the following command in your terminal:

    ```bash
    python frontend.py
    ```

## Project Structure

- `frontend.py`: The main application file containing the PyQt5 user interface.
- `recieve.py`: Handles the backend logic and communication with the ESP32 device.
- `esp32_controller.ino`: The code for the ESP32 microcontroller.
- `README.md`: This file, providing an overview of the project.
