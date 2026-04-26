"""Username Recon Tab"""

import customtkinter as ctk
import threading
from ui.helpers import *
from core.username_recon import check_username, PLATFORMS


class UsernameTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self._stop_event = threading.Event()
        self._results = []
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="👤  Username Recon", font=FONT_TITLE,
                     text_color=ACCENT).pack(anchor="w", padx=20, pady=(18, 2))
        ctk.CTkLabel(self, text=f"Hunt username across {len(PLATFORMS)} platforms simultaneously",
                     font=FONT_SMALL, text_color=TEXT2).pack(anchor="w", padx=20, pady=(0, 14))

        inp = ctk.CTkFrame(self, fg_color=CARD, corner_radius=12)
        inp.pack(fill="x", padx=20, pady=(0, 10))
        row = ctk.CTkFrame(inp, fg_color="transparent")
        row.pack(padx=16, pady=14)
        make_label(row, "Username:", color=TEXT).pack(side="left", padx=(0, 8))
        self.user_entry = make_entry(row, "e.g. john_doe", width=300)
        self.user_entry.pack(side="left", padx=(0, 8))
        self.scan_btn = make_button(row, "🚀 Scan All", self._start_scan, width=110)
        self.scan_btn.pack(side="left", padx=4)
        self.stop_btn = make_button(row, "⏹ Stop", self._stop_scan, color=RED, width=80)
        self.stop_btn.pack(side="left", padx=4)
        self.stop_btn.configure(state="disabled")

        # Progress
        prog_frame = ctk.CTkFrame(inp, fg_color="transparent")
        prog_frame.pack(fill="x", padx=16, pady=(0, 8))
        self.progress = ctk.CTkProgressBar(prog_frame, fg_color=BG2, progress_color=ACCENT,
                                            height=6, corner_radius=3)
        self.progress.pack(fill="x")
        self.progress.set(0)
        self.status_lbl = make_label(inp, f"0 / {len(PLATFORMS)} checked  •  0 found", color=TEXT2)
        self.status_lbl.pack(pady=(0, 8))

        # Stats row
        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", padx=20, pady=(0, 10))
        for i in range(3): stats.columnconfigure(i, weight=1)
        self.stat_vals = []
        for i, lbl in enumerate(["✅ Found", "❌ Not Found", "⚠️ Other"]):
            c = ctk.CTkFrame(stats, fg_color=CARD, corner_radius=10)
            c.grid(row=0, column=i, padx=4, sticky="ew")
            make_label(c, lbl, font=FONT_SMALL, color=TEXT2).pack(pady=(8, 2))
            v = make_label(c, "0", font=("Segoe UI", 18, "bold"),
                           color=[GREEN, RED, ORANGE][i])
            v.pack(pady=(0, 8))
            self.stat_vals.append(v)

        # Results
        res = ctk.CTkFrame(self, fg_color=CARD, corner_radius=12)
        res.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        hdr_row = ctk.CTkFrame(res, fg_color="transparent")
        hdr_row.pack(fill="x", padx=14, pady=(10, 4))
        make_label(hdr_row, "Results", font=FONT_HEAD, color=TEXT).pack(side="left")
        make_button(hdr_row, "💾 Export", self._export, color=BG2, width=90).pack(side="right")
        make_button(hdr_row, "🧹 Clear", self._clear, color=BG2, width=80).pack(side="right", padx=4)

        self.result_box = make_result_box(res, height=340)
        self.result_box.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def _start_scan(self):
        username = self.user_entry.get().strip()
        if not username:
            self.status_lbl.configure(text="⚠ Enter a username", text_color=ORANGE); return
        self._results.clear()
        self._stop_event.clear()
        self._checked = 0
        self._found = self._not_found = self._other = 0
        for v in self.stat_vals: v.configure(text="0")
        self.progress.set(0)
        write_box(self.result_box, f"🚀 Scanning '{username}' across {len(PLATFORMS)} platforms...\n\n")
        self.scan_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")

        threading.Thread(
            target=check_username,
            args=(username, self._cb, self._stop_event),
            daemon=True
        ).start()

    def _cb(self, platform, url, status):
        self._results.append((platform, url, status))
        self._checked += 1
        if "✅" in status: self._found += 1
        elif "❌" in status: self._not_found += 1
        else: self._other += 1
        self.after(0, self._update_ui, platform, url, status)

    def _update_ui(self, platform, url, status):
        total = len(PLATFORMS)
        done = self._checked
        self.progress.set(done / total)
        self.status_lbl.configure(
            text=f"{done} / {total} checked  •  {self._found} found",
            text_color=TEXT2
        )
        self.stat_vals[0].configure(text=str(self._found))
        self.stat_vals[1].configure(text=str(self._not_found))
        self.stat_vals[2].configure(text=str(self._other))
        line = f"  {status}  {platform:<20} {url}\n"
        append_box(self.result_box, line)
        if done >= total:
            append_box(self.result_box, f"\n{'─'*60}\n")
            append_box(self.result_box, f"  SCAN COMPLETE: {self._found} profiles found out of {total} platforms\n")
            self.scan_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")

    def _stop_scan(self):
        self._stop_event.set()
        self.scan_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def _clear(self):
        self._results.clear()
        self._stop_event.set()
        write_box(self.result_box, "")
        self.progress.set(0)
        self.status_lbl.configure(text=f"0 / {len(PLATFORMS)} checked  •  0 found")
        for v in self.stat_vals: v.configure(text="0")

    def _export(self):
        from tkinter import filedialog
        if not self._results: return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text files", "*.txt")],
            initialfile=f"username_{self.user_entry.get().strip()}.txt"
        )
        if path:
            with open(path, "w") as f:
                for plat, url, status in self._results:
                    f.write(f"{status}  {plat:<20}  {url}\n")
