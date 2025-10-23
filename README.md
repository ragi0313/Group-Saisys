

# **Group-Saisys-RouteXplorer**

Your path, redefined.

## **Overview**

**RouteXplorer** is an enhanced routing and visualization web application built on the **GraphHopper API**.
It provides interactive route maps, vehicle-specific KPIs, and turn-by-turn navigation — ideal for transportation and logistics demonstrations in the Philippine context.

This project extends a previous CLI-based routing tool into a fully interactive browser interface with real-time visualization, fuel and energy estimations, and dynamic travel metrics.

---

## **Features**

* **Interactive Web Interface** – Clean and intuitive HTML/CSS/JS front end with live route generation
* **Visual Route Mapping** – Leaflet map display with start and destination markers (pin and green flag)
* **Multiple Vehicle Types** – Supports car, motorcycle, bike, foot, and e-bike routing modes
* **Dynamic KPI Dashboard** – Automatic updates for distance, duration, and vehicle-specific metrics

  * Car/Motorcycle → Fuel (L) and Cost (₱)
  * Bike → Calories and Average Speed
  * Walking → Steps and Calories
  * E-Bike → Energy (Wh/kWh) and Charge Cost
* **Turn-By-Turn Directions** – Icon-based instructions for left, right, u-turn, roundabout, and arrival steps
* **Highlighted Destination** – Final “Arrive at destination” step visually emphasized
* **Dark/Light Mode Support** – Built-in theme toggle
* **Loading Progress** – Animated loader while generating routes

---

## **Requirements**

* Modern browser (Edge, Chrome, or Firefox)
* Internet connection for GraphHopper API access
* GraphHopper API key (free tier available at [https://www.graphhopper.com](https://www.graphhopper.com))

---

## **Installation**

1. Clone this repository:

   ```bash
   git clone git@github.com:ragi0313/Group-Saisys--RouteXplorer.git
   cd Group-Saisys--ProjectXplorer
   ```

2. Install dependencies (if using the Python helper tools):

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

   Alternatively, create a `.env` file (see `.env.example`).

---

## **Usage**

Run the main web file:

```bash
start index.html
```

or open it directly in your browser.

1. Enter your **Origin** (e.g., “Batangas City Hall”)
2. Enter your **Destination** (e.g., “SM City Batangas”)
3. Select a **Vehicle Type** (Car, Motorcycle, Bike, Foot, or E-Bike)
4. Click **Generate Report**

The application will:

* Display a suggested route on the map
* Show a **📍 pin** for origin and **green flag** for destination
* Present detailed KPIs and turn-by-turn directions

---

## **Default Values**

The application uses Philippine market defaults (as of October 2025):

* **Gasoline**: ₱57.20 / L
* **Electricity**: ₱12.00 / kWh
* **Fuel Efficiency**: 7.0 L / 100 km
* **Body Weight**: 70 kg
* **Steps per km**: 1,250

---

## **Report Features**

Generated route reports include:

* Interactive Leaflet map visualization
* Start and end location markers
* Distance (km / mi) and estimated duration
* Fuel consumption and cost (motorized modes)
* Calorie or energy estimation for active transport
* Icon-coded turn instructions
* Highlighted destination step

---

## **Future Enhancements**

* Multi-route comparison (shortest vs scenic)
* Real-time traffic and weather overlays
* Export route summaries (PDF or CSV)
* Optional user profiles with saved routes

---

## **API Key**

Get your free GraphHopper API key at:
[https://www.graphhopper.com](https://www.graphhopper.com)

**Important:** Never commit your API key to version control.
Use environment variables or a `.env` file.

---

## **License**

This project is for educational and research purposes.

---

## **Credits**

* **GraphHopper Routing API** – Routing engine
* **Leaflet** – Interactive mapping
* **OpenStreetMap** – Base map data
* **Group 3 Networking – SAISys Project Team**

---
