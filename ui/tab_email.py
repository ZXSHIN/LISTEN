"""Email Recon Tab"""

import customtkinter as ctk
import threading
from ui.helpers import *
from core.email_recon import check_mx, analyze_header


class EmailTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="📧  Email Recon", font=FONT_TITLE,
                     text_color=ACCENT).pack(anchor="w", padx=20, pady=(18, 2))
        ctk.CTkLabel(self, text="Validate email, check MX records, and analyze email headers",
                     font=FONT_SMALL, text_color=TEXT2).pack(anchor="w", padx=20, pady=(0, 14))

        tabs = ctk.CTkTabview(self, fg_color=CARD, corner_radius=12,
                               segmented_button_fg_color=BG2,
                               segmented_button_selected_color=ACCENT,
                               segmented_button_selected_hover_color=ACCENT_D,
                               text_color=TEXT)
        tabs.pack(fill="both", expand=True, padx=20, pady=(0, 14))
        tabs.add("Email Lookup")
        tabs.add("Header Analyzer")

        # ── Email Lookup ──────────────────────────────────────
        elook = tabs.tab("Email Lookup")
        row = ctk.CTkFrame(elook, fg_color="transparent")
        row.pack(fill="x", padx=8, pady=12)
        make_label(row, "Email Address:", color=TEXT).pack(side="left", padx=(0,8))
        self.email_entry = make_entry(row, "user@example.com", width=360)
        self.email_entry.pack(side="left", padx=(0,8))
        make_button(row, "🔍 Analyze", self._check_email).pack(side="left", padx=4)

        self.email_status = make_label(elook, "", color=TEXT2)
        self.email_status.pack(anchor="w", padx=8)

        # Info cards
        cframe = ctk.CTkFrame(elook, fg_color="transparent")
        cframe.pack(fill="x", padx=8, pady=8)
        for i in range(3):
            cframe.columnconfigure(i, weight=1)
        self.email_cards = []
        for i, title in enumerate(["✉ Format", "🏢 Domain MX", "📬 MX Servers"]):
            c = ctk.CTkFrame(cframe, fg_color=BG, corner_radius=10)
            c.grid(row=0, column=i, padx=4, sticky="ew")
            make_label(c, title, font=FONT_SMALL, color=TEXT2).pack(pady=(8,2))
            v = make_label(c, "—", font=("Segoe UI", 12, "bold"), color=ACCENT)
            v.pack(pady=(0,8))
            self.email_cards.append(v)

        self.email_box = make_result_box(elook, height=260)
        self.email_box.pack(fill="both", expand=True, padx=8, pady=(0,8))

        # ── Header Analyzer ──────────────────────────────────
        hdr = tabs.tab("Header Analyzer")
        make_label(hdr, "Paste raw email header below:", color=TEXT2).pack(anchor="w", padx=8, pady=(10,4))
        self.header_input = ctk.CTkTextbox(hdr, height=180, font=FONT_MONO,
                                            fg_color=BG2, text_color=TEXT,
                                            border_color=BORDER, border_width=1)
        self.header_input.pack(fill="x", padx=8, pady=(0,8))
        make_button(hdr, "🔎 Analyze Header", self._analyze_header, width=160).pack(pady=4)
        self.header_box = make_result_box(hdr, height=280)
        self.header_box.pack(fill="both", expand=True, padx=8, pady=(4,8))

    def _check_email(self):
        email = self.email_entry.get().strip()
        if not email:
            self.email_status.configure(text="⚠ Enter an email", text_color=ORANGE); return
        self.email_status.configure(text="⏳ Checking...", text_color=ACCENT)
        threading.Thread(target=lambda: self.after(0, lambda: self._show_email(check_mx(email))), daemon=True).start()

    def _show_email(self, d):
        if d.get("error") and not d.get("valid_format"):
            self.email_status.configure(text=f"❌ {d['error']}", text_color=RED)
            self.email_cards[0].configure(text="❌ Invalid", text_color=RED)
            write_box(self.email_box, f"Error: {d['error']}"); return

        self.email_status.configure(text="✅ Analysis complete", text_color=GREEN)
        self.email_cards[0].configure(text="✅ Valid" if d["valid_format"] else "❌ Invalid",
                                       text_color=GREEN if d["valid_format"] else RED)
        has_mx = d.get("domain_has_mx", False)
        self.email_cards[1].configure(text="✅ Active" if has_mx else "❌ No MX",
                                       text_color=GREEN if has_mx else RED)
        mx_list = d.get("mx_records", [])
        self.email_cards[2].configure(text=str(len(mx_list)) + " server(s)", text_color=ACCENT)

        lines = [f"  Email    : {d['email']}", f"  Format   : {'✅ Valid' if d['valid_format'] else '❌ Invalid'}"]
        if d.get("error"):
            lines.append(f"  Error    : {d['error']}")
        if mx_list:
            lines.append("\n  MX Records:")
            for pref, exch in mx_list:
                lines.append(f"    [{pref:3}] {exch}")
        write_box(self.email_box, "\n".join(lines))

    def _analyze_header(self):
        raw = self.header_input.get("1.0", "end").strip()
        if not raw:
            write_box(self.header_box, "⚠ Please paste an email header first."); return
        d = analyze_header(raw)
        lines = ["╔══════ EMAIL HEADER ANALYSIS ══════╗"]
        if d.get("from"):    lines.append(f"  From        : {d['from'][0]}")
        if d.get("to"):      lines.append(f"  To          : {d['to'][0]}")
        if d.get("subject"): lines.append(f"  Subject     : {d['subject']}")
        if d.get("date"):    lines.append(f"  Date        : {d['date']}")
        if d.get("message_id"): lines.append(f"  Message-ID  : {d['message_id']}")
        if d.get("spam_score"):  lines.append(f"  Spam Status : {d['spam_score']}")
        if d.get("x_originating_ip"): lines.append(f"  Origin IP   : {d['x_originating_ip']}")
        if d.get("ips"):
            lines.append("\n  IPs Found in Routing:")
            for ip in d["ips"]:
                lines.append(f"    • {ip}")
        if d.get("received_from"):
            lines.append(f"\n  Hops : {len(d['received_from'])}")
        if d.get("error"): lines.append(f"\n  Error: {d['error']}")
        lines.append("╚════════════════════════════════════╝")
        write_box(self.header_box, "\n".join(lines))
