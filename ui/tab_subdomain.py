"""Subdomain Enumeration Tab"""

import customtkinter as ctk
import threading
from tkinter import filedialog
from ui.helpers import *
from core.subdomain_enum import enumerate_subdomains, enumerate_subdomains_from_list, COMMON_SUBDOMAINS


class SubdomainTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self._stop_event = threading.Event()
        self._found = []
        self._checked = 0
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="🔗  Subdomain Enumeration", font=FONT_TITLE,
                     text_color=ACCENT).pack(anchor="w", padx=20, pady=(18, 2))
        ctk.CTkLabel(self, text="Brute-force DNS subdomains using built-in or custom wordlist",
                     font=FONT_SMALL, text_color=TEXT2).pack(anchor="w", padx=20, pady=(0, 14))

        inp = ctk.CTkFrame(self, fg_color=CARD, corner_radius=12)
        inp.pack(fill="x", padx=20, pady=(0, 10))
        row1 = ctk.CTkFrame(inp, fg_color="transparent")
        row1.pack(fill="x", padx=16, pady=(12, 4))
        make_label(row1, "Domain:", color=TEXT).pack(side="left", padx=(0, 8))
        self.domain_entry = make_entry(row1, "e.g. example.com", width=320)
        self.domain_entry.pack(side="left", padx=(0, 8))
        self.scan_btn = make_button(row1, "🚀 Start Scan", self._start, width=120)
        self.scan_btn.pack(side="left", padx=4)
        self.stop_btn = make_button(row1, "⏹ Stop", self._stop, color=RED, width=80)
        self.stop_btn.pack(side="left", padx=4)
        self.stop_btn.configure(state="disabled")

        row2 = ctk.CTkFrame(inp, fg_color="transparent")
        row2.pack(fill="x", padx=16, pady=(0, 4))
        make_label(row2, "Wordlist:", color=TEXT2).pack(side="left", padx=(0, 8))
        self.wl_mode = ctk.StringVar(value="built-in")
        ctk.CTkRadioButton(row2, text=f"Built-in ({len(COMMON_SUBDOMAINS)} words)",
                            variable=self.wl_mode, value="built-in",
                            fg_color=ACCENT, text_color=TEXT).pack(side="left", padx=4)
        ctk.CTkRadioButton(row2, text="Custom wordlist",
                            variable=self.wl_mode, value="custom",
                            fg_color=ACCENT, text_color=TEXT).pack(side="left", padx=12)
        make_button(row2, "📂 Browse", self._browse_wl, color=BG2, width=90).pack(side="left", padx=4)
        self.wl_label = make_label(row2, "", font=FONT_SMALL, color=TEXT2)
        self.wl_label.pack(side="left", padx=4)
        self._custom_wl = ""

        prog_row = ctk.CTkFrame(inp, fg_color="transparent")
        prog_row.pack(fill="x", padx=16, pady=(4, 8))
        self.progress = ctk.CTkProgressBar(prog_row, fg_color=BG2, progress_color=ACCENT,
                                            height=6, corner_radius=3)
        self.progress.pack(fill="x")
        self.progress.set(0)

        self.status_lbl = make_label(inp, "Ready", color=TEXT2)
        self.status_lbl.pack(pady=(2, 8))

        # Stats
        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", padx=20, pady=(0, 10))
        for i in range(3): stats.columnconfigure(i, weight=1)
        self.stat_vals = []
        for i, (lbl, color) in enumerate([("✅ Found", GREEN), ("🔍 Checked", ACCENT), ("⏳ Remaining", TEXT2)]):
            c = ctk.CTkFrame(stats, fg_color=CARD, corner_radius=10)
            c.grid(row=0, column=i, padx=4, sticky="ew")
            make_label(c, lbl, font=FONT_SMALL, color=TEXT2).pack(pady=(8, 2))
            v = make_label(c, "0", font=("Segoe UI", 18, "bold"), color=color)
            v.pack(pady=(0, 8))
            self.stat_vals.append(v)

        res = ctk.CTkFrame(self, fg_color=CARD, corner_radius=12)
        res.pack(fill="both", expand=True, padx=20, pady=(0, 14))
        hdr_row = ctk.CTkFrame(res, fg_color="transparent")
        hdr_row.pack(fill="x", padx=14, pady=(10, 4))
        make_label(hdr_row, "Discovered Subdomains", font=FONT_HEAD, color=TEXT).pack(side="left")
        make_button(hdr_row, "💾 Export", self._export, color=BG2, width=90).pack(side="right")
        self.result_box = make_result_box(res, height=340)
        self.result_box.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def _browse_wl(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            self._custom_wl = path
            import os
            self.wl_label.configure(text=os.path.basename(path), text_color=ACCENT)
            self.wl_mode.set("custom")

    def _start(self):
        domain = self.domain_entry.get().strip()
        if not domain:
            self.status_lbl.configure(text="⚠ Enter a domain", text_color=ORANGE); return

        self._found.clear()
        self._checked = 0
        self._stop_event.clear()
        self.progress.set(0)
        for v in self.stat_vals: v.configure(text="0")
        write_box(self.result_box, f"🚀 Scanning subdomains for: {domain}\n\n")
        self.scan_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_lbl.configure(text="⏳ Scanning...", text_color=ACCENT)

        if self.wl_mode.get() == "custom" and self._custom_wl:
            try:
                with open(self._custom_wl, "r", errors="ignore") as f:
                    words = [l.strip() for l in f if l.strip()]
                self._total = len(words)
                threading.Thread(
                    target=enumerate_subdomains_from_list,
                    args=(domain, words, self._cb, self._stop_event),
                    daemon=True
                ).start()
            except Exception as e:
                self.status_lbl.configure(text=f"❌ {e}", text_color=RED)
                self.scan_btn.configure(state="normal"); return
        else:
            self._total = len(COMMON_SUBDOMAINS)
            threading.Thread(
                target=self._run_builtin,
                args=(domain,),
                daemon=True
            ).start()

    def _run_builtin(self, domain):
        enumerate_subdomains(domain, self._cb, self._stop_event)
        self.after(0, self._scan_done)

    def _cb(self, subdomain, ips, status):
        self._checked += 1
        if status == "found":
            self._found.append((subdomain, ips))
            self.after(0, self._update_found, subdomain, ips)
        self.after(0, self._update_progress)

    def _update_found(self, sub, ips):
        ip_str = ", ".join(ips)
        append_box(self.result_box, f"  ✅  {sub:<45} → {ip_str}\n")

    def _update_progress(self):
        total = self._total
        done = self._checked
        pct = min(done / total, 1.0) if total else 0
        self.progress.set(pct)
        self.stat_vals[0].configure(text=str(len(self._found)))
        self.stat_vals[1].configure(text=str(done))
        self.stat_vals[2].configure(text=str(max(0, total - done)))
        if done >= total:
            self._scan_done()

    def _scan_done(self):
        self.status_lbl.configure(
            text=f"✅ Done — {len(self._found)} subdomains found", text_color=GREEN)
        self.scan_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        append_box(self.result_box,
                   f"\n{'─'*60}\n  SCAN COMPLETE: {len(self._found)} subdomains discovered\n")

    def _stop(self):
        self._stop_event.set()
        self.scan_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_lbl.configure(text="⏹ Stopped", text_color=ORANGE)

    def _export(self):
        if not self._found: return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text files", "*.txt")],
            initialfile=f"subdomains_{self.domain_entry.get().strip()}.txt"
        )
        if path:
            with open(path, "w") as f:
                for sub, ips in self._found:
                    f.write(f"{sub}  →  {', '.join(ips)}\n")
