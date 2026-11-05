import os
import time
import requests

from .geocoding import MapboxServiceError


GOOGLE_ROUTES_URL = (
    "https://routes.googleapis.com/directions/v2:computeRoutes"
)


def decode_polyline(encoded):
    """Decode Google's encoded polyline into GeoJSON coordinates."""

    coordinates = []

    index = 0
    lat = 0
    lng = 0

    while index < len(encoded):

        result = 0
        shift = 0

        while True:
            b = ord(encoded[index]) - 63
            index += 1

            result |= (b & 0x1f) << shift
            shift += 5

            if b < 0x20:
                break

        delta_lat = (
            ~(result >> 1)
            if result & 1
            else result >> 1
        )

        lat += delta_lat

        result = 0
        shift = 0

        while True:
            b = ord(encoded[index]) - 63
            index += 1

            result |= (b & 0x1f) << shift
            shift += 5

            if b < 0x20:
                break

        delta_lng = (
            ~(result >> 1)
            if result & 1
            else result >> 1
        )

        lng += delta_lng

        coordinates.append([
            lng / 1e5,
            lat / 1e5
        ])

    return {
        "type": "LineString",
        "coordinates": coordinates
    }


def generate_routes(origin, destination):

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if not api_key:
        raise MapboxServiceError(
            "GOOGLE_MAPS_API_KEY is missing."
        )

    payload = {

        "origin": {
            "location": {
                "latLng": {
                    "latitude": origin["latitude"],
                    "longitude": origin["longitude"]
                }
            }
        },

        "destination": {
            "location": {
                "latLng": {
                    "latitude": destination["latitude"],
                    "longitude": destination["longitude"]
                }
            }
        },

        "travelMode": "DRIVE",

        "routingPreference": "TRAFFIC_AWARE",

        "computeAlternativeRoutes": True,

        "polylineQuality": "HIGH_QUALITY",

        "polylineEncoding": "ENCODED_POLYLINE",

        "languageCode": "en-US",

        "units": "IMPERIAL"
    }

    headers = {

        "Content-Type": "application/json",

        "X-Goog-Api-Key": api_key,

        "X-Goog-FieldMask": (
            "routes.distanceMeters,"
            "routes.duration,"
            "routes.polyline.encodedPolyline,"
            "routes.routeLabels"
        )
    }

    last_error = None

    for attempt in range(3):

        try:

            response = requests.post(
                GOOGLE_ROUTES_URL,
                json=payload,
                headers=headers,
                timeout=(10, 60)
            )

            response.raise_for_status()

            data = response.json()

            break

        except requests.Timeout as exc:

            last_error = exc

            if attempt < 2:
                time.sleep(2 ** attempt)

        except requests.RequestException as exc:

            raise MapboxServiceError(
                f"Google Routes API failed: {exc}"
            ) from exc

    else:

        raise MapboxServiceError(
            f"Google Routes API timed out: {last_error}"
        )

    routes_data = data.get("routes", [])

    if not routes_data:

        raise MapboxServiceError(
            "Google could not generate a route."
        )

    routes = []

    route_names = [
        "Fastest Route",
        "Alternative Route 1",
        "Alternative Route 2"
    ]

    for index, route in enumerate(routes_data[:3]):

        distance_meters = route["distanceMeters"]

        duration_seconds = float(
            route["duration"].replace("s", "")
        )

        encoded_polyline = (
            route["polyline"]["encodedPolyline"]
        )

        geometry = decode_polyline(encoded_polyline)

        routes.append({

            "route_id": f"route_{index + 1}",

            "route_name": route_names[index],

            "distance_meters": distance_meters,

            "distance_km": round(
                distance_meters / 1000, 2
            ),

            "distance_miles": round(
                distance_meters / 1609.344, 2
            ),

            "duration_seconds": duration_seconds,

            "duration_minutes": round(
                duration_seconds / 60, 2
            ),

            "duration_hours": round(
                duration_seconds / 3600, 2
            ),

            "geometry": geometry,

        })

    return routes