"""Phone Number Reconnaissance"""

import phonenumbers
from phonenumbers import geocoder, carrier, timezone


def lookup_phone(number: str) -> dict:
    result = {"number": number, "error": None}
    try:
        number = number.strip()
        parsed = phonenumbers.parse(number, None)

        if not phonenumbers.is_valid_number(parsed):
            result["error"] = "Invalid phone number"
            return result

        result.update({
            "number": number,
            "international_format": phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            ),
            "national_format": phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.NATIONAL
            ),
            "e164_format": phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.E164
            ),
            "country": geocoder.description_for_number(parsed, "en"),
            "country_code": f"+{parsed.country_code}",
            "national_number": str(parsed.national_number),
            "carrier": carrier.name_for_number(parsed, "en") or "N/A",
            "timezones": list(timezone.time_zones_for_number(parsed)),
            "is_valid": True,
            "is_possible": phonenumbers.is_possible_number(parsed),
            "number_type": _get_number_type(parsed),
        })
    except phonenumbers.NumberParseException as e:
        result["error"] = f"Parse error: {e}"
    except Exception as e:
        result["error"] = str(e)
    return result


def _get_number_type(parsed):
    ntype = phonenumbers.number_type(parsed)
    types = {
        phonenumbers.PhoneNumberType.MOBILE: "Mobile",
        phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed Line",
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed/Mobile",
        phonenumbers.PhoneNumberType.TOLL_FREE: "Toll Free",
        phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium Rate",
        phonenumbers.PhoneNumberType.SHARED_COST: "Shared Cost",
        phonenumbers.PhoneNumberType.VOIP: "VoIP",
        phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal",
        phonenumbers.PhoneNumberType.PAGER: "Pager",
        phonenumbers.PhoneNumberType.UAN: "UAN",
        phonenumbers.PhoneNumberType.UNKNOWN: "Unknown",
    }
    return types.get(ntype, "Unknown")
