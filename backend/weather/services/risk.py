RISK_LEVELS = {
    "Low": 1,
    "Moderate": 2,
    "High": 3,
    "Severe": 4,
    "No Travel": 5,
    "Unavailable": None,
}


def classify_weather(weather, load_weight):
    """
    Classify checkpoint weather using assessment thresholds
    and truck-load safety overrides.
    """

    if not weather.get("available"):
        return {
            "risk_level": "Unavailable",
            "risk_rank": None,
            "reason": weather.get(
                "reason",
                "Weather data unavailable.",
            ),
        }

    wind = weather["wind_mph"]
    rain = weather["rain_in_per_hour"]
    snow = weather["snow_in_per_hour"]

    risks = []

    # Wind classification.
    if wind >= 55:
        risks.append("No Travel")
    elif wind >= 45:
        risks.append("Severe")
    elif wind >= 35:
        risks.append("High")
    elif wind >= 25:
        risks.append("Moderate")
    else:
        risks.append("Low")

    # Rain classification.
    if rain > 1.00:
        risks.append("No Travel")
    elif rain >= 0.50:
        risks.append("Severe")
    elif rain >= 0.25:
        risks.append("High")
    elif rain >= 0.10:
        risks.append("Moderate")
    else:
        risks.append("Low")

    # Snow classification.
    if snow > 3.0:
        risks.append("No Travel")
    elif snow >= 2.0:
        risks.append("Severe")
    elif snow >= 1.0:
        risks.append("High")
    elif snow >= 0.5:
        risks.append("Moderate")
    else:
        risks.append("Low")

    risk = max(risks, key=lambda item: RISK_LEVELS[item])

    # Truck load overrides.
    if wind >= 55:
        risk = "No Travel"

    elif wind >= 45 and load_weight > 30000:
        risk = "No Travel"

    elif wind >= 35 and load_weight > 40000:
        risk = "Severe"

    return {
        "risk_level": risk,
        "risk_rank": RISK_LEVELS[risk],
        "weather": weather,
        "load_weight": load_weight,
    }
