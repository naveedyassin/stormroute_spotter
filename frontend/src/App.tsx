import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import {
  CloudSun,
  ShieldCheck,
  Truck,
  Map,
  Menu,
  Bell,
  Navigation,
  Clock,
  Route as RouteIcon,
  AlertTriangle,
  CheckCircle2,
  Cloud,
  LoaderCircle,
  MapPin,
  Gauge,
} from "lucide-react";

import TripForm, { type TripData } from "./components/TripForm";

import "leaflet/dist/leaflet.css";
import "./App.css";

interface Checkpoint {
  checkpoint_id?: number;
  longitude: number;
  latitude: number;
  distance_miles?: number;
  estimated_arrival?: string;
  risk_level?: string;
  risk_rank?: string;
  weather?: {
    temperature?: number;
    precipitation?: number;
    wind_speed?: number;
    weather_code?: number;
  };
}

interface RouteResult {
  route_id: string;
  route_name?: string;
  distance_miles?: number;
  distance_km?: number;
  duration_seconds?: number;
  duration_hours?: number;
  geometry?: {
    type: string;
    coordinates: [number, number][];
  };
  checkpoints?: Checkpoint[];
  checkpoint_count?: number;
  weather_available?: boolean;
  weather_coverage?: number;
  safety_score?: number | null;
  worst_risk?: string;
  average_risk?: number;
}

interface TripApiResponse {
  success: boolean;
  message?: string;
  error?: string;
  trip_id?: string;
  status?: string;
  total_routes?: number;
  recommended_route_id?: string;
  recommendation_reason?: string;
  routes?: RouteResult[];
}

const API_URL = "http://127.0.0.1:8000/api/trips/"; 
/*local development:http://127.0.0.1:8000*/


const riskColor = (risk?: string) => {
  switch (risk?.toLowerCase()) {
    case "low":
      return "#16a36a";
    case "moderate":
      return "#e5a000";
    case "high":
      return "#ed8426";
    case "severe":
    case "no travel":
      return "#dc3545";
    default:
      return "#8b95a7";
  }
};

function RouteMap({
  route,
}: {
  route: RouteResult | undefined;
}) {
  const mapElement = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mapElement.current) return;

    const map = L.map(mapElement.current, {
      zoomControl: true,
      scrollWheelZoom: true,
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map);

    const coordinates = route?.geometry?.coordinates;

    if (coordinates && coordinates.length > 1) {
      const latLngs = coordinates.map(([longitude, latitude]) => [
        latitude,
        longitude,
      ] as L.LatLngExpression);

      const routeLine = L.polyline(latLngs, {
        color: "#246bfd",
        weight: 6,
        opacity: 0.85,
      }).addTo(map);

      const bounds = routeLine.getBounds();

      route.checkpoints?.forEach((checkpoint, index) => {
        if (
          typeof checkpoint.latitude !== "number" ||
          typeof checkpoint.longitude !== "number"
        ) {
          return;
        }

        const risk =
          checkpoint.risk_level ??
          checkpoint.risk_rank ??
          "Unavailable";

        const marker = L.circleMarker(
          [checkpoint.latitude, checkpoint.longitude],
          {
            radius: 8,
            color: "#ffffff",
            weight: 2,
            fillColor: riskColor(risk),
            fillOpacity: 1,
          }
        );

        marker.bindPopup(`
          <div class="map-popup">
            <strong>Checkpoint ${index + 1}</strong>
            <p>Risk: <b>${risk}</b></p>
            <p>Distance: ${checkpoint.distance_miles ?? "N/A"} miles</p>
            <p>Arrival: ${checkpoint.estimated_arrival ?? "N/A"}</p>
          </div>
        `);

        marker.addTo(map);
      });

      map.fitBounds(bounds, { padding: [35, 35] });
    } else {
      map.setView([20, 0], 2);
    }

    setTimeout(() => map.invalidateSize(), 100);

    return () => {
      map.remove();
    };
  }, [route]);

  return <div className="map-container" ref={mapElement} />;
}

