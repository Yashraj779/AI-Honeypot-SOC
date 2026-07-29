import requests
from flask import request


def get_client_ip():
    """
    Get the real client IP address.
    Supports reverse proxies like Railway, Render, Nginx, etc.
    """

    forwarded = request.headers.get("X-Forwarded-For")

    if forwarded:
        return forwarded.split(",")[0].strip()

    return request.remote_addr


def get_user_agent():
    """
    Return the client's browser User-Agent.
    """

    return request.headers.get("User-Agent", "Unknown")


def get_geo(ip):
    """
    Get country, city and coordinates from an IP address.
    """

    country = "Unknown"
    city = "Unknown"
    latitude = None
    longitude = None

    try:
        response = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,country,city,lat,lon",
            timeout=3
        )

        data = response.json()

        if data.get("status") == "success":
            country = data.get("country")
            city = data.get("city")
            latitude = data.get("lat")
            longitude = data.get("lon")

    except Exception:
        pass

    return country, city, latitude, longitude