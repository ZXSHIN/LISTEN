"""Email Reconnaissance Module"""

import re
import dns.resolver


def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def check_mx(email: str) -> dict:
    result = {"email": email, "valid_format": False, "mx_records": [], "error": None}
    email = email.strip()

    if not validate_email(email):
        result["error"] = "Invalid email format"
        return result

    result["valid_format"] = True
    domain = email.split("@")[1]

    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=5)
        result["mx_records"] = sorted(
            [(r.preference, str(r.exchange)) for r in answers]
        )
        result["domain_has_mx"] = True
    except dns.resolver.NXDOMAIN:
        result["error"] = f"Domain '{domain}' does not exist"
        result["domain_has_mx"] = False
    except Exception as e:
        result["error"] = str(e)
        result["domain_has_mx"] = False

    return result


def analyze_header(raw_header: str) -> dict:
    """Parse raw email header and extract routing info"""
    result = {
        "from": [],
        "to": [],
        "subject": "",
        "date": "",
        "received_from": [],
        "ips": [],
        "x_originating_ip": "",
        "message_id": "",
        "spam_score": "",
        "error": None
    }
    try:
        lines = raw_header.replace('\r\n', '\n').split('\n')
        current_field = None
        current_value = []

        for line in lines:
            if line and not line[0].isspace():
                if current_field and current_value:
                    val = ' '.join(current_value).strip()
                    _assign_header_field(result, current_field, val)
                if ':' in line:
                    idx = line.index(':')
                    current_field = line[:idx].strip().lower()
                    current_value = [line[idx+1:].strip()]
                else:
                    current_field = None
                    current_value = []
            else:
                if current_field:
                    current_value.append(line.strip())

        if current_field and current_value:
            val = ' '.join(current_value).strip()
            _assign_header_field(result, current_field, val)

        # Extract IPs from received headers
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        for recv in result["received_from"]:
            ips = re.findall(ip_pattern, recv)
            for ip in ips:
                if ip not in result["ips"] and not ip.startswith("127."):
                    result["ips"].append(ip)

    except Exception as e:
        result["error"] = str(e)

    return result


def _assign_header_field(result, field, value):
    if field == "from":
        result["from"].append(value)
    elif field == "to":
        result["to"].append(value)
    elif field == "subject":
        result["subject"] = value
    elif field == "date":
        result["date"] = value
    elif field == "received":
        result["received_from"].append(value)
    elif field == "x-originating-ip":
        result["x_originating_ip"] = value
    elif field == "message-id":
        result["message_id"] = value
    elif field in ("x-spam-score", "x-spam-status"):
        result["spam_score"] = value
