# Group-Saisys

GraphHopper Routing Application with Visual Reports

## Overview

An enhanced GUI application for route planning using the GraphHopper API. Generates beautiful interactive HTML reports with maps, turn-by-turn directions, fuel cost calculations, and calorie estimations.

## Features

- **Interactive GUI** - Easy-to-use Tkinter interface
- **Visual Route Reports** - Interactive HTML reports with Leaflet maps
- **Multiple Vehicle Types** - Support for car, bike, foot, motorcycle, truck, ebike, scooter
- **Fuel Cost Calculations** - Automatic fuel consumption and cost estimation with Philippine market prices
- **Calorie Tracking** - Automatic calorie estimation for active transportation (walking, cycling)
- **E-bike Energy** - Battery consumption estimates for electric bikes
- **Color-coded Directions** - Turn-by-turn instructions with custom icons
- **Dark Mode Support** - Built-in theme options
- **Loading Progress** - Threaded route generation with progress indicator

## Requirements

- Python 3.7+
- GraphHopper API key (free tier available at https://www.graphhopper.com/)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd Group-Saisys
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key:
```bash
# On Windows
set GRAPHHOPPER_API_KEY=your_api_key_here

# On Linux/Mac
export GRAPHHOPPER_API_KEY=your_api_key_here
```

Alternatively, create a `.env` file (see `.env.example`)

## Usage

Run the application:
```bash
python graphhopper.py
```

1. Enter your **Origin** location (e.g., "Manila, Philippines")
2. Enter your **Destination** (e.g., "Quezon City, Philippines")
3. Select a **Vehicle type** from the dropdown
4. Click **Generate Report**

The application will generate an interactive HTML report (`report.html`) and open it automatically in your default browser.

## Default Values

The application uses Philippine market defaults (as of October 2025):

- **Gasoline**: ₱57.20/L
- **Diesel**: ₱55.45/L
- **Fuel Efficiency**: 7.0 L/100km
- **Body Weight** (for calorie calculation): 70kg

## Vehicle Types

- **car** - Standard automobile (gasoline)
- **truck** - Heavy vehicle (diesel)
- **motorcycle** - Two-wheeler (gasoline)
- **bike** - Bicycle (includes calorie estimation)
- **foot** - Walking (includes calorie estimation)
- **ebike** - Electric bicycle (includes energy consumption)
- **scooter** - Motor scooter (gasoline)

## Report Features

Generated reports include:

- Interactive map with route visualization
- Start and end location markers
- Distance (miles and kilometers)
- Estimated duration
- Fuel consumption and cost (for motorized vehicles)
- Calorie expenditure (for active transportation)
- E-bike battery consumption (for ebike mode)
- Detailed turn-by-turn directions with color-coded icons

## API Key

Get your free GraphHopper API key at: https://www.graphhopper.com/

**Important**: Never commit your API key to version control. Use environment variables or a `.env` file.

## License

This project is for educational purposes.

## Credits

- GraphHopper Routing API
- Leaflet for interactive maps
- OpenStreetMap for map data