function App() {
  const [trip, setTrip] = useState<TripData | null>(null);
  const [result, setResult] = useState<TripApiResponse | null>(null);
  const [selectedRouteId, setSelectedRouteId] = useState("");
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleTripSubmit = async (data: TripData) => {
    setTrip(data);
    setResult(null);
    setSelectedRouteId("");
    setApiError("");
    setLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          origin: data.origin,
          destination: data.destination,
          departure_date: data.departureDate,
          departure_time: data.departureTime,
          load_weight: data.loadWeight,
          checkpoint_interval: data.checkpointInterval,
        }),
      });

      const responseData: TripApiResponse = await response.json();

      if (!response.ok || !responseData.success) {
        throw new Error(
          responseData.message ||
          responseData.error ||
          "Route analysis failed."
        );
      }

      setResult(responseData);

      const recommended = responseData.routes?.find(
        (route) => route.route_id === responseData.recommended_route_id
      );

      setSelectedRouteId(
        recommended?.route_id ??
        responseData.routes?.[0]?.route_id ??
        ""
      );
    } catch (error) {
      setApiError(
        error instanceof Error
          ? error.message
          : "Unable to connect to StormRoute backend."
      );
    } finally {
      setLoading(false);
    }
  };

  const selectedRoute = result?.routes?.find(
    (route) => route.route_id === selectedRouteId
  );

  const recommendedRoute = result?.routes?.find(
    (route) => route.route_id === result.recommended_route_id
  );

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileMenuOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-icon">
            <CloudSun size={25} />
          </div>
          <span>Storm<span>Route</span></span>
        </div>

        <div className="sidebar-label">WORKSPACE</div>

        <nav>
          <a className="nav-item active" href="#planner">
            <Map size={19} />
            Route Planner
          </a>

          <a className="nav-item" href="#safety">
            <ShieldCheck size={19} />
            Safety Intelligence
          </a>

          <a className="nav-item" href="#fleet">
            <Truck size={19} />
            Fleet Overview
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-status">
            <span className="status-dot" />
            System operational
          </div>
          <small>STORMROUTE v1.0</small>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <button
            className="mobile-menu"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            <Menu size={21} />
          </button>

          <span className="breadcrumb">
            Workspace / Route Planner
          </span>

          <div className="topbar-right">
            <button className="notification" aria-label="Notifications">
              <Bell size={19} />
            </button>
            <div className="avatar">SR</div>
          </div>
        </header>

        <section className="page-content" id="planner">
          <div className="page-heading">
            <div>
              <span className="eyebrow">
                INTELLIGENT TRANSPORTATION PLATFORM
              </span>
              <h1>Weather-aware routing</h1>
              <p>
                Analyze road conditions, compare alternative routes,
                and make safer transportation decisions.
              </p>
            </div>

            <div className="live-badge">
              <span className="status-dot" />
              System online
            </div>
          </div>

          <div className="dashboard-grid">
            <section className="configuration-panel">
              <TripForm onSubmit={handleTripSubmit} />

              {trip && (
                <div className="trip-card">
                  <div className="panel-heading">
                    <Navigation size={18} />
                    <h3>Current journey</h3>
                  </div>

                  <div className="journey-point">
                    <span className="origin-dot" />
                    <div>
                      <small>ORIGIN</small>
                      <strong>{trip.origin}</strong>
                    </div>
                  </div>

                  <div className="journey-line" />

                  <div className="journey-point">
                    <span className="destination-dot" />
                    <div>
                      <small>DESTINATION</small>
                      <strong>{trip.destination}</strong>
                    </div>
                  </div>
                </div>
              )}

              {loading && (
                <div className="loading-card">
                  <LoaderCircle className="spin" size={24} />
                  <div>
                    <strong>Analyzing your journey</strong>
                    <p>Generating routes and evaluating weather conditions.</p>
                  </div>
                </div>
              )}

              {apiError && (
                <div className="error-card" role="alert">
                  <AlertTriangle size={21} />
                  <div>
                    <strong>Analysis failed</strong>
                    <p>{apiError}</p>
                  </div>
                </div>
              )}
            </section>

            <section className="map-panel">
              <div className="panel-top">
                <div>
                  <span className="eyebrow">LIVE ROUTE VISUALIZATION</span>
                  <h2>Journey map</h2>
                </div>

                <span className="map-tag">
                  <MapPin size={14} />
                  Interactive map
                </span>
              </div>

              <RouteMap route={selectedRoute} />

              <div className="map-legend">
                <span><i className="legend-dot low" /> Low</span>
                <span><i className="legend-dot moderate" /> Moderate</span>
                <span><i className="legend-dot high" /> High</span>
                <span><i className="legend-dot severe" /> Severe</span>
              </div>
            </section>
          </div>

          {result && (
            <section className="results-section" id="safety">
              <div className="results-heading">
                <div>
                  <span className="eyebrow">ANALYSIS REPORT</span>
                  <h2>Route intelligence</h2>
                  <p>
                    {result.total_routes ?? result.routes?.length ?? 0}
                    {" "}alternative routes analyzed.
                  </p>
                </div>

                <div className="completed-badge">
                  <CheckCircle2 size={16} />
                  Analysis completed
                </div>
              </div>

              <div className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-icon blue">
                    <RouteIcon size={21} />
                  </div>
                  <span>Total routes</span>
                  <strong>
                    {result.total_routes ?? result.routes?.length ?? 0}
                  </strong>
                </div>

                <div className="metric-card">
                  <div className="metric-icon green">
                    <ShieldCheck size={21} />
                  </div>
                  <span>Recommended route</span>
                  <strong>
                    {recommendedRoute
                      ? recommendedRoute.route_name ?? recommendedRoute.route_id
                      : "Not available"}
                  </strong>
                </div>

                <div className="metric-card">
                  <div className="metric-icon orange">
                    <Cloud size={21} />
                  </div>
                  <span>Weather checkpoints</span>
                  <strong>
                    {selectedRoute?.checkpoint_count ??
                      selectedRoute?.checkpoints?.length ??
                      0}
                  </strong>
                </div>

                <div className="metric-card">
                  <div className="metric-icon purple">
                    <Clock size={21} />
                  </div>
                  <span>Estimated duration</span>
                  <strong>
                    {selectedRoute?.duration_hours != null
                      ? `${selectedRoute.duration_hours.toFixed(2)} hrs`
                      : selectedRoute?.duration_seconds
                        ? `${(selectedRoute.duration_seconds / 3600).toFixed(2)} hrs`
                        : "N/A"}
                  </strong>
                </div>
              </div>

              {result.recommendation_reason && (
                <div className="recommendation-banner">
                  <ShieldCheck size={23} />
                  <div>
                    <strong>StormRoute recommendation</strong>
                    <p>{result.recommendation_reason}</p>
                  </div>
                </div>
              )}

              <div className="route-comparison">
                <div className="section-title">
                  <div>
                    <h3>Available routes</h3>
                    <p>Select a route to inspect its checkpoints on the map.</p>
                  </div>
                </div>

                <div className="route-cards">
                  {result.routes?.map((route, index) => {
                    const isRecommended =
                      route.route_id === result.recommended_route_id;

                    const isSelected =
                      route.route_id === selectedRouteId;

                    return (
                      <button
                        type="button"
                        key={route.route_id}
                        className={`route-card ${isSelected ? "selected" : ""}`}
                        onClick={() => setSelectedRouteId(route.route_id)}
                      >
                        <div className="route-card-top">
                          <div className="route-number">
                            {index + 1}
                          </div>

                          <div className="route-card-name">
                            <strong>
                              {route.route_name ?? `Route ${index + 1}`}
                            </strong>
                            <span>{route.route_id}</span>
                          </div>

                          {isRecommended && (
                            <span className="recommended-badge">
                              <ShieldCheck size={13} />
                              Safest
                            </span>
                          )}
                        </div>

                        <div className="route-stats">
                          <div>
                            <span>Distance</span>
                            <strong>
                              {route.distance_miles != null
                                ? `${route.distance_miles} mi`
                                : route.distance_km != null
                                  ? `${route.distance_km} km`
                                  : "N/A"}
                            </strong>
                          </div>

                          <div>
                            <span>Duration</span>
                            <strong>
                              {route.duration_hours != null
                                ? `${route.duration_hours.toFixed(2)} hrs`
                                : route.duration_seconds
                                  ? `${(route.duration_seconds / 3600).toFixed(2)} hrs`
                                  : "N/A"}
                            </strong>
                          </div>

                          <div>
                            <span>Checkpoints</span>
                            <strong>
                              {route.checkpoint_count ??
                                route.checkpoints?.length ??
                                0}
                            </strong>
                          </div>
                        </div>

                        <div className="route-weather">
                          <span>Weather coverage</span>
                          <strong>
                            {route.weather_coverage != null
                              ? `${route.weather_coverage.toFixed(0)}%`
                              : route.weather_available
                                ? "Available"
                                : "Unavailable"}
                          </strong>
                        </div>

                        <div className="route-card-footer">
                          <span>
                            <i
                              className="legend-dot"
                              style={{
                                background: riskColor(route.worst_risk),
                              }}
                            />
                            Worst risk: {route.worst_risk ?? "Unknown"}
                          </span>

                          <span className="inspect-label">
                            {isSelected ? "Viewing route" : "View route"}
                          </span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {selectedRoute && (
                <div className="checkpoint-section">
                  <div className="section-title">
                    <div>
                      <h3>Weather checkpoints</h3>
                      <p>
                        {selectedRoute.route_name ?? selectedRoute.route_id}
                        {" "}— weather risk along the journey.
                      </p>
                    </div>
                    <span className="checkpoint-count">
                      {selectedRoute.checkpoints?.length ?? 0} checkpoints
                    </span>
                  </div>

                  <div className="checkpoint-list">
                    {selectedRoute.checkpoints?.map((checkpoint, index) => {
                      const risk =
                        checkpoint.risk_level ??
                        checkpoint.risk_rank ??
                        "Unavailable";

                      return (
                        <div className="checkpoint-row" key={index}>
                          <div className="checkpoint-number">
                            {index + 1}
                          </div>

                          <div className="checkpoint-info">
                            <strong>Checkpoint {index + 1}</strong>
                            <span>
                              {checkpoint.distance_miles != null
                                ? `${checkpoint.distance_miles} miles from origin`
                                : "Route checkpoint"}
                            </span>
                          </div>

                          <span
                            className="risk-badge"
                            style={{
                              color: riskColor(risk),
                              background: `${riskColor(risk)}18`,
                            }}
                          >
                            {risk}
                          </span>
                        </div>
                      );
                    })}

                    {!selectedRoute.checkpoints?.length && (
                      <div className="empty-checkpoints">
                        No weather checkpoints are available for this route.
                      </div>
                    )}
                  </div>
                </div>
              )}
            </section>
          )}

          {!result && !loading && !apiError && (
            <div className="empty-state">
              <div className="empty-icon">
                <Gauge size={30} />
              </div>
              <h3>Your route intelligence starts here</h3>
              <p>
                Configure a journey to visualize alternative routes,
                inspect weather conditions and identify safer travel options.
              </p>
            </div>
          )}

          <footer className="footer">
            <span>© 2026 StormRoute</span>
            <span>Smarter Routes. Safer Deliveries.</span>
          </footer>
        </section>
      </main>
    </div>
  );
}

export default App;