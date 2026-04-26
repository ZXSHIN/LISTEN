"""WHOIS & DNS Tab"""

import customtkinter as ctk
import threading
from ui.helpers import *
from core.whois_lookup import whois_lookup, dns_lookup


class WhoisTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="📋  WHOIS Lookup", font=FONT_TITLE,
                     text_color=ACCENT).pack(anchor="w", padx=20, pady=(18, 2))
        ctk.CTkLabel(self, text="Domain registration info, DNS records & nameservers",
                     font=FONT_SMALL, text_color=TEXT2).pack(anchor="w", padx=20, pady=(0, 14))

        inp = ctk.CTkFrame(self, fg_color=CARD, corner_radius=12)
        inp.pack(fill="x", padx=20, pady=(0, 12))
        row = ctk.CTkFrame(inp, fg_color="transparent")
        row.pack(padx=16, pady=14)
        make_label(row, "Domain:", color=TEXT).pack(side="left", padx=(0,8))
        self.domain_entry = make_entry(row, "e.g. google.com", width=360)
        self.domain_entry.pack(side="left", padx=(0,8))
        make_button(row, "🔍 WHOIS", self._do_whois).pack(side="left", padx=4)
        make_button(row, "📡 DNS Records", self._do_dns, color="#1a3a1a", width=120).pack(side="left", padx=4)
        self.status_lbl = make_label(inp, "", color=TEXT2)
        self.status_lbl.pack(pady=(0, 8))

        # Tabs for WHOIS / DNS
        self.tab_bar = ctk.CTkTabview(self, fg_color=CARD, corner_radius=12,
                                       segmented_button_fg_color=BG2,
                                       segmented_button_selected_color=ACCENT,
                                       segmented_button_selected_hover_color=ACCENT_D,
                                       text_color=TEXT)
        self.tab_bar.pack(fill="both", expand=True, padx=20, pady=(0, 14))
        self.tab_bar.add("WHOIS Info")
        self.tab_bar.add("DNS Records")

        self.whois_box = make_result_box(self.tab_bar.tab("WHOIS Info"), height=420)
        self.whois_box.pack(fill="both", expand=True, padx=8, pady=8)

        self.dns_box = make_result_box(self.tab_bar.tab("DNS Records"), height=420)
        self.dns_box.pack(fill="both", expand=True, padx=8, pady=8)

        make_button(self, "💾 Export TXT", self._export, color=BG2, width=130).pack(pady=(0, 10))

    def _status(self, msg, color=TEXT2):
        self.status_lbl.configure(text=msg, text_color=color)

    def _do_whois(self):
        domain = self.domain_entry.get().strip()
        if not domain:
            self._status("⚠ Enter a domain", ORANGE); return
        self._status("⏳ Querying WHOIS...", ACCENT)
        threading.Thread(target=lambda: self.after(0, lambda: self._show_whois(whois_lookup(domain))), daemon=True).start()

    def _do_dns(self):
        domain = self.domain_entry.get().strip()
        if not domain:
            self._status("⚠ Enter a domain", ORANGE); return
        self._status("⏳ Fetching DNS records...", ACCENT)
        threading.Thread(target=lambda: self.after(0, lambda: self._show_dns(dns_lookup(domain))), daemon=True).start()

    def _show_whois(self, d):
        if d.get("error"):
            self._status(f"❌ {d['error']}", RED)
            write_box(self.whois_box, f"Error: {d['error']}"); return
        self._status("✅ WHOIS complete", GREEN)
        lines = [
            "╔══════════════════════════════════════════════╗",
            "║           WHOIS LOOKUP REPORT                ║",
            "╠══════════════════════════════════════════════╣",
            f"  Domain         : {d.get('domain','N/A')}",
            f"  Registrar      : {d.get('registrar','N/A')}",
            f"  Organization   : {d.get('org','N/A')}",
            f"  Registrant     : {d.get('registrant','N/A')}",
            f"  Country        : {d.get('country','N/A')}",
            f"  State          : {d.get('state','N/A')}",
            "",
            f"  Created        : {d.get('creation_date','N/A')}",
            f"  Updated        : {d.get('updated_date','N/A')}",
            f"  Expires        : {d.get('expiration_date','N/A')}",
            "",
            f"  Name Servers   : {d.get('name_servers','N/A')}",
            f"  Status         : {d.get('status','N/A')}",
            f"  Emails         : {d.get('emails','N/A')}",
            f"  DNSSEC         : {d.get('dnssec','N/A')}",
            "╚══════════════════════════════════════════════╝",
        ]
        report = "\n".join(lines)
        write_box(self.whois_box, report)
        self._last = report
        self.tab_bar.set("WHOIS Info")

    def _show_dns(self, records):
        self._status("✅ DNS complete", GREEN)
        lines = ["╔══════════════════════════════════╗",
                 "║        DNS RECORDS               ║",
                 "╠══════════════════════════════════╣"]
        for rtype, vals in records.items():
            lines.append(f"\n  [{rtype}]")
            if vals:
                for v in vals:
                    lines.append(f"    {v}")
            else:
                lines.append("    (none)")
        lines.append("\n╚══════════════════════════════════╝")
        write_box(self.dns_box, "\n".join(lines))
        self.tab_bar.set("DNS Records")

    def _export(self):
        from tkinter import filedialog
        if not hasattr(self, "_last"): return
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files","*.txt")])
        if path:
            with open(path, "w") as f: f.write(self._last)
