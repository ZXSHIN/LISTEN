"""IP Lookup Module - Geolocation and intelligence"""

import requests
import socket

def lookup_ip(ip: str) -> dict:
    """Lookup IP geolocation via ip-api.com"""
    result = {"ip": ip, "error": None}
    try:
        ip = ip.strip()
        if not ip:
            result["error"] = "IP address cannot be empty"
            return result

        r = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,"
            f"region,regionName,city,zip,lat,lon,timezone,isp,org,as,query",
            timeout=10
        )
        data = r.json()

        if data.get("status") == "fail":
            result["error"] = data.get("message", "Lookup failed")
            return result

        result.update({
            "ip": data.get("query", ip),
            "country": data.get("country", "N/A"),
            "country_code": data.get("countryCode", "N/A"),
            "region": data.get("regionName", "N/A"),
            "city": data.get("city", "N/A"),
            "zip": data.get("zip", "N/A"),
            "lat": data.get("lat", "N/A"),
            "lon": data.get("lon", "N/A"),
            "timezone": data.get("timezone", "N/A"),
            "isp": data.get("isp", "N/A"),
            "org": data.get("org", "N/A"),
            "asn": data.get("as", "N/A"),
        })

        # Reverse DNS
        try:
            result["hostname"] = socket.gethostbyaddr(ip)[0]
        except Exception:
            result["hostname"] = "N/A"

    except requests.exceptions.ConnectionError:
        result["error"] = "No internet connection"
    except Exception as e:
        result["error"] = str(e)

    return result


def get_my_ip() -> str:
    """Get current public IP"""
    try:
        r = requests.get("https://api.ipify.org?format=json", timeout=5)
        return r.json().get("ip", "Unknown")
    except Exception:
        return "Unknown"
