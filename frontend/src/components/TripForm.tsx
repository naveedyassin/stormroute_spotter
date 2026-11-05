import { useState, type FormEvent } from "react";
import {
  MapPin,
  Navigation,
  CalendarDays,
  Clock3,
  Weight,
  Route,
  ArrowDownUp,
  ShieldCheck,
  ChevronRight,
  Zap,
  Gauge,
  Info,
  Package,
  Sparkles,
} from "lucide-react";

export interface TripData {
  origin: string;
  destination: string;
  departureDate: string;
  departureTime: string;
  loadWeight: number;
  checkpointInterval: number;
}

interface TripFormProps {
  onSubmit: (data: TripData) => void;
}

const intervals = [
  {
    value: 10,
    title: "Detailed",
    subtitle: "Every 10 miles",
    description: "More frequent weather checks",
    icon: ShieldCheck,
  },
  {
    value: 25,
    title: "Balanced",
    subtitle: "Every 25 miles",
    description: "Recommended for most trips",
    icon: Gauge,
  },
  {
    value: 50,
    title: "Extended",
    subtitle: "Every 50 miles",
    description: "Fewer weather checkpoints",
    icon: Zap,
  },
];

function TripForm({ onSubmit }: TripFormProps) {
  const [origin, setOrigin] = useState("New York");
  const [destination, setDestination] = useState("Boston");
  const [departureDate, setDepartureDate] = useState("2026-11-20");
  const [departureTime, setDepartureTime] = useState("04:22");
  const [loadWeight, setLoadWeight] = useState("14000");
  const [checkpointInterval, setCheckpointInterval] = useState(25);
  const [error, setError] = useState("");

  const handleSwap = () => {
    setOrigin(destination);
    setDestination(origin);
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");

    if (!origin.trim() || !destination.trim()) {
      setError("Please enter both origin and destination.");
      return;
    }

    if (origin.trim().toLowerCase() === destination.trim().toLowerCase()) {
      setError("Origin and destination cannot be the same.");
      return;
    }

    const weight = Number(loadWeight);

    if (!Number.isFinite(weight) || weight <= 0) {
      setError("Please enter a valid cargo weight.");
      return;
    }

    if (!departureDate || !departureTime) {
      setError("Please select a departure date and time.");
      return;
    }

    const departure = new Date(`${departureDate}T${departureTime}`);

    if (Number.isNaN(departure.getTime()) || departure <= new Date()) {
      setError("Please select a future departure date and time.");
      return;
    }

    onSubmit({
      origin: origin.trim(),
      destination: destination.trim(),
      departureDate,
      departureTime,
      loadWeight: weight,
      checkpointInterval,
    });
  };

  return (
    <form className="journey-form" onSubmit={handleSubmit}>
      <div className="journey-form-header">
        <div>
          <div className="form-eyebrow">
            <Sparkles size={13} />
            SMART ROUTE PLANNING
          </div>

          <h2>Plan your journey</h2>

          <p>
            Configure your shipment and let StormRoute identify
            safer travel options.
          </p>
        </div>

        <div className="form-header-icon">
          <Navigation size={23} />
        </div>
      </div>

      <div className="form-divider" />

      {/* ROUTE SECTION */}

      <div className="form-section-heading">
        <div className="form-section-icon">
          <Route size={17} />
        </div>

        <div>
          <h3>Route details</h3>
          <p>Where is your shipment going?</p>
        </div>

        <span className="section-step">01</span>
      </div>

      <div className="location-inputs">
        <div className="location-field">
          <label htmlFor="origin">ORIGIN LOCATION</label>

          <div className="advanced-input">
            <div className="location-icon origin-icon">
              <MapPin size={19} />
            </div>

            <input
              id="origin"
              type="text"
              placeholder="Enter pickup city"
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
              required
            />

            <span className="input-indicator">A</span>
          </div>
        </div>

        <div className="location-connector">
          <div />
          <button
            type="button"
            className="swap-locations"
            onClick={handleSwap}
            aria-label="Swap origin and destination"
            title="Swap locations"
          >
            <ArrowDownUp size={16} />
          </button>
        </div>

        <div className="location-field">
          <label htmlFor="destination">DESTINATION</label>

          <div className="advanced-input">
            <div className="location-icon destination-icon">
              <Navigation size={19} />
            </div>

            <input
              id="destination"
              type="text"
              placeholder="Enter destination city"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              required
            />

            <span className="input-indicator destination-indicator">
              B
            </span>
          </div>
        </div>
      </div>

      {/* DEPARTURE SECTION */}

      <div className="form-section-heading departure-heading">
        <div className="form-section-icon">
          <CalendarDays size={17} />
        </div>

        <div>
          <h3>Departure schedule</h3>
          <p>When should your journey begin?</p>
        </div>

        <span className="section-step">02</span>
      </div>

      <div className="schedule-grid">
        <div className="advanced-field">
          <label htmlFor="departureDate">DEPARTURE DATE</label>

          <div className="field-control">
            <CalendarDays size={18} />
            <input
              id="departureDate"
              type="date"
              value={departureDate}
              onChange={(e) => setDepartureDate(e.target.value)}
              required
            />
          </div>
        </div>

        <div className="advanced-field">
          <label htmlFor="departureTime">DEPARTURE TIME</label>

          <div className="field-control">
            <Clock3 size={18} />
            <input
              id="departureTime"
              type="time"
              value={departureTime}
              onChange={(e) => setDepartureTime(e.target.value)}
              required
            />
          </div>
        </div>
      </div>

      {/* SHIPMENT SECTION */}

      <div className="form-section-heading shipment-heading">
        <div className="form-section-icon">
          <Package size={17} />
        </div>

        <div>
          <h3>Shipment information</h3>
          <p>Provide your cargo specifications.</p>
        </div>

        <span className="section-step">03</span>
      </div>

      <div className="weight-card">
        <div className="weight-card-heading">
          <div className="weight-label">
            <Weight size={17} />
            <label htmlFor="loadWeight">TOTAL CARGO WEIGHT</label>
          </div>

          <span className="unit-label">IMPERIAL · LBS</span>
        </div>

        <div className="weight-input-wrapper">
          <input
            id="loadWeight"
            type="number"
            min="1"
            step="1"
            value={loadWeight}
            onChange={(e) => setLoadWeight(e.target.value)}
            placeholder="Enter total weight"
            required
          />

          <span>lbs</span>
        </div>

        <div className="weight-helper">
          <Info size={13} />
          Include the combined weight of your cargo.
        </div>
      </div>

      {/* WEATHER SECTION */}

      <div className="form-section-heading weather-heading">
        <div className="form-section-icon">
          <ShieldCheck size={17} />
        </div>

        <div>
          <h3>Weather monitoring</h3>
          <p>Choose how frequently conditions are checked.</p>
        </div>

        <span className="section-step">04</span>
      </div>

      <div className="interval-options">
        {intervals.map((interval) => {
          const Icon = interval.icon;
          const active = checkpointInterval === interval.value;

          return (
            <button
              type="button"
              key={interval.value}
              className={`interval-option ${active ? "interval-active" : ""}`}
              onClick={() => setCheckpointInterval(interval.value)}
              aria-pressed={active}
            >
              <div className="interval-option-top">
                <div className="interval-icon">
                  <Icon size={17} />
                </div>

                <span className="interval-radio">
                  {active && <span />}
                </span>
              </div>

              <strong>{interval.title}</strong>
              <span className="interval-distance">
                {interval.subtitle}
              </span>

              <small>{interval.description}</small>
            </button>
          );
        })}
      </div>

      {error && (
        <div className="advanced-form-error" role="alert">
          {error}
        </div>
      )}

      {/* SUBMIT */}

      <div className="analysis-footer">
        <div className="analysis-note">
          <ShieldCheck size={17} />

          <span>
            Weather and route analysis will run after submission.
          </span>
        </div>

        <button type="submit" className="analyze-button">
          <span className="analyze-button-icon">
            <Navigation size={17} />
          </span>

          <span>Analyze routes</span>

          <ChevronRight size={19} />
        </button>

        <div className="secure-note">
          <ShieldCheck size={12} />
          Powered by StormRoute route intelligence
        </div>
      </div>
    </form>
  );
}

export default TripForm;