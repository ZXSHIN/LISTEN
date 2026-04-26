"""Phone Lookup Tab"""

import customtkinter as ctk
import threading
from ui.helpers import *
from core.phone_recon import lookup_phone


class PhoneTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="📱  Phone Lookup", font=FONT_TITLE,
                     text_color=ACCENT).pack(anchor="w", padx=20, pady=(18, 2))
        ctk.CTkLabel(self, text="Identify country, carrier, and type from phone number",
                     font=FONT_SMALL, text_color=TEXT2).pack(anchor="w", padx=20, pady=(0, 14))

        inp = ctk.CTkFrame(self, fg_color=CARD, corner_radius=12)
        inp.pack(fill="x", padx=20, pady=(0, 12))
        row = ctk.CTkFrame(inp, fg_color="transparent")
        row.pack(padx=16, pady=14)
        make_label(row, "Phone Number:", color=TEXT).pack(side="left", padx=(0, 8))
        self.phone_entry = make_entry(row, "+62 812 3456 7890  (include country code)", width=380)
        self.phone_entry.pack(side="left", padx=(0, 8))
        make_button(row, "🔍 Lookup", self._lookup).pack(side="left", padx=4)
        self.status_lbl = make_label(inp, "", color=TEXT2)
        self.status_lbl.pack(pady=(0, 8))

        # Info cards
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="x", padx=20, pady=(0, 12))
        for i in range(4): cards.columnconfigure(i, weight=1)
        self.card_vals = []
        for i, lbl in enumerate(["🌍 Country", "📡 Carrier", "📞 Type", "⏰ Timezone"]):
            c = ctk.CTkFrame(cards, fg_color=CARD, corner_radius=10)
            c.grid(row=0, column=i, padx=4, sticky="ew")
            make_label(c, lbl, font=FONT_SMALL, color=TEXT2).pack(pady=(10, 2))
            v = make_label(c, "—", font=("Segoe UI", 12, "bold"), color=ACCENT)
            v.pack(pady=(0, 10))
            self.card_vals.append(v)

        res = ctk.CTkFrame(self, fg_color=CARD, corner_radius=12)
        res.pack(fill="both", expand=True, padx=20, pady=(0, 14))
        ctk.CTkLabel(res, text="Full Report", font=FONT_HEAD, text_color=TEXT).pack(
            anchor="w", padx=14, pady=(12, 4))
        self.result_box = make_result_box(res, height=380)
        self.result_box.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        # Tip
        tip = ctk.CTkFrame(self, fg_color=CARD, corner_radius=8)
        tip.pack(fill="x", padx=20, pady=(0, 10))
        make_label(tip, "💡 Tip: Always include the country code.  Examples: +1 (US), +62 (ID), +44 (UK), +91 (IN)",
                   font=FONT_SMALL, color=TEXT2).pack(pady=8)

    def _lookup(self):
        num = self.phone_entry.get().strip()
        if not num:
            self.status_lbl.configure(text="⚠ Enter a phone number", text_color=ORANGE); return
        self.status_lbl.configure(text="⏳ Looking up...", text_color=ACCENT)
        threading.Thread(target=lambda: self.after(0, lambda: self._display(lookup_phone(num))), daemon=True).start()

    def _display(self, d):
        if d.get("error"):
            self.status_lbl.configure(text=f"❌ {d['error']}", text_color=RED)
            write_box(self.result_box, f"Error: {d['error']}"); return

        self.status_lbl.configure(text="✅ Lookup complete", text_color=GREEN)
        tzs = d.get("timezones", [])
        self.card_vals[0].configure(text=d.get("country", "—"))
        self.card_vals[1].configure(text=d.get("carrier", "—") or "Unknown")
        self.card_vals[2].configure(text=d.get("number_type", "—"))
        self.card_vals[3].configure(text=tzs[0] if tzs else "—")

        report = (
            f"╔══════════════════════════════════════════════╗\n"
            f"║         PHONE NUMBER REPORT                  ║\n"
            f"╠══════════════════════════════════════════════╣\n"
            f"  Input            : {d.get('number','N/A')}\n"
            f"  International    : {d.get('international_format','N/A')}\n"
            f"  National         : {d.get('national_format','N/A')}\n"
            f"  E.164 Format     : {d.get('e164_format','N/A')}\n"
            f"  Country Code     : {d.get('country_code','N/A')}\n\n"
            f"  Country          : {d.get('country','N/A')}\n"
            f"  Carrier / ISP    : {d.get('carrier','N/A') or 'N/A'}\n"
            f"  Number Type      : {d.get('number_type','N/A')}\n"
            f"  Timezones        : {', '.join(tzs) or 'N/A'}\n\n"
            f"  Valid            : {'✅ Yes' if d.get('is_valid') else '❌ No'}\n"
            f"  Possible         : {'✅ Yes' if d.get('is_possible') else '❌ No'}\n"
            f"╚══════════════════════════════════════════════╝"
        )
        write_box(self.result_box, report)
