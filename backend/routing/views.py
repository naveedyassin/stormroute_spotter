import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from timezonefinder import TimezoneFinder

from routing.serializers import TripSerializer
from routing.services.geocoding import (
    geocode_location,
    MapboxServiceError,
)
from routing.services.directions import generate_routes

from weather.services.checkpoints import generate_checkpoints
from weather.services.forecast import (
    get_weather_forecasts,
    WeatherServiceError,
)
from weather.services.risk import classify_weather


RISK_RANKS = {
    "Low": 1,
    "Moderate": 2,
    "High": 3,
    "Severe": 4,
    "No Travel": 5,
    "Unavailable": 6,
}


def calculate_route_safety(route):
    """
    Calculate route safety using checkpoint weather risks.

    Lower safety_score means lower average risk.
    Higher weather_coverage means more reliable weather data.
    """

    checkpoints = route.get("checkpoints", [])

    if not checkpoints:
        return {
            "safety_score": None,
            "worst_risk": "Unavailable",
            "weather_coverage": 0,
        }

    risk_scores = []

    for checkpoint in checkpoints:
        risk_level = checkpoint.get(
            "risk_level",
            "Unavailable"
        )

        risk_scores.append(
            RISK_RANKS.get(risk_level, 6)
        )

    average_risk = (
        sum(risk_scores) / len(risk_scores)
    )

    worst_risk_score = max(risk_scores)

    worst_risk = next(
        (
            level
            for level, rank in RISK_RANKS.items()
            if rank == worst_risk_score
        ),
        "Unavailable",
    )

    available = sum(
        1 for score in risk_scores if score < 6
    )

    coverage = (
        available / len(checkpoints)
    ) * 100

    return {
        "safety_score": round(average_risk, 2),
        "worst_risk": worst_risk,
        "weather_coverage": round(coverage, 1),
    }


def recommend_safest_route(routes):
    """
    Recommend the safest route.

    Priority:
    1. Lowest worst-case weather risk.
    2. Lowest average weather risk.
    3. Highest weather data coverage.
    4. Shortest duration as tie-breaker.

    Routes with no usable weather data are ranked last.
    """

    if not routes:
        return None

    routes.sort(
        key=lambda route: (
            RISK_RANKS.get(
                route.get("worst_risk", "Unavailable"),
                6,
            ),

            route.get(
                "safety_score",
                float("inf"),
            ) if route.get("safety_score") is not None
            else float("inf"),

            -route.get("weather_coverage", 0),

            route.get(
                "duration_seconds",
                float("inf"),
            ),
        )
    )

    return routes[0]


