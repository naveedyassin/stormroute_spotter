import requests
from datetime import datetime, timezone
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT = (5, 30)
MAX_BATCH_SIZE = 50
class WeatherServiceError(Exception):
    pass
def _get_checkpoint_weather(hourly, arrival_time):
    """
    Match hourly weather data to checkpoint arrival time.
    """
    times = hourly.get("time", [])
    if not times:
        return {
            "available": False,
            "reason": "No hourly forecast data available.",
        }
    target = arrival_time.astimezone(timezone.utc)
    try:
        forecast_times = [
            datetime.fromisoformat(value).replace(
                tzinfo=timezone.utc
            )
            for value in times
        ]
        nearest_index = min(
            range(len(forecast_times)),
            key=lambda index: abs(
                (forecast_times[index] - target).total_seconds()
            ),
        )
    except (ValueError, TypeError) as exc:
        raise WeatherServiceError(
            f"Invalid forecast timestamps: {exc}"
        ) from exc
    forecast_time = forecast_times[nearest_index]
    # Reject forecasts more than one hour away.
    if abs(
        (forecast_time - target).total_seconds()
    ) > 3600:
        return {
            "available": False,
            "reason": "No sufficiently close hourly forecast.",
        }
    wind = hourly.get("wind_speed_10m", [])
    rain = hourly.get("rain", [])
    snowfall = hourly.get("snowfall", [])
    if not all(
        len(values) > nearest_index
        for values in [wind, rain, snowfall]
    ):
        return {
            "available": False,
            "reason": "Incomplete weather forecast data.",
        }
    return {
        "available": True,
        "forecast_time": forecast_time.isoformat(),
        "wind_mph": float(
            wind[nearest_index] or 0
        ),
        "rain_in_per_hour": float(
            rain[nearest_index] or 0
        ),
        "snow_in_per_hour": float(
            snowfall[nearest_index] or 0
        ) / 2.54,
        "source": "Open-Meteo",
    }
def get_weather_forecasts(checkpoints):
    """
    Retrieve weather for multiple checkpoints
    using batched Open-Meteo requests.
    Returns weather results in checkpoint order.
    """
    if not checkpoints:
        return []
    results = []
    # Process checkpoints in batches.
    for start in range(0, len(checkpoints), MAX_BATCH_SIZE):
        batch = checkpoints[
            start:start + MAX_BATCH_SIZE
        ]
        latitudes = ",".join(
            str(checkpoint["latitude"])
            for checkpoint in batch
        )
        longitudes = ",".join(
            str(checkpoint["longitude"])
            for checkpoint in batch
        )
        params = {
            "latitude": latitudes,
            "longitude": longitudes,
            "hourly": (
                "wind_speed_10m,"
                "rain,"
                "snowfall"
            ),
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
            "timezone": "UTC",
            "forecast_days": 16,
        }
        try:
            response = requests.get(
                OPEN_METEO_URL,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise WeatherServiceError(
                f"Open-Meteo batch request failed: {exc}"
            ) from exc
        # Open-Meteo returns a dictionary for one location
        # and a list of dictionaries for multiple locations.
        if isinstance(data, dict):
            location_data = [data]
        elif isinstance(data, list):
            location_data = data
        else:
            raise WeatherServiceError(
                "Unexpected Open-Meteo response format."
            )
        if len(location_data) != len(batch):
            raise WeatherServiceError(
                "Weather response count does not match "
                "checkpoint count."
            )
        for checkpoint, weather_data in zip(
            batch,
            location_data,
        ):
            arrival_time = datetime.fromisoformat(
                checkpoint["estimated_arrival"]
            )
            hourly = weather_data.get("hourly", {})
            weather = _get_checkpoint_weather(
                hourly,
                arrival_time,
            )
            results.append(weather)
    return results
def get_weather_forecast(latitude, longitude, arrival_time):
    """
    Backward-compatible single-checkpoint function.
    """
    checkpoint = {
        "latitude": latitude,
        "longitude": longitude,
        "estimated_arrival": arrival_time.isoformat(),
    }
    results = get_weather_forecasts([checkpoint])
    return results[0]