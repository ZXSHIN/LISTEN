"""Shodan Recon Tab"""

import customtkinter as ctk
import threading
from tkinter import filedialog
from ui.helpers import *
from core.shodan_recon import host_lookup, search_shodan, get_api_info


class ShodanTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self._results = []
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="🛡  Shodan Intelligence", font=FONT_TITLE,
                     text_color=ACCENT).pack(anchor="w", padx=20, pady=(18, 2))
        ctk.CTkLabel(self, text="Search exposed devices, services, and vulnerabilities using Shodan API",
                     font=FONT_SMALL, text_color=TEXT2).pack(anchor="w", padx=20, pady=(0, 14))

        tabs = ctk.CTkTabview(self, fg_color=CARD, corner_radius=12,
                               segmented_button_fg_color=BG2,
                               segmented_button_selected_color=ACCENT,
                               segmented_button_selected_hover_color=ACCENT_D,
                               text_color=TEXT)
        tabs.pack(fill="both", expand=True, padx=20, pady=(0, 14))
        tabs.add("Host Lookup")
        tabs.add("Search Query")
        tabs.add("API Info")

        # ── Host Lookup ──────────────────────────────────────────────────────
        hl = tabs.tab("Host Lookup")
        row = ctk.CTkFrame(hl, fg_color="transparent")
        row.pack(fill="x", padx=8, pady=12)
        make_label(row, "IP Address:", color=TEXT).pack(side="left", padx=(0, 8))
        self.ip_entry = make_entry(row, "e.g. 8.8.8.8", width=300)
        self.ip_entry.pack(side="left", padx=(0, 8))
        make_button(row, "🔍 Lookup", self._host_lookup).pack(side="left", padx=4)
        self.host_status = make_label(hl, "", color=TEXT2)
        self.host_status.pack(anchor="w", padx=8)

        # Summary cards
        cframe = ctk.CTkFrame(hl, fg_color="transparent")
        cframe.pack(fill="x", padx=8, pady=8)
        for i in range(4): cframe.columnconfigure(i, weight=1)
        self.host_cards = []
        for i, lbl in enumerate(["🏢 Org", "🌍 Country", "🔌 Ports", "⚠ Vulns"]):
            c = ctk.CTkFrame(cframe, fg_color=BG, corner_radius=10)
            c.grid(row=0, column=i, padx=3, sticky="ew")
            make_label(c, lbl, font=FONT_SMALL, color=TEXT2).pack(pady=(8, 2))
            v = make_label(c, "—", font=("Segoe UI", 12, "bold"),
                           color=[ACCENT, ACCENT, GREEN, RED][i])
            v.pack(pady=(0, 8))
            self.host_cards.append(v)

        self.host_box = make_result_box(hl, height=310)
        self.host_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # ── Search Query ────────────────────────────────────────────────────
        sq = tabs.tab("Search Query")

        # Quick filters
        make_label(sq, "Quick Filters:", color=TEXT2).pack(anchor="w", padx=8, pady=(10, 4))
        qf = ctk.CTkScrollableFrame(sq, fg_color=BG2, height=90, corner_radius=8)
        qf.pack(fill="x", padx=8, pady=(0, 8))
        quick_queries = [
            ("Apache", "product:Apache"), ("nginx", "product:nginx"),
            ("IIS", "product:IIS"), ("MySQL", "product:MySQL"),
            ("MongoDB", "product:MongoDB"), ("Redis", "product:Redis"),
            ("FTP Anonymous", "port:21 anonymous"), ("RDP Open", "port:3389"),
            ("SSH", "port:22"), ("Webcams", "has_screenshot:true"),
            ("Vuln Heartbleed", "vuln:CVE-2014-0160"),
            ("Printers", "port:9100"), ("Telnet", "port:23"),
            ("Industrial", "tag:ics"), ("Router", 'product:"RouterOS"'),
        ]
        for i, (label, q) in enumerate(quick_queries):
            btn = ctk.CTkButton(
                qf, text=label, width=100, height=26,
                fg_color=BG, hover_color=BORDER, text_color=ACCENT,
                font=FONT_SMALL, corner_radius=6,
                command=lambda ql=q: self._set_query(ql)
            )
            btn.grid(row=i // 5, column=i % 5, padx=3, pady=2)

        row2 = ctk.CTkFrame(sq, fg_color="transparent")
        row2.pack(fill="x", padx=8, pady=(0, 8))
        make_label(row2, "Query:", color=TEXT).pack(side="left", padx=(0, 8))
        self.query_entry = make_entry(row2, 'e.g. port:22 country:"ID"', width=360)
        self.query_entry.pack(side="left", padx=(0, 8))
        make_button(row2, "🔍 Search", self._search).pack(side="left", padx=4)

        self.search_status = make_label(sq, "", color=TEXT2)
        self.search_status.pack(anchor="w", padx=8)

        self.search_box = make_result_box(sq, height=330)
        self.search_box.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        exp_row = ctk.CTkFrame(sq, fg_color="transparent")
        exp_row.pack(pady=(0, 6))
        make_button(exp_row, "💾 Export Results", self._export, color=BG2, width=140).pack()

        # ── API Info ─────────────────────────────────────────────────────────
        ai = tabs.tab("API Info")
        make_button(ai, "🔄 Load API Info", self._load_api_info, width=160).pack(padx=8, pady=12)
        self.api_box = make_result_box(ai, height=440)
        self.api_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _host_lookup(self):
        ip = self.ip_entry.get().strip()
        if not ip:
            self.host_status.configure(text="⚠ Enter an IP", text_color=ORANGE); return
        self.host_status.configure(text="⏳ Querying Shodan...", text_color=ACCENT)
        threading.Thread(
            target=lambda: self.after(0, lambda: self._show_host(host_lookup(ip))),
            daemon=True
        ).start()

    def _show_host(self, d):
        if d.get("error"):
            self.host_status.configure(text=f"❌ {d['error']}", text_color=RED)
            write_box(self.host_box, f"Error: {d['error']}"); return
        self.host_status.configure(text="✅ Done", text_color=GREEN)
        self.host_cards[0].configure(text=(d.get("organization") or "—")[:20])
        self.host_cards[1].configure(text=d.get("country", "—"))
        self.host_cards[2].configure(text=str(len(d.get("ports", []))))
        vulns = d.get("vulns", [])
        self.host_cards[3].configure(text=str(len(vulns)),
                                      text_color=RED if vulns else GREEN)

        lines = [
            "╔══════════════════════════════════════════════════╗",
            "║             SHODAN HOST REPORT                   ║",
            "╠══════════════════════════════════════════════════╣",
            f"  IP           : {d.get('ip','N/A')}",
            f"  Organization : {d.get('organization','N/A')}",
            f"  ISP          : {d.get('isp','N/A')}",
            f"  ASN          : {d.get('asn','N/A')}",
            f"  Country      : {d.get('country','N/A')}",
            f"  City         : {d.get('city','N/A')}",
            f"  OS           : {d.get('os','N/A')}",
            f"  Last Update  : {d.get('last_update','N/A')}",
            f"  Hostnames    : {', '.join(d.get('hostnames',[])) or 'None'}",
            f"  Domains      : {', '.join(d.get('domains',[])) or 'None'}",
            f"  Tags         : {', '.join(d.get('tags',[])) or 'None'}",
            f"  Open Ports   : {', '.join(map(str, d.get('ports',[]))) or 'None'}",
        ]
        if vulns:
            lines.append(f"\n  ⚠ VULNERABILITIES ({len(vulns)}):")
            for v in vulns:
                lines.append(f"    • {v}")
        if d.get("services"):
            lines.append(f"\n  SERVICES ({len(d['services'])}):")
            for svc in d["services"]:
                prod = f"{svc.get('product','')} {svc.get('version','')}".strip()
                lines.append(f"    [{svc.get('port')}/{svc.get('transport','tcp')}]  {prod}")
                if svc.get("vulns"):
                    lines.append(f"      Vulns: {', '.join(svc['vulns'])}")
        lines.append("╚══════════════════════════════════════════════════╝")
        write_box(self.host_box, "\n".join(lines))

    def _set_query(self, q):
        self.query_entry.delete(0, "end")
        self.query_entry.insert(0, q)

    def _search(self):
        q = self.query_entry.get().strip()
        if not q:
            self.search_status.configure(text="⚠ Enter a query", text_color=ORANGE); return
        self.search_status.configure(text="⏳ Searching Shodan...", text_color=ACCENT)
        self._results.clear()
        threading.Thread(
            target=lambda: self.after(0, lambda: self._show_search(search_shodan(q))),
            daemon=True
        ).start()

    def _show_search(self, d):
        if d.get("error"):
            self.search_status.configure(text=f"❌ {d['error']}", text_color=RED)
            write_box(self.search_box, f"Error: {d['error']}"); return
        matches = d.get("matches", [])
        total = d.get("total", 0)
        self.search_status.configure(
            text=f"✅ {total:,} total results — showing {len(matches)}", text_color=GREEN)

        self._results = matches
        lines = [
            f"╔══ SHODAN SEARCH: {d['query']} ══╗",
            f"  Total Results : {total:,}",
            f"  Showing       : {len(matches)}",
            "─" * 60,
        ]
        for m in matches:
            lines.append(
                f"\n  IP      : {m.get('ip','')}:{m.get('port','')}"
            )
            lines.append(f"  Org     : {m.get('org','N/A')}")
            lines.append(f"  Country : {m.get('country','N/A')} / {m.get('city','N/A')}")
            if m.get("product"):
                lines.append(f"  Product : {m.get('product','')} {m.get('version','')}")
            if m.get("hostnames"):
                lines.append(f"  Host    : {', '.join(m['hostnames'][:3])}")
            if m.get("vulns"):
                lines.append(f"  Vulns   : {', '.join(m['vulns'])}")
            if m.get("banner"):
                banner_lines = m["banner"].replace("\r", "").split("\n")[:3]
                for bl in banner_lines:
                    if bl.strip():
                        lines.append(f"  Banner  : {bl.strip()[:80]}")
            lines.append("  " + "─" * 56)
        write_box(self.search_box, "\n".join(lines))

    def _load_api_info(self):
        write_box(self.api_box, "⏳ Loading API info...")
        threading.Thread(
            target=lambda: self.after(0, lambda: self._show_api(get_api_info())),
            daemon=True
        ).start()

    def _show_api(self, d):
        if d.get("error"):
            write_box(self.api_box, f"❌ Error: {d['error']}"); return
        lines = [
            "╔══════════════════════════════════════╗",
            "║         SHODAN API INFORMATION       ║",
            "╠══════════════════════════════════════╣",
        ]
        for k, v in d.items():
            if k != "error":
                lines.append(f"  {k:<25}: {v}")
        lines.append("╚══════════════════════════════════════╝")
        write_box(self.api_box, "\n".join(lines))

    def _export(self):
        if not self._results: return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text files", "*.txt")]
        )
        if path:
            with open(path, "w") as f:
                for m in self._results:
                    f.write(f"{m.get('ip')}:{m.get('port')}  {m.get('org','N/A')}  "
                            f"{m.get('country','N/A')}\n")
