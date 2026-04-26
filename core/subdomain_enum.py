"""Subdomain Enumeration - DNS brute-force"""

import threading
import dns.resolver

COMMON_SUBDOMAINS = [
    "www", "mail", "ftp", "admin", "api", "app", "blog", "cdn", "cloud",
    "cpanel", "dashboard", "dev", "direct", "docs", "download", "email",
    "forum", "help", "home", "host", "imap", "internal", "intranet",
    "login", "m", "manage", "mobile", "mx", "mysql", "news", "ns1", "ns2",
    "office", "old", "panel", "pop", "portal", "preview", "remote",
    "secure", "server", "shop", "smtp", "sql", "ssh", "staging", "static",
    "store", "support", "test", "vpn", "web", "webmail", "wiki", "wp",
    "beta", "alpha", "assets", "media", "images", "img", "files",
    "auth", "id", "accounts", "my", "status", "sandbox", "preprod",
    "prod", "production", "backup", "db", "database", "redis", "cache",
    "monitor", "metrics", "logs", "jenkins", "ci", "gitlab", "git",
    "bitbucket", "jira", "confluence", "slack", "zoom",
]


def enumerate_subdomains(domain: str, callback, stop_event=None, threads=30):
    """
    Enumerate subdomains using DNS resolution.
    callback(subdomain, ip_list, status) called for each result.
    """
    sem = threading.Semaphore(threads)

    def check(sub):
        if stop_event and stop_event.is_set():
            return
        fqdn = f"{sub}.{domain}"
        with sem:
            try:
                answers = dns.resolver.resolve(fqdn, "A", lifetime=3)
                ips = [str(r) for r in answers]
                callback(fqdn, ips, "found")
            except dns.resolver.NXDOMAIN:
                pass
            except dns.resolver.NoAnswer:
                callback(fqdn, [], "no_answer")
            except Exception:
                pass

    workers = []
    for sub in COMMON_SUBDOMAINS:
        if stop_event and stop_event.is_set():
            break
        t = threading.Thread(target=check, args=(sub,), daemon=True)
        workers.append(t)
        t.start()

    for t in workers:
        t.join(timeout=15)


def custom_wordlist_enum(domain: str, wordlist_path: str, callback, stop_event=None):
    """Enumerate using custom wordlist file"""
    try:
        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
            words = [line.strip() for line in f if line.strip()]
        enumerate_subdomains_from_list(domain, words, callback, stop_event)
    except Exception as e:
        callback(None, [], f"error:{e}")


def enumerate_subdomains_from_list(domain, wordlist, callback, stop_event=None, threads=30):
    sem = threading.Semaphore(threads)

    def check(sub):
        if stop_event and stop_event.is_set():
            return
        fqdn = f"{sub}.{domain}"
        with sem:
            try:
                answers = dns.resolver.resolve(fqdn, "A", lifetime=3)
                ips = [str(r) for r in answers]
                callback(fqdn, ips, "found")
            except Exception:
                pass

    workers = []
    for sub in wordlist:
        if stop_event and stop_event.is_set():
            break
        t = threading.Thread(target=check, args=(sub,), daemon=True)
        workers.append(t)
        t.start()

    for t in workers:
        t.join(timeout=20)
