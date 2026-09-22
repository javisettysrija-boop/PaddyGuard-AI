def generate_alerts(temperature, humidity, rainfall):

    alerts = []

    if temperature > 35:
        alerts.append(
            "High temperature. Monitor the paddy crop and maintain proper water management."
        )

    if humidity > 85:
        alerts.append(
            "High humidity. Monitor the crop for signs of fungal disease."
        )

    if rainfall > 50:
        alerts.append(
            "Heavy rainfall. Check field drainage and standing water."
        )

    if not alerts:
        alerts.append(
            "No major weather-based crop alert at this time."
        )

    return alerts