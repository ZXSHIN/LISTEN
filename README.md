# LISTEN — OSINT & Dorking Desktop Toolkit

```
██╗     ██╗███████╗████████╗███████╗███╗   ██╗
██║     ██║██╔════╝╚══██╔══╝██╔════╝████╗  ██║
██║     ██║███████╗   ██║   █████╗  ██╔██╗ ██║
██║     ██║╚════██║   ██║   ██╔══╝  ██║╚██╗██║
███████╗██║███████║   ██║   ███████╗██║ ╚████║
╚══════╝╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═══╝
```

Tool OSINT dan Google Dorking berbasis desktop menggunakan Python + CustomTkinter.

---
## tambahkan apikey shodan
di file config.py

## Cara Menjalankan

```bash
# Install dependencies (sekali saja)
pip install -r requirements.txt

# Jalankan aplikasi
python listen.py

# Atau klik dua kali
LISTEN.bat
```

---

## Modul

| Modul | Fitur |
|---|---|
| 🏠 Dashboard | Overview & status IP publik |
| 🔍 Google Dorking | 100+ template dork, custom builder, buka di Google/Bing/DDG |
| 🌐 IP Lookup | Geolocation, ISP, ASN, reverse DNS |
| 📋 WHOIS | Registrar, DNS records (A, MX, TXT, NS, SOA) |
| 📧 Email Recon | Validasi, MX check, header analyzer |
| 👤 Username Recon | Cek 50+ platform sekaligus (multithreaded) |
| 📱 Phone Lookup | Negara, carrier, tipe nomor |
| 🗂 Metadata | EXIF dari foto (termasuk GPS!), PDF, DOCX |
| 🔗 Subdomains | DNS brute-force, wordlist custom |
| 🛡 Shodan | Host lookup, search query, API info |

---

## Struktur Project

```
d:\osint\
├── listen.py           ← Entry point
├── config.py           ← API keys & settings
├── requirements.txt
├── LISTEN.bat          ← Windows launcher
├── core\               ← Backend modules
│   ├── dork_engine.py
│   ├── ip_lookup.py
│   ├── whois_lookup.py
│   ├── email_recon.py
│   ├── username_recon.py
│   ├── phone_recon.py
│   ├── metadata_extractor.py
│   ├── subdomain_enum.py
│   └── shodan_recon.py
└── ui\                 ← GUI modules
    ├── app.py
    ├── helpers.py
    ├── tab_dashboard.py
    ├── tab_dork.py
    ├── tab_ip.py
    ├── tab_whois.py
    ├── tab_email.py
    ├── tab_username.py
    ├── tab_phone.py
    ├── tab_metadata.py
    ├── tab_subdomain.py
    └── tab_shodan.py
```

---

> ⚠ **Disclaimer**: Tool ini dibuat untuk tujuan edukasi dan pengujian keamanan yang sah. Gunakan hanya pada sistem yang Anda miliki izinnya.