class CreateTripView(APIView):

    def post(self, request):

        # 1. Validate request

        serializer = TripSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Invalid trip details.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        trip_data = serializer.validated_data

        origin = trip_data["origin"]
        destination = trip_data["destination"]

        departure_date = trip_data["departure_date"]
        departure_time = trip_data["departure_time"]

        load_weight = trip_data["load_weight"]

        interval_miles = trip_data.get(
            "checkpoint_interval",
            50,
        )

        # 2. Geocode locations

        try:

            origin_location = geocode_location(origin)

            destination_location = geocode_location(
                destination
            )

        except MapboxServiceError as exc:

            return Response(
                {
                    "success": False,
                    "message": "Unable to locate origin or destination.",
                    "error": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3. Determine departure timezone

        try:

            timezone_finder = TimezoneFinder()

            timezone_name = (
                timezone_finder.timezone_at(
                    lng=origin_location["longitude"],
                    lat=origin_location["latitude"],
                )
                or "UTC"
            )

            origin_timezone = ZoneInfo(timezone_name)

            departure_datetime = datetime.combine(
                departure_date,
                departure_time,
            ).replace(
                tzinfo=origin_timezone
            )

        except Exception as exc:

            return Response(
                {
                    "success": False,
                    "message": "Unable to determine departure timezone.",
                    "error": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 4. Generate alternative routes

        try:

            routes = generate_routes(
                origin_location,
                destination_location,
            )

        except MapboxServiceError as exc:

            return Response(
                {
                    "success": False,
                    "message": "Unable to generate routes.",
                    "error": str(exc),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if not routes:

            return Response(
                {
                    "success": False,
                    "message": "No routes found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        processed_routes = []

        # 5. Process each route

        for route_index, route in enumerate(routes):

            geometry = route.get("geometry", {})

            duration_seconds = route.get(
                "duration_seconds",
                0,
            )

            # Generate checkpoints

            try:

                checkpoints = generate_checkpoints(
                    geometry=geometry,
                    departure_time=departure_datetime,
                    duration_seconds=duration_seconds,
                    interval_miles=interval_miles,
                )

            except (ValueError, TypeError, KeyError) as exc:

                print(
                    f"Checkpoint generation failed: {exc}"
                )

                checkpoints = []

            # 6. Fetch weather forecasts

            weather_error = None

            try:

                weather_results = get_weather_forecasts(
                    checkpoints
                )

            except WeatherServiceError as exc:

                weather_error = str(exc)

                print(
                    f"Weather service error: {weather_error}"
                )

                weather_results = [
                    {
                        "available": False,
                        "reason": weather_error,
                    }
                    for _ in checkpoints
                ]

            # Validate weather response

            if len(weather_results) != len(checkpoints):

                weather_error = (
                    "Weather response count does not match "
                    "checkpoint count."
                )

                weather_results = [
                    {
                        "available": False,
                        "reason": weather_error,
                    }
                    for _ in checkpoints
                ]

            processed_checkpoints = []

            # 7. Classify checkpoint weather risk

            for checkpoint, weather in zip(
                checkpoints,
                weather_results,
            ):

                try:

                    risk = classify_weather(
                        weather=weather,
                        load_weight=load_weight,
                    )

                except (ValueError, TypeError, KeyError) as exc:

                    print(
                        f"Risk classification error: {exc}"
                    )

                    risk = {
                        "risk_level": "Unavailable",
                        "risk_rank": None,
                        "reason": str(exc),
                    }

                processed_checkpoints.append(
                    {
                        **checkpoint,
                        "weather": weather,
                        **risk,
                    }
                )

            # 8. Calculate average checkpoint risk

            risk_values = [
                checkpoint["risk_rank"]
                for checkpoint in processed_checkpoints
                if checkpoint.get("risk_rank") is not None
            ]

            average_risk = (
                round(
                    sum(risk_values) / len(risk_values),
                    2,
                )
                if risk_values
                else None
            )

            # Check weather availability

            weather_available = any(
                checkpoint.get(
                    "weather",
                    {},
                ).get(
                    "available",
                    False,
                )
                for checkpoint in processed_checkpoints
            )

            # 9. Build processed route response

            processed_routes.append(
                {
                    "route_id": route.get(
                        "route_id",
                        f"route_{route_index + 1}",
                    ),

                    "route_name": route.get(
                        "route_name",
                        f"Route {route_index + 1}",
                    ),

                    "distance_meters": route.get(
                        "distance_meters"
                    ),

                    "distance_km": route.get(
                        "distance_km"
                    ),

                    "distance_miles": route.get(
                        "distance_miles"
                    ),

                    "duration_seconds": duration_seconds,

                    "duration_minutes": route.get(
                        "duration_minutes"
                    ),

                    "duration_hours": route.get(
                        "duration_hours"
                    ),

                    "geometry": geometry,

                    "checkpoints": processed_checkpoints,

                    "checkpoint_count": len(
                        processed_checkpoints
                    ),

                    "weather_available": weather_available,

                    "weather_error": weather_error,

                    "average_risk": average_risk,
                }
            )

        # 10. Calculate safety for every processed route

        for route in processed_routes:

            safety = calculate_route_safety(route)

            route.update(safety)

        # 11. Recommend the safest route

        recommended_route = recommend_safest_route(
            processed_routes
        )

        # 12. Return API response

        return Response(
            {
                "success": True,

                "message": "Route analysis completed",

                "trip_id": str(uuid.uuid4()),

                "status": "completed",

                "total_routes": len(processed_routes),

                "recommended_route_id": (
                    recommended_route["route_id"]
                    if recommended_route
                    else None
                ),

                "recommendation_reason": (
                    "Selected based on worst-case weather risk, "
                    "average risk, weather data coverage, "
                    "and travel duration."
                    if recommended_route
                    else None
                ),

                "routes": processed_routes,
            },
            status=status.HTTP_200_OK,
        )