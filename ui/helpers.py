"""Shared UI helpers and color constants"""

# Color palette
BG        = "#0a0e1a"
BG2       = "#0f1629"
CARD      = "#141c2e"
SIDEBAR   = "#0c1220"
ACCENT    = "#00d4ff"
ACCENT_D  = "#0099bb"
GREEN     = "#00ff88"
ORANGE    = "#ff8c00"
RED       = "#ff4444"
TEXT      = "#e6edf3"
TEXT2     = "#8b949e"
BORDER    = "#1e2d4a"
BTN_FG    = "#0a0e1a"

FONT_TITLE  = ("Segoe UI", 20, "bold")
FONT_HEAD   = ("Segoe UI", 13, "bold")
FONT_BODY   = ("Segoe UI", 11)
FONT_MONO   = ("Consolas", 10)
FONT_SMALL  = ("Segoe UI", 9)


def make_result_box(parent, height=300):
    import customtkinter as ctk
    box = ctk.CTkTextbox(
        parent, height=height,
        font=FONT_MONO,
        fg_color=BG, text_color=ACCENT,
        border_color=BORDER, border_width=1,
        wrap="none",
    )
    return box


def make_entry(parent, placeholder="", width=300):
    import customtkinter as ctk
    return ctk.CTkEntry(
        parent, placeholder_text=placeholder, width=width,
        fg_color=BG2, border_color=BORDER,
        text_color=TEXT, placeholder_text_color=TEXT2,
        font=FONT_BODY,
    )


def make_button(parent, text, command, color=ACCENT, width=120):
    import customtkinter as ctk
    return ctk.CTkButton(
        parent, text=text, command=command,
        fg_color=color, hover_color=ACCENT_D if color == ACCENT else color,
        text_color=BTN_FG if color == ACCENT else TEXT,
        font=("Segoe UI", 11, "bold"), width=width, height=34,
        corner_radius=8,
    )


def make_label(parent, text, font=None, color=TEXT2):
    import customtkinter as ctk
    return ctk.CTkLabel(parent, text=text, font=font or FONT_BODY, text_color=color)


def clear_box(box):
    box.configure(state="normal")
    box.delete("1.0", "end")
    box.configure(state="normal")


def append_box(box, text):
    box.configure(state="normal")
    box.insert("end", text)
    box.see("end")


def write_box(box, text):
    clear_box(box)
    append_box(box, text)
