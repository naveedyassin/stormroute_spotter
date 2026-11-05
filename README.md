🌦️ StormRoute

AI-Powered Weather-Aware Truck Routing & Safety Platform

StormRoute is an intelligent truck route planning platform designed to help drivers and fleet operators identify safer and more efficient routes using real-time and forecasted weather conditions.

Unlike traditional navigation systems that primarily prioritize distance and travel time, StormRoute evaluates weather risks along different routes to help users make safer transportation decisions.

⸻

🚀 Overview

StormRoute combines route optimization, weather forecasting, geospatial analysis, and intelligent risk assessment to provide weather-aware transportation recommendations.

Users can enter their shipment details, select their departure time, specify cargo weight, and analyze available routes.

The platform evaluates weather conditions at multiple checkpoints along each route and calculates weather risk levels to identify the safest available option.

✨ Key Features

🗺️ Intelligent Route Generation

* Dynamic origin and destination selection.
* Route generation using Mapbox Directions API.
* Alternative route generation.
* Distance and estimated travel time calculations.
* GeoJSON route geometry for map visualization.

🌧️ Weather Intelligence

* Weather forecasting using Open-Meteo.
* Weather analysis at multiple geographical checkpoints.
* Forecasts based on estimated arrival times.
* Weather availability tracking.
* Individual checkpoint risk assessment.

🛡️ Route Safety Analysis

* Weather-based route risk assessment.
* Low, Moderate, and High risk classifications.
* Individual route safety evaluation.
* Comparison of alternative routes.
* Safest-route recommendation instead of simply choosing the shortest route.

🚛 Shipment Planning

* Custom origin and destination.
* Departure date and time.
* Total cargo/load weight.
* Configurable weather checkpoint intervals.
* Automated route analysis.

📊 Route Comparison

* Total route distance.
* Estimated travel duration.
* Number of weather checkpoints.
* Weather availability.
* Overall weather risk assessment.

⸻

🏗️ Technology Stack

Component	Technology
Frontend	React, TypeScript
Backend	Python, Django
API	Django REST Framework
Routing	Mapbox Directions API
Geocoding	Mapbox Geocoding
Weather API	Open-Meteo
HTTP Requests	Python Requests
Version Control	Git & GitHub

⸻

⚙️ System Architecture

             USER
               |
               v
       REACT FRONTEND
               |
               v
       DJANGO REST API
               |
       +-------+-------+
       |               |
       v               v
    MAPBOX          TRIP DATA
       |               |
       v               |
 ROUTE GENERATION      |
       |               |
       +-------+-------+
               |
               v
       ROUTE CHECKPOINTS
               |
               v
        OPEN-METEO API
               |
               v
       WEATHER ANALYSIS
               |
               v
        RISK CALCULATION
               |
               v
       ROUTE COMPARISON
               |
               v
      SAFEST ROUTE RESULT
               |
               v
        REACT FRONTEND

⸻

📂 Project Structure

stormroute/
│
├── backend/
│   ├── routing/
│   │   ├── services/
│   │   │   ├── directions.py
│   │   │   └── geocoding.py
│   │   │
│   │   └── ...
│   │
│   ├── weather/
│   │   ├── services/
│   │   │   ├── forecast.py
│   │   │   └── risk.py
│   │   │
│   │   └── ...
│   │
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── .gitignore
└── README.md

The structure above represents the main application components; individual files may vary.

⸻

🛠️ Installation & Setup

Prerequisites

Make sure you have installed:

* Python 3.10+
* Node.js
* npm
* Git
* Mapbox API access token

1. Clone the repository

git clone YOUR_GITHUB_REPOSITORY_URL
cd stormroute

2. Backend Setup

Navigate to the backend:

cd backend

Create a virtual environment:

python3 -m venv venv

Activate it on macOS/Linux:

source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

3. Environment Variables

Create a .env file inside the backend directory.

MAPBOX_ACCESS_TOKEN=your_mapbox_access_token

Add any additional environment variables required by your Django configuration.

Important: Never commit API keys, passwords, or secret credentials to GitHub.

4. Run Database Migrations

python manage.py migrate

5. Start Backend

python manage.py runserver

Backend development server:

http://127.0.0.1:8000/

6. Frontend Setup

Open another terminal:

cd frontend

Install dependencies:

npm install

Start the frontend:

npm run dev

Open the local development URL displayed in your terminal.

⸻

🔄 How StormRoute Works

Step 1: Shipment Information

Users enter:

* Origin
* Destination
* Departure date
* Departure time
* Total shipment weight
* Weather checkpoint interval

Step 2: Route Generation

StormRoute sends the geographical coordinates to the routing service to generate available driving routes.

Step 3: Checkpoint Generation

Each route is divided into multiple geographical checkpoints based on the selected checkpoint interval.

Step 4: Weather Forecasting

The system retrieves weather forecasts for individual checkpoints using Open-Meteo.

Step 5: Risk Assessment

Weather conditions are evaluated to determine the risk level at each checkpoint.

Step 6: Route Recommendation

Available routes are compared using their weather risk, distance, and estimated duration.

The system recommends the safest available route rather than automatically selecting the shortest route.

⸻

🎯 Project Goals

StormRoute aims to improve transportation safety through intelligent weather-aware route planning.

Our long-term vision includes:

* AI-powered predictive route optimization.
* Advanced weather-risk modelling.
* Real-time severe weather alerts.
* Road condition and accident-risk integration.
* Fleet management capabilities.
* Cargo-aware route optimization.
* Live vehicle tracking.
* Intelligent transportation analytics.

⸻

🔮 Future Improvements

Feature	Status
Dynamic origin/destination	Implemented
Mapbox route generation	Implemented
Weather API integration	Implemented
Weather checkpoints	Implemented
Weather risk assessment	Implemented
Route safety comparison	In development
Three alternative route options	Planned
Interactive route visualization	Planned
Real-time severe weather alerts	Planned
AI predictive risk modelling	Planned
Fleet management dashboard	Planned

Feature status should be updated as development progresses.

⸻

🌍 Vision

We believe transportation decisions should consider more than just distance and travel time.

StormRoute aims to make every journey smarter, safer, and more predictable by combining intelligent routing with weather forecasting and risk analysis.

Don’t just find the fastest route. Find the safest route.

⸻

👨‍💻 Development

StormRoute is an actively developed project focused on intelligent transportation, weather-aware logistics, and route safety optimization.

Contributions, suggestions, and feedback are welcome.

⸻

📄 License

A license has not yet been specified. Please contact the repository owner regarding usage and distribution permissions.