"""WHOIS & DNS Lookup Module"""

import whois
import dns.resolver
import dns.reversename

def whois_lookup(domain: str) -> dict:
    """Perform WHOIS lookup on domain"""
    result = {"domain": domain, "error": None}
    try:
        domain = domain.strip().lower()
        # Remove protocol if present
        for prefix in ["https://", "http://", "www."]:
            if domain.startswith(prefix):
                domain = domain[len(prefix):]
        domain = domain.split("/")[0]

        w = whois.whois(domain)

        def fmt(val):
            if val is None:
                return "N/A"
            if isinstance(val, list):
                return ', '.join(str(v) for v in val)
            return str(val)

        result.update({
            "domain": domain,
            "registrar": fmt(w.registrar),
            "creation_date": fmt(w.creation_date),
            "expiration_date": fmt(w.expiration_date),
            "updated_date": fmt(w.updated_date),
            "name_servers": fmt(w.name_servers),
            "status": fmt(w.status),
            "emails": fmt(w.emails),
            "org": fmt(w.org),
            "country": fmt(w.country),
            "state": fmt(w.state),
            "registrant": fmt(getattr(w, 'registrant_name', None)),
            "dnssec": fmt(getattr(w, 'dnssec', None)),
        })
    except Exception as e:
        result["error"] = str(e)
    return result


def dns_lookup(domain: str) -> dict:
    """Get DNS records for domain"""
    domain = domain.strip().lower()
    for prefix in ["https://", "http://", "www."]:
        if domain.startswith(prefix):
            domain = domain[len(prefix):]
    domain = domain.split("/")[0]

    records = {}
    for rtype in ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]:
        try:
            answers = dns.resolver.resolve(domain, rtype, lifetime=5)
            records[rtype] = [str(r) for r in answers]
        except Exception:
            records[rtype] = []
    return records
