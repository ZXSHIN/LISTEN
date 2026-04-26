"""IP Lookup Tab"""

import customtkinter as ctk
import threading
from ui.helpers import *
from core.ip_lookup import lookup_ip, get_my_ip


class IPTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="🌐  IP Lookup", font=FONT_TITLE,
                     text_color=ACCENT).pack(anchor="w", padx=20, pady=(18, 2))
        ctk.CTkLabel(self, text="Geolocation, ISP, ASN and reverse DNS lookup",
                     font=FONT_SMALL, text_color=TEXT2).pack(anchor="w", padx=20, pady=(0, 14))

        inp = ctk.CTkFrame(self, fg_color=CARD, corner_radius=12)
        inp.pack(fill="x", padx=20, pady=(0, 12))
        row = ctk.CTkFrame(inp, fg_color="transparent")
        row.pack(padx=16, pady=14)
        make_label(row, "Target IP / Domain:", color=TEXT).pack(side="left", padx=(0, 8))
        self.ip_entry = make_entry(row, "e.g. 8.8.8.8 or google.com", width=340)
        self.ip_entry.pack(side="left", padx=(0, 8))
        make_button(row, "🔍 Lookup", self._lookup).pack(side="left", padx=4)
        make_button(row, "📍 My IP", self._my_ip, color=BG2, width=90).pack(side="left", padx=4)
        self.status_lbl = make_label(inp, "", color=TEXT2)
        self.status_lbl.pack(pady=(0, 10))

        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="x", padx=20, pady=(0, 12))
        for i in range(4):
            cards.columnconfigure(i, weight=1)
        labels = ["🌍 Country", "🏙 City/Region", "📡 ISP", "🔢 ASN"]
        self.card_vals = []
        for i, lbl in enumerate(labels):
            card = ctk.CTkFrame(cards, fg_color=CARD, corner_radius=10)
            card.grid(row=0, column=i, padx=4, sticky="ew")
            make_label(card, lbl, font=FONT_SMALL, color=TEXT2).pack(pady=(10, 2))
            val = make_label(card, "—", font=("Segoe UI", 13, "bold"), color=ACCENT)
            val.pack(pady=(0, 10))
            self.card_vals.append(val)

        res = ctk.CTkFrame(self, fg_color=CARD, corner_radius=12)
        res.pack(fill="both", expand=True, padx=20, pady=(0, 14))
        ctk.CTkLabel(res, text="Full Report", font=FONT_HEAD, text_color=TEXT).pack(
            anchor="w", padx=14, pady=(12, 4))
        self.result_box = make_result_box(res, height=380)
        self.result_box.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        make_button(self, "💾 Export TXT", self._export, color=BG2, width=130).pack(pady=(0, 10))

    def _set_status(self, msg, color=TEXT2):
        self.status_lbl.configure(text=msg, text_color=color)

    def _lookup(self):
        ip = self.ip_entry.get().strip()
        if not ip:
            self._set_status("⚠ Please enter an IP or domain", ORANGE)
            return
        self._set_status("⏳ Looking up...", ACCENT)
        threading.Thread(target=self._do_lookup, args=(ip,), daemon=True).start()

    def _my_ip(self):
        self._set_status("⏳ Fetching your IP...", ACCENT)
        def fetch():
            ip = get_my_ip()
            self.after(0, lambda: self.ip_entry.delete(0, "end"))
            self.after(0, lambda: self.ip_entry.insert(0, ip))
            self._do_lookup(ip)
        threading.Thread(target=fetch, daemon=True).start()

    def _do_lookup(self, ip):
        data = lookup_ip(ip)
        self.after(0, lambda: self._display(data))

    def _display(self, d):
        if d.get("error"):
            self._set_status(f"❌ {d['error']}", RED)
            write_box(self.result_box, f"Error: {d['error']}")
            return
        self._set_status("✅ Lookup complete", GREEN)
        self.card_vals[0].configure(text=f"{d.get('country','—')} [{d.get('country_code','—')}]")
        self.card_vals[1].configure(text=f"{d.get('city','—')}, {d.get('region','—')}")
        self.card_vals[2].configure(text=d.get("isp", "—"))
        self.card_vals[3].configure(text=d.get("asn", "—"))
        lat, lon = d.get('lat',''), d.get('lon','')
        report = (
            f"╔══════════════════════════════════════════════╗\n"
            f"║            IP LOOKUP REPORT                  ║\n"
            f"╠══════════════════════════════════════════════╣\n"
            f"  IP Address   : {d.get('ip','N/A')}\n"
            f"  Hostname     : {d.get('hostname','N/A')}\n\n"
            f"  Country      : {d.get('country','N/A')} ({d.get('country_code','N/A')})\n"
            f"  Region       : {d.get('region','N/A')}\n"
            f"  City         : {d.get('city','N/A')}\n"
            f"  ZIP Code     : {d.get('zip','N/A')}\n"
            f"  Coordinates  : {lat}, {lon}\n"
            f"  Timezone     : {d.get('timezone','N/A')}\n\n"
            f"  ISP          : {d.get('isp','N/A')}\n"
            f"  Organization : {d.get('org','N/A')}\n"
            f"  ASN          : {d.get('asn','N/A')}\n\n"
            f"  Google Maps  : https://maps.google.com/?q={lat},{lon}\n"
            f"╚══════════════════════════════════════════════╝"
        )
        write_box(self.result_box, report)
        self._last_report = report

    def _export(self):
        from tkinter import filedialog
        if not hasattr(self, "_last_report"):
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile=f"ip_{self.ip_entry.get().strip()}.txt"
        )
        if path:
            with open(path, "w") as f:
                f.write(self._last_report)
