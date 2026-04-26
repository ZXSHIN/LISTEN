"""Metadata Extractor Tab"""

import customtkinter as ctk
import threading
import os
from tkinter import filedialog
from ui.helpers import *
from core.metadata_extractor import extract_metadata


class MetadataTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="🗂  Metadata Extractor", font=FONT_TITLE,
                     text_color=ACCENT).pack(anchor="w", padx=20, pady=(18, 2))
        ctk.CTkLabel(self, text="Extract EXIF, GPS, author info from images, PDFs, and documents",
                     font=FONT_SMALL, text_color=TEXT2).pack(anchor="w", padx=20, pady=(0, 14))

        # Drop zone / file selector
        drop = ctk.CTkFrame(self, fg_color=CARD, corner_radius=12)
        drop.pack(fill="x", padx=20, pady=(0, 12))

        inner = ctk.CTkFrame(drop, fg_color=BG2, corner_radius=10)
        inner.pack(fill="x", padx=16, pady=16)
        ctk.CTkLabel(inner, text="📂  Select a file to analyze",
                     font=("Segoe UI", 13), text_color=TEXT2).pack(pady=(16, 6))
        ctk.CTkLabel(inner, text="Supported: JPG, PNG, TIFF, BMP, WEBP  |  PDF  |  DOCX",
                     font=FONT_SMALL, text_color=TEXT2).pack()

        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(pady=12)
        make_button(btn_row, "📂 Browse File", self._browse).pack(side="left", padx=6)
        make_button(btn_row, "🔍 Extract", self._extract, width=100).pack(side="left", padx=6)

        self.file_label = make_label(inner, "No file selected", font=FONT_SMALL, color=TEXT2)
        self.file_label.pack(pady=(0, 10))
        self.status_lbl = make_label(drop, "", color=TEXT2)
        self.status_lbl.pack(pady=(0, 8))

        # Info cards (dynamic, shown after extraction)
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=20, pady=(0, 12))

        # Results
        res = ctk.CTkFrame(self, fg_color=CARD, corner_radius=12)
        res.pack(fill="both", expand=True, padx=20, pady=(0, 14))
        hdr_row = ctk.CTkFrame(res, fg_color="transparent")
        hdr_row.pack(fill="x", padx=14, pady=(10, 4))
        make_label(hdr_row, "Extracted Metadata", font=FONT_HEAD, color=TEXT).pack(side="left")
        make_button(hdr_row, "💾 Export", self._export, color=BG2, width=90).pack(side="right")
        self.result_box = make_result_box(res, height=360)
        self.result_box.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self._filepath = ""

    def _browse(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("Supported files", "*.jpg *.jpeg *.png *.tiff *.bmp *.webp *.pdf *.docx *.doc"),
                ("All files", "*.*"),
            ]
        )
        if path:
            self._filepath = path
            fname = os.path.basename(path)
            size = os.path.getsize(path)
            self.file_label.configure(
                text=f"📄 {fname}  ({size:,} bytes)",
                text_color=ACCENT
            )

    def _extract(self):
        if not self._filepath:
            self.status_lbl.configure(text="⚠ Select a file first", text_color=ORANGE); return
        self.status_lbl.configure(text="⏳ Extracting metadata...", text_color=ACCENT)
        write_box(self.result_box, "")
        threading.Thread(
            target=lambda: self.after(0, lambda: self._display(extract_metadata(self._filepath))),
            daemon=True
        ).start()

    def _display(self, d):
        if d.get("error"):
            self.status_lbl.configure(text=f"❌ {d['error']}", text_color=RED)
            write_box(self.result_box, f"Error: {d['error']}"); return

        self.status_lbl.configure(text="✅ Extraction complete", text_color=GREEN)
        meta = d.get("metadata", {})
        self._last_meta = meta

        # Build report
        lines = [
            "╔══════════════════════════════════════════════════╗",
            "║           METADATA EXTRACTION REPORT             ║",
            "╠══════════════════════════════════════════════════╣",
            f"  File : {os.path.basename(d['file'])}",
            "",
        ]

        # Highlight GPS if present
        gps_lat = meta.get("GPS Latitude")
        gps_lon = meta.get("GPS Longitude")
        if gps_lat and gps_lon:
            lines.append(f"  ⚠ GPS COORDINATES FOUND!")
            lines.append(f"  Latitude   : {gps_lat}")
            lines.append(f"  Longitude  : {gps_lon}")
            lines.append(f"  Maps Link  : {meta.get('Google Maps','')}")
            lines.append("")

        for k, v in meta.items():
            if k not in ("GPS Latitude", "GPS Longitude", "Google Maps"):
                lines.append(f"  {k:<25}: {v}")

        lines.append("╚══════════════════════════════════════════════════╝")
        write_box(self.result_box, "\n".join(lines))

    def _export(self):
        if not hasattr(self, "_last_meta"): return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text files", "*.txt")]
        )
        if path:
            with open(path, "w") as f:
                for k, v in self._last_meta.items():
                    f.write(f"{k}: {v}\n")
