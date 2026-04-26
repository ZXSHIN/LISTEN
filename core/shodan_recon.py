"""Shodan Reconnaissance Module"""

import shodan as shodan_lib
from config import SHODAN_API_KEY


def get_api():
    return shodan_lib.Shodan(SHODAN_API_KEY)


def host_lookup(ip: str) -> dict:
    result = {"ip": ip, "error": None}
    try:
        api = get_api()
        host = api.host(ip.strip())

        result.update({
            "ip": host.get("ip_str", ip),
            "organization": host.get("org", "N/A"),
            "isp": host.get("isp", "N/A"),
            "asn": host.get("asn", "N/A"),
            "country": host.get("country_name", "N/A"),
            "city": host.get("city", "N/A"),
            "latitude": host.get("latitude", "N/A"),
            "longitude": host.get("longitude", "N/A"),
            "os": host.get("os", "N/A"),
            "last_update": host.get("last_update", "N/A"),
            "hostnames": host.get("hostnames", []),
            "domains": host.get("domains", []),
            "tags": host.get("tags", []),
            "vulns": list(host.get("vulns", {}).keys()),
            "ports": host.get("ports", []),
            "services": [],
        })

        for item in host.get("data", []):
            svc = {
                "port": item.get("port"),
                "transport": item.get("transport", "tcp"),
                "product": item.get("product", ""),
                "version": item.get("version", ""),
                "banner": (item.get("data", "") or "")[:300],
                "cpe": item.get("cpe", []),
                "vulns": list(item.get("vulns", {}).keys()),
            }
            result["services"].append(svc)

    except shodan_lib.APIError as e:
        result["error"] = f"Shodan API Error: {e}"
    except Exception as e:
        result["error"] = str(e)
    return result


def search_shodan(query: str, page: int = 1) -> dict:
    result = {"query": query, "error": None, "matches": [], "total": 0}
    try:
        api = get_api()
        resp = api.search(query, page=page)
        result["total"] = resp.get("total", 0)
        for match in resp.get("matches", []):
            result["matches"].append({
                "ip": match.get("ip_str", ""),
                "port": match.get("port", ""),
                "org": match.get("org", "N/A"),
                "country": match.get("location", {}).get("country_name", "N/A"),
                "city": match.get("location", {}).get("city", "N/A"),
                "hostnames": match.get("hostnames", []),
                "banner": (match.get("data", "") or "")[:200],
                "product": match.get("product", ""),
                "version": match.get("version", ""),
                "vulns": list(match.get("vulns", {}).keys()),
                "timestamp": match.get("timestamp", ""),
            })
    except shodan_lib.APIError as e:
        result["error"] = f"Shodan API Error: {e}"
    except Exception as e:
        result["error"] = str(e)
    return result


def get_api_info() -> dict:
    try:
        api = get_api()
        info = api.info()
        return {"error": None, **info}
    except Exception as e:
        return {"error": str(e)}
