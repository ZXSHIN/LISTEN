"""LISTEN - Main Application Window"""

import customtkinter as ctk
import sys
import os
import datetime

from ui.helpers import *
from ui.tab_dashboard import DashboardTab
from ui.tab_dork import DorkTab
from ui.tab_ip import IPTab
from ui.tab_whois import WhoisTab
from ui.tab_email import EmailTab
from ui.tab_username import UsernameTab
from ui.tab_phone import PhoneTab
from ui.tab_metadata import MetadataTab
from ui.tab_subdomain import SubdomainTab
from ui.tab_shodan import ShodanTab

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

NAV_ITEMS = [
    ("🏠  Dashboard",   DashboardTab),
    ("🔍  Dorking",     DorkTab),
    ("🌐  IP Lookup",   IPTab),
    ("📋  WHOIS",       WhoisTab),
    ("📧  Email Recon", EmailTab),
    ("👤  Username",    UsernameTab),
    ("📱  Phone",       PhoneTab),
    ("🗂  Metadata",    MetadataTab),
    ("🔗  Subdomains",  SubdomainTab),
    ("🛡  Shodan",      ShodanTab),
]

LOGO_ASCII = """
██╗     ██╗███████╗████████╗███████╗███╗   ██╗
██║     ██║██╔════╝╚══██╔══╝██╔════╝████╗  ██║
██║     ██║███████╗   ██║   █████╗  ██╔██╗ ██║
██║     ██║╚════██║   ██║   ██╔══╝  ██║╚██╗██║
███████╗██║███████║   ██║   ███████╗██║ ╚████║
╚══════╝╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═══╝"""


class LISTENApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._active_tab = None
        self._tabs = {}
        self._nav_buttons = {}
        self._setup_window()
        self._build_ui()
        self._select_tab("🏠  Dashboard")

    def _setup_window(self):
        self.title("LISTEN — OSINT & Dorking Toolkit")
        self.geometry("1300x820")
        self.minsize(1100, 700)
        self.configure(fg_color=BG)
        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 1300) // 2
        y = (self.winfo_screenheight() - 820) // 2
        self.geometry(f"1300x820+{x}+{y}")

    def _build_ui(self):
        # ── Root layout: sidebar | content ───────────────────────────────────
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        sidebar = ctk.CTkFrame(self, fg_color=SIDEBAR, width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        self._build_sidebar(sidebar)

        # Content area
        self.content_frame = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

    def _build_sidebar(self, sidebar):
        # Logo area
        logo_frame = ctk.CTkFrame(sidebar, fg_color=BG, corner_radius=0, height=140)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)

        ctk.CTkLabel(
            logo_frame, text="LISTEN",
            font=("Consolas", 28, "bold"), text_color=ACCENT
        ).pack(pady=(22, 0))
        ctk.CTkLabel(
            logo_frame, text="OSINT & DORKING TOOLKIT",
            font=("Segoe UI", 7, "bold"), text_color=TEXT2
        ).pack()

        # Separator
        sep = ctk.CTkFrame(sidebar, fg_color=BORDER, height=1)
        sep.pack(fill="x", padx=16, pady=(8, 12))

        ctk.CTkLabel(sidebar, text="MODULES", font=("Segoe UI", 8, "bold"),
                     text_color=TEXT2).pack(anchor="w", padx=16, pady=(0, 6))

        # Navigation buttons
        for name, tab_cls in NAV_ITEMS:
            btn = ctk.CTkButton(
                sidebar,
                text=name,
                anchor="w",
                width=200,
                height=40,
                font=("Segoe UI", 12),
                fg_color="transparent",
                hover_color=BORDER,
                text_color=TEXT2,
                corner_radius=8,
                command=lambda n=name: self._select_tab(n),
            )
            btn.pack(padx=10, pady=2)
            self._nav_buttons[name] = btn

        # Separator
        sep2 = ctk.CTkFrame(sidebar, fg_color=BORDER, height=1)
        sep2.pack(fill="x", padx=16, pady=(12, 8))

        # Bottom info
        bottom = ctk.CTkFrame(sidebar, fg_color="transparent")
        bottom.pack(side="bottom", fill="x", padx=16, pady=16)

        now = datetime.datetime.now().strftime("%Y-%m-%d")
        ctk.CTkLabel(bottom, text=f"v1.0.0  •  {now}",
                     font=FONT_SMALL, text_color=TEXT2).pack(anchor="w")
        ctk.CTkLabel(bottom, text="⚠ For authorized use only",
                     font=("Segoe UI", 8), text_color=ORANGE).pack(anchor="w", pady=(4, 0))

        # Status dot
        status_row = ctk.CTkFrame(sidebar, fg_color="transparent")
        status_row.pack(side="bottom", fill="x", padx=16, pady=(0, 4))
        ctk.CTkLabel(status_row, text="●", font=("Segoe UI", 10),
                     text_color=GREEN).pack(side="left")
        ctk.CTkLabel(status_row, text=" ONLINE", font=("Segoe UI", 9),
                     text_color=GREEN).pack(side="left")

    def _select_tab(self, name):
        if self._active_tab == name:
            return

        # Reset old button
        if self._active_tab and self._active_tab in self._nav_buttons:
            self._nav_buttons[self._active_tab].configure(
                fg_color="transparent", text_color=TEXT2
            )

        # Highlight new button
        self._nav_buttons[name].configure(fg_color=ACCENT, text_color=BTN_FG)
        self._active_tab = name

        # Show/hide frames
        for n, frame in self._tabs.items():
            frame.grid_remove()

        if name not in self._tabs:
            tab_cls = dict(NAV_ITEMS)[name]
            frame = tab_cls(self.content_frame)
            frame.grid(row=0, column=0, sticky="nsew")
            self._tabs[name] = frame
        else:
            self._tabs[name].grid()
