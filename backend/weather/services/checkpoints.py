import math
from datetime import timedelta


EARTH_RADIUS_METERS = 6371000
METERS_PER_MILE = 1609.344


def haversine_distance(point1, point2):
    """Calculate distance between two [longitude, latitude] points."""

    lon1, lat1 = map(math.radians, point1)
    lon2, lat2 = map(math.radians, point2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * EARTH_RADIUS_METERS * math.asin(math.sqrt(a))


def interpolate_point(start, end, fraction):
    """Interpolate a point between two coordinates."""

    return [
        start[0] + (end[0] - start[0]) * fraction,
        start[1] + (end[1] - start[1]) * fraction,
    ]


def generate_checkpoints(
    geometry,
    departure_time,
    duration_seconds,
    interval_miles,
):
    """
    Generate checkpoints along a GeoJSON LineString.

    Each checkpoint includes:
    - Coordinates
    - Distance from route origin
    - Estimated arrival time
    """

    coordinates = geometry.get("coordinates", [])

    if len(coordinates) < 2:
        return []

    if interval_miles not in [10, 25, 50]:
        raise ValueError("Interval must be 10, 25 or 50 miles.")

    segments = []
    cumulative_distance = 0

    for index in range(len(coordinates) - 1):

        start = coordinates[index]
        end = coordinates[index + 1]

        segment_distance = haversine_distance(start, end)

        if segment_distance <= 0:
            continue

        segments.append({
            "start": start,
            "end": end,
            "start_distance": cumulative_distance,
            "end_distance": cumulative_distance + segment_distance,
        })

        cumulative_distance += segment_distance

    if cumulative_distance == 0:
        return []

    interval_meters = interval_miles * METERS_PER_MILE

    target_distances = []
    distance = 0

    while distance < cumulative_distance:
        target_distances.append(distance)
        distance += interval_meters

    # Always include the destination.
    if not target_distances or target_distances[-1] != cumulative_distance:
        target_distances.append(cumulative_distance)

    checkpoints = []

    segment_index = 0

    for checkpoint_index, target_distance in enumerate(target_distances):

        while (
            segment_index < len(segments) - 1
            and segments[segment_index]["end_distance"] < target_distance
        ):
            segment_index += 1

        segment = segments[segment_index]

        segment_length = (
            segment["end_distance"] - segment["start_distance"]
        )

        fraction = (
            (target_distance - segment["start_distance"])
            / segment_length
        )

        point = interpolate_point(
            segment["start"],
            segment["end"],
            fraction,
        )

        progress = target_distance / cumulative_distance

        arrival_time = departure_time + timedelta(
            seconds=duration_seconds * progress
        )

        checkpoints.append({
            "checkpoint_id": checkpoint_index + 1,
            "longitude": point[0],
            "latitude": point[1],
            "distance_miles": round(
                target_distance / METERS_PER_MILE, 2
            ),
            "progress": round(progress, 4),
            "estimated_arrival": arrival_time.isoformat(),
        })

    return checkpoints
