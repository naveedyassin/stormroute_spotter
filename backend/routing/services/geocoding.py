import os
import requests
from urllib.parse import quote


MAPBOX_GEOCODING_URL = (
    "https://api.mapbox.com/geocoding/v5/mapbox.places"
)


class MapboxServiceError(Exception):
    """Raised when a Mapbox API request fails."""


def geocode_location(location):
    """
    Convert a human-readable location into longitude and latitude.

    Returns:
        {
            "place_name": str,
            "longitude": float,
            "latitude": float
        }
    """

    token = os.getenv("MAPBOX_ACCESS_TOKEN")

    if not token:
        raise MapboxServiceError(
            "MAPBOX_ACCESS_TOKEN is missing from backend .env"
        )

    encoded_location = quote(location, safe="")

    url = f"{MAPBOX_GEOCODING_URL}/{encoded_location}.json"

    params = {
        "access_token": token,
        "limit": 1,
        "autocomplete": "false",
        "country": "us",
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=15
        )
        response.raise_for_status()

        data = response.json()

    except requests.RequestException as exc:
        raise MapboxServiceError(
            f"Mapbox geocoding request failed: {exc}"
        ) from exc

    features = data.get("features", [])

    if not features:
        raise MapboxServiceError(
            f"Could not find location: {location}"
        )

    feature = features[0]
    longitude, latitude = feature["center"]

    return {
        "place_name": feature.get("place_name", location),
        "longitude": longitude,
        "latitude": latitude,
    }
