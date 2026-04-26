"""Dashboard / Home Tab"""

import customtkinter as ctk
import threading
from ui.helpers import *
from core.ip_lookup import get_my_ip


class DashboardTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self._build()
        threading.Thread(target=self._load_myip, daemon=True).start()

    def _build(self):
        # ── Header / Banner ─────────────────────────────────────────────────
        banner = ctk.CTkFrame(self, fg_color=CARD, corner_radius=16)
        banner.pack(fill="x", padx=20, pady=(20, 14))

        ascii_art = (
            "██╗     ██╗███████╗████████╗███████╗███╗   ██╗\n"
            "██║     ██║██╔════╝╚══██╔══╝██╔════╝████╗  ██║\n"
            "██║     ██║███████╗   ██║   █████╗  ██╔██╗ ██║\n"
            "██║     ██║╚════██║   ██║   ██╔══╝  ██║╚██╗██║\n"
            "███████╗██║███████║   ██║   ███████╗██║ ╚████║\n"
            "╚══════╝╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═══╝"
        )
        ctk.CTkLabel(
            banner, text=ascii_art,
            font=("Consolas", 11, "bold"),
            text_color=ACCENT, justify="left"
        ).pack(padx=20, pady=(16, 4))

        ctk.CTkLabel(
            banner,
            text="OSINT & Dorking Desktop Toolkit  •  v1.0.0",
            font=("Segoe UI", 11), text_color=TEXT2
        ).pack(pady=(0, 6))

        ctk.CTkLabel(
            banner,
            text="⚠  For educational and authorized use only",
            font=("Segoe UI", 9, "bold"), text_color=ORANGE
        ).pack(pady=(0, 14))

        # ── My IP Card ───────────────────────────────────────────────────────
        ip_row = ctk.CTkFrame(banner, fg_color=BG2, corner_radius=10)
        ip_row.pack(fill="x", padx=20, pady=(0, 16))
        make_label(ip_row, "📍 Your Public IP:", font=FONT_BODY, color=TEXT2).pack(
            side="left", padx=12, pady=10)
        self.my_ip_lbl = make_label(ip_row, "Fetching...", font=("Consolas", 13, "bold"), color=GREEN)
        self.my_ip_lbl.pack(side="left", padx=4)

        # ── Module Grid ──────────────────────────────────────────────────────
        make_label(self, "Available Modules", font=FONT_HEAD, color=TEXT).pack(
            anchor="w", padx=20, pady=(4, 8))

        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=20)
        for i in range(3):
            grid.columnconfigure(i, weight=1)

        modules = [
            ("🔍", "Google Dorking",
             "Template & custom dork builder\nOpen in Google, Bing, DuckDuckGo",
             ACCENT),
            ("🌐", "IP Lookup",
             "Geolocation, ISP, ASN\nReverse DNS & Maps link",
             "#4fc3f7"),
            ("📋", "WHOIS",
             "Domain registration info\nDNS A, MX, TXT, NS records",
             "#81c784"),
            ("📧", "Email Recon",
             "Format validation, MX check\nEmail header routing analyzer",
             "#ffb74d"),
            ("👤", "Username Recon",
             "Hunt across 50+ platforms\nMulti-threaded parallel scan",
             "#ce93d8"),
            ("📱", "Phone Lookup",
             "Country, carrier, type\nInternational format parser",
             "#80cbc4"),
            ("🗂", "Metadata",
             "EXIF from images (GPS!)\nPDF & DOCX author info",
             "#ef9a9a"),
            ("🔗", "Subdomains",
             "DNS brute-force enum\nBuilt-in + custom wordlist",
             "#ffe082"),
            ("🛡", "Shodan",
             "Host & service intel\nSearch exposed devices & vulns",
             RED),
        ]

        for idx, (icon, name, desc, color) in enumerate(modules):
            row_i = idx // 3
            col_i = idx % 3
            card = ctk.CTkFrame(grid, fg_color=CARD, corner_radius=12)
            card.grid(row=row_i, column=col_i, padx=5, pady=5, sticky="nsew")
            grid.rowconfigure(row_i, weight=1)

            ctk.CTkLabel(card, text=icon, font=("Segoe UI", 26)).pack(pady=(14, 2))
            ctk.CTkLabel(card, text=name, font=("Segoe UI", 12, "bold"),
                         text_color=color).pack()
            ctk.CTkLabel(card, text=desc, font=FONT_SMALL,
                         text_color=TEXT2, justify="center").pack(pady=(4, 14), padx=8)

        # ── Status Bar ───────────────────────────────────────────────────────
        status = ctk.CTkFrame(self, fg_color=CARD, corner_radius=10)
        status.pack(fill="x", padx=20, pady=(14, 16))
        status_items = [
            ("●  LISTEN Running", GREEN),
            ("●  Shodan API Connected", ACCENT),
            ("●  Network Available", GREEN),
        ]
        for text, color in status_items:
            make_label(status, text, font=("Segoe UI", 9), color=color).pack(
                side="left", padx=16, pady=8)

    def _load_myip(self):
        ip = get_my_ip()
        self.after(0, lambda: self.my_ip_lbl.configure(text=ip))
