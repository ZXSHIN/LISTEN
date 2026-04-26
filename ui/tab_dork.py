"""Google Dorking Tab"""

import customtkinter as ctk
import threading
import tkinter as tk
from ui.helpers import *
from core.dork_engine import DorkEngine


class DorkTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG)
        self.engine = DorkEngine()
        self._build()

    def _build(self):
        # Title
        ctk.CTkLabel(self, text="🔍  Google Dorking", font=FONT_TITLE,
                     text_color=ACCENT).pack(anchor="w", padx=20, pady=(18, 2))
        ctk.CTkLabel(self, text="Generate & launch powerful Google dork queries",
                     font=FONT_SMALL, text_color=TEXT2).pack(anchor="w", padx=20, pady=(0, 14))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=0)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)

        # ── Left: Template Selector ──────────────────────────────────────────
        left = ctk.CTkFrame(content, fg_color=CARD, corner_radius=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)

        ctk.CTkLabel(left, text="Template Library", font=FONT_HEAD,
                     text_color=TEXT).pack(anchor="w", padx=14, pady=(12, 6))

        cats = self.engine.get_categories()
        self.cat_var = ctk.StringVar(value=cats[0])
        cat_menu = ctk.CTkOptionMenu(
            left, values=cats, variable=self.cat_var,
            command=self._on_cat_change,
            fg_color=BG2, button_color=ACCENT, button_hover_color=ACCENT_D,
            text_color=TEXT, font=FONT_BODY, width=260,
        )
        cat_menu.pack(padx=14, pady=(0, 8))

        self.template_list = ctk.CTkScrollableFrame(left, fg_color=BG, height=200,
                                                     corner_radius=8)
        self.template_list.pack(fill="x", padx=14, pady=(0, 10))
        self._load_templates(cats[0])

        # Target field
        ctk.CTkLabel(left, text="Target (optional):", font=FONT_BODY,
                     text_color=TEXT2).pack(anchor="w", padx=14)
        self.target_entry = make_entry(left, "example.com", width=260)
        self.target_entry.pack(padx=14, pady=(4, 10))

        # ── Left: Custom Builder ──────────────────────────────────────────────
        ctk.CTkLabel(left, text="Custom Dork Builder", font=FONT_HEAD,
                     text_color=TEXT).pack(anchor="w", padx=14, pady=(6, 4))

        fields = [
            ("site:", "site_e", "example.com"),
            ("inurl:", "inurl_e", "admin"),
            ("intitle:", "intitle_e", "Login"),
            ("filetype:", "filetype_e", "pdf"),
            ("intext:", "intext_e", "password"),
            ("ext:", "ext_e", "sql"),
            ("Custom:", "custom_e", 'OR "backup"'),
        ]
        for label, attr, ph in fields:
            row = ctk.CTkFrame(left, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=2)
            ctk.CTkLabel(row, text=label, font=FONT_SMALL, text_color=TEXT2,
                         width=65, anchor="e").pack(side="left")
            e = make_entry(row, ph, width=185)
            e.pack(side="left", padx=(4, 0))
            setattr(self, attr, e)

        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.pack(pady=10)
        make_button(btn_row, "⚙ Build", self._build_dork, width=100).pack(side="left", padx=4)
        make_button(btn_row, "🗑 Clear", self._clear_builder, color=BG2, width=80).pack(side="left", padx=4)

        # ── Right: Query & Results ────────────────────────────────────────────
        right = ctk.CTkFrame(content, fg_color=CARD, corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=0)

        ctk.CTkLabel(right, text="Generated Query", font=FONT_HEAD,
                     text_color=TEXT).pack(anchor="w", padx=14, pady=(12, 4))

        self.query_box = ctk.CTkTextbox(right, height=60, font=FONT_MONO,
                                         fg_color=BG, text_color=GREEN,
                                         border_color=BORDER, border_width=1)
        self.query_box.pack(fill="x", padx=14, pady=(0, 8))

        launch_row = ctk.CTkFrame(right, fg_color="transparent")
        launch_row.pack(pady=4)
        make_button(launch_row, "🌐 Google", lambda: self._open("google"), width=100).pack(side="left", padx=4)
        make_button(launch_row, "🔵 Bing", lambda: self._open("bing"), color="#1e3a5f", width=90).pack(side="left", padx=4)
        make_button(launch_row, "🦆 DDG", lambda: self._open("ddg"), color="#1e3a1e", width=90).pack(side="left", padx=4)
        make_button(launch_row, "📋 Copy", self._copy_query, color=BG2, width=80).pack(side="left", padx=4)

        ctk.CTkLabel(right, text="Dork Cheat Sheet", font=FONT_HEAD,
                     text_color=TEXT).pack(anchor="w", padx=14, pady=(14, 4))
        self.result_box = make_result_box(right, height=380)
        self.result_box.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self._load_cheatsheet()

    def _load_templates(self, category):
        for w in self.template_list.winfo_children():
            w.destroy()
        templates = self.engine.get_templates(category)
        for t in templates:
            btn = ctk.CTkButton(
                self.template_list, text=t, anchor="w",
                fg_color="transparent", hover_color=BORDER,
                text_color=ACCENT, font=FONT_MONO, height=26,
                command=lambda tmpl=t: self._use_template(tmpl)
            )
            btn.pack(fill="x", pady=1)

    def _on_cat_change(self, cat):
        self._load_templates(cat)

    def _use_template(self, tmpl):
        target = self.target_entry.get().strip()
        q = self.engine.apply_target(tmpl, target) if target else tmpl
        write_box(self.query_box, q)

    def _build_dork(self):
        q = self.engine.build_custom_dork(
            site=self.site_e.get().strip(),
            inurl=self.inurl_e.get().strip(),
            intitle=self.intitle_e.get().strip(),
            filetype=self.filetype_e.get().strip(),
            intext=self.intext_e.get().strip(),
            ext=self.ext_e.get().strip(),
            custom=self.custom_e.get().strip(),
        )
        write_box(self.query_box, q)

    def _clear_builder(self):
        for attr in ["site_e", "inurl_e", "intitle_e", "filetype_e",
                     "intext_e", "ext_e", "custom_e"]:
            getattr(self, attr).delete(0, "end")
        clear_box(self.query_box)

    def _get_query(self):
        return self.query_box.get("1.0", "end").strip()

    def _open(self, engine):
        q = self._get_query()
        if not q:
            self._build_dork()
            q = self._get_query()
        if not q:
            return
        if engine == "google":
            self.engine.open_google(q)
        elif engine == "bing":
            self.engine.open_bing(q)
        else:
            self.engine.open_duckduckgo(q)

    def _copy_query(self):
        q = self._get_query()
        self.clipboard_clear()
        self.clipboard_append(q)

    def _load_cheatsheet(self):
        cheat = """╔══════════════════════════════════════════════════════════════╗
║               GOOGLE DORK OPERATOR CHEATSHEET               ║
╠══════════════════════════════════════════════════════════════╣
║  site:domain.com      → Limit results to specific domain     ║
║  inurl:keyword        → Keyword must appear in URL           ║
║  intitle:keyword      → Keyword must appear in page title    ║
║  intext:keyword       → Keyword must appear in page body     ║
║  filetype:pdf         → Filter by file type (pdf,doc,xls...) ║
║  ext:sql              → Filter by file extension             ║
║  cache:url            → Show Google's cached version         ║
║  link:url             → Pages that link to the URL           ║
║  related:url          → Pages related to the URL             ║
║  "exact phrase"       → Search exact phrase                  ║
║  -word                → Exclude word from results            ║
║  OR                   → Boolean OR operator                  ║
║  *                    → Wildcard                             ║
╠══════════════════════════════════════════════════════════════╣
║  EXAMPLES:                                                   ║
║  site:gov filetype:pdf "confidential"                        ║
║  inurl:"/wp-admin/" site:target.com                          ║
║  intitle:"index of" "parent directory"                       ║
║  filetype:env "DB_PASSWORD" "APP_KEY"                        ║
║  site:pastebin.com "api_key" "secret"                        ║
╚══════════════════════════════════════════════════════════════╝"""
        write_box(self.result_box, cheat)
