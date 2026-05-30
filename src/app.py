import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from predict import predict_diabetes
from recommendation import give_recommendation, heart_recommendation
from predict_heart import predict_heart

# ── Theme ──────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Palette ────────────────────────────────────────────────────────────
BG_MAIN      = "#0A0F1E"   # near-black navy
BG_SIDEBAR   = "#0D1526"   # slightly lighter navy
BG_CARD      = "#111827"   # card background
BG_ENTRY     = "#1A2336"   # input background
ACCENT       = "#00C2FF"   # electric cyan
ACCENT_HOVER = "#00A8DC"
TEXT_MAIN    = "#E8F0FE"
TEXT_MUTED   = "#6B7A99"
BORDER       = "#1E2D45"
SUCCESS      = "#00E676"
WARNING      = "#FFB300"
DANGER       = "#FF3D5A"

FONT_TITLE  = ("Courier New", 24, "bold")
FONT_HEAD   = ("Courier New", 13, "bold")
FONT_BODY   = ("Consolas", 11)
FONT_SMALL  = ("Consolas", 10)
FONT_MONO   = ("Courier New", 11)

# ── App Window ─────────────────────────────────────────────────────────
app = ctk.CTk()
app.geometry("1000x680")
app.title("AI Health System")
app.configure(fg_color=BG_MAIN)
app.resizable(False, False)

# ── Sidebar ────────────────────────────────────────────────────────────
sidebar = ctk.CTkFrame(app, width=200, fg_color=BG_SIDEBAR, corner_radius=0)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

# Logo area
logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
logo_frame.pack(pady=(30, 10), padx=20, fill="x")

ctk.CTkLabel(
    logo_frame, text="◈",
    font=("Courier New", 28, "bold"),
    text_color=ACCENT
).pack()

ctk.CTkLabel(
    logo_frame, text="HEALTH AI",
    font=("Courier New", 14, "bold"),
    text_color=TEXT_MAIN
).pack()

ctk.CTkLabel(
    logo_frame, text="DIAGNOSTIC SYSTEM",
    font=("Consolas", 8),
    text_color=TEXT_MUTED
).pack()

# Divider
ctk.CTkFrame(sidebar, height=1, fg_color=BORDER).pack(fill="x", padx=20, pady=20)

ctk.CTkLabel(
    sidebar, text="MODULES",
    font=("Consolas", 9),
    text_color=TEXT_MUTED
).pack(anchor="w", padx=24, pady=(0, 8))

# ── Main Frame ─────────────────────────────────────────────────────────
main_frame = ctk.CTkFrame(app, fg_color=BG_MAIN, corner_radius=0)
main_frame.pack(side="right", fill="both", expand=True)

active_btn = {"ref": None}

def set_active(btn):
    if active_btn["ref"] and active_btn["ref"] != btn:
        active_btn["ref"].configure(fg_color="transparent", text_color=TEXT_MUTED)
    btn.configure(fg_color="#152035", text_color=ACCENT)
    active_btn["ref"] = btn

def show_frame(frame_fn, btn):
    set_active(btn)
    for w in main_frame.winfo_children():
        w.destroy()
    frame_fn()

# ── Helper: Scrollable content area ───────────────────────────────────
def make_scroll_area():
    canvas = tk.Canvas(main_frame, bg=BG_MAIN, highlightthickness=0, bd=0)
    scrollbar = ctk.CTkScrollbar(main_frame, command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    inner = ctk.CTkFrame(canvas, fg_color=BG_MAIN)
    window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    def on_configure(e):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(window_id, width=canvas.winfo_width())

    inner.bind("<Configure>", on_configure)
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(window_id, width=e.width))

    def _on_mousewheel(e):
        canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    return inner

# ── Helper: Section card ───────────────────────────────────────────────
def make_card(parent, padx=40, pady=16):
    card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=12,
                        border_width=1, border_color=BORDER)
    card.pack(fill="x", padx=padx, pady=pady)
    return card

# ── Helper: Styled entry ───────────────────────────────────────────────
def make_entry(parent, label_text, placeholder, row):
    lbl = ctk.CTkLabel(parent, text=label_text,
                       font=FONT_SMALL, text_color=TEXT_MUTED, anchor="w")
    lbl.grid(row=row * 2, column=0, columnspan=2, sticky="w", padx=20, pady=(12, 2))

    entry = ctk.CTkEntry(
        parent, placeholder_text=placeholder,
        height=40, corner_radius=8,
        fg_color=BG_ENTRY, border_color=BORDER,
        border_width=1, text_color=TEXT_MAIN,
        placeholder_text_color=TEXT_MUTED,
        font=FONT_MONO
    )
    entry.grid(row=row * 2 + 1, column=0, columnspan=2,
               sticky="ew", padx=20, pady=(0, 4))
    return entry

# ── Helper: Risk badge (canvas-drawn) ─────────────────────────────────
def draw_risk_badge(parent, text, color, pct):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(pady=10)

    c = tk.Canvas(frame, width=280, height=80,
                  bg=BG_CARD, highlightthickness=0)
    c.pack()

    # background bar
    c.create_rectangle(20, 55, 260, 70, fill="#1A2336", outline="")
    fill_w = int(20 + (pct / 100) * 240)
    c.create_rectangle(20, 55, fill_w, 70, fill=color, outline="")

    c.create_text(140, 28, text=text,
                  fill=color, font=("Courier New", 18, "bold"))
    c.create_text(140, 47, text=f"{pct:.1f}% probability",
                  fill=TEXT_MUTED, font=("Consolas", 10))

# ── Diabetes Page ─────────────────────────────────────────────────────
def diabetes_page():
    scroll = make_scroll_area()

    # Header
    hdr = ctk.CTkFrame(scroll, fg_color="transparent")
    hdr.pack(fill="x", padx=40, pady=(30, 4))
    ctk.CTkLabel(hdr, text="DIABETES", font=("Courier New", 28, "bold"),
                 text_color=ACCENT).pack(anchor="w")
    ctk.CTkLabel(hdr, text="RISK ASSESSMENT MODULE",
                 font=("Consolas", 11), text_color=TEXT_MUTED).pack(anchor="w")

    ctk.CTkFrame(scroll, height=1, fg_color=BORDER).pack(fill="x", padx=40, pady=(8, 20))

    # Input card
    card = make_card(scroll)
    ctk.CTkLabel(card, text="PATIENT PARAMETERS",
                 font=FONT_HEAD, text_color=TEXT_MUTED).grid(
        row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(16, 4))
    card.columnconfigure(0, weight=1)
    card.columnconfigure(1, weight=1)

    fields = [
        ("PREGNANCIES",          "Number of pregnancies",     "Preg"),
        ("GLUCOSE (mg/dL)",      "Plasma glucose level",      "Glucose"),
        ("BLOOD PRESSURE (mmHg)","Diastolic BP",              "BP"),
        ("SKIN THICKNESS (mm)",  "Triceps skin fold",         "Skin"),
        ("INSULIN (μU/mL)",      "2-hour serum insulin",      "Insulin"),
        ("BMI (kg/m²)",          "Body mass index",           "BMI"),
        ("DIABETES PED. FUNC.",  "Diabetes pedigree function","DPF"),
        ("AGE (years)",          "Patient age",               "Age"),
    ]

    entries = []
    for i, (label, ph, _) in enumerate(fields):
        col = i % 2
        row_in_card = (i // 2) * 2 + 1

        lbl = ctk.CTkLabel(card, text=label, font=FONT_SMALL, text_color=TEXT_MUTED, anchor="w")
        lbl.grid(row=row_in_card, column=col, sticky="w", padx=20, pady=(12, 2))

        entry = ctk.CTkEntry(
            card, placeholder_text=ph,
            height=40, corner_radius=8,
            fg_color=BG_ENTRY, border_color=BORDER,
            border_width=1, text_color=TEXT_MAIN,
            placeholder_text_color=TEXT_MUTED,
            font=FONT_MONO
        )
        entry.grid(row=row_in_card + 1, column=col,
                   sticky="ew", padx=20, pady=(0, 4))
        entries.append(entry)

    # Result area
    result_card = make_card(scroll)
    result_inner = ctk.CTkFrame(result_card, fg_color="transparent")
    result_inner.pack(fill="x", padx=10, pady=10)

    result_placeholder = ctk.CTkLabel(
        result_inner, text="— Run prediction to see results —",
        font=FONT_BODY, text_color=TEXT_MUTED
    )
    result_placeholder.pack(pady=20)

    rec_card = make_card(scroll)
    rec_inner = ctk.CTkFrame(rec_card, fg_color="transparent")
    rec_inner.pack(fill="x", padx=10, pady=10)

    def check():
        try:
            values = [float(e.get()) for e in entries]
        except Exception:
            messagebox.showerror("Input Error", "Please enter valid numeric values in all fields.")
            return

        _, prob = predict_diabetes(values)
        recs = give_recommendation(values[1], values[5])
        risk = prob * 100

        if prob > 0.7:
            color, text = DANGER, "HIGH RISK"
        elif prob > 0.4:
            color, text = WARNING, "MODERATE RISK"
        else:
            color, text = SUCCESS, "LOW RISK"

        # Clear and redraw result card
        for w in result_inner.winfo_children():
            w.destroy()

        draw_risk_badge(result_inner, text, color, risk)

        # Clear and redraw rec card
        for w in rec_inner.winfo_children():
            w.destroy()

        ctk.CTkLabel(rec_inner, text="RECOMMENDATIONS",
                     font=FONT_HEAD, text_color=TEXT_MUTED).pack(anchor="w", padx=10, pady=(10, 6))
        for rec in recs:
            row = ctk.CTkFrame(rec_inner, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=3)
            ctk.CTkLabel(row, text="▸", font=FONT_BODY, text_color=ACCENT, width=18).pack(side="left")
            ctk.CTkLabel(row, text=rec, font=FONT_BODY, text_color=TEXT_MAIN,
                         wraplength=560, justify="left").pack(side="left")

    ctk.CTkButton(
        scroll, text="RUN ANALYSIS  →",
        command=check, height=48, corner_radius=10,
        fg_color=ACCENT, hover_color=ACCENT_HOVER,
        text_color="#000000", font=("Courier New", 13, "bold")
    ).pack(padx=40, pady=(10, 30), fill="x")

# ── Heart Page ─────────────────────────────────────────────────────────
def heart_page():
    scroll = make_scroll_area()

    hdr = ctk.CTkFrame(scroll, fg_color="transparent")
    hdr.pack(fill="x", padx=40, pady=(30, 4))
    ctk.CTkLabel(hdr, text="CARDIAC", font=("Courier New", 28, "bold"),
                 text_color="#FF3D5A").pack(anchor="w")
    ctk.CTkLabel(hdr, text="HEART DISEASE ASSESSMENT MODULE",
                 font=("Consolas", 11), text_color=TEXT_MUTED).pack(anchor="w")

    ctk.CTkFrame(scroll, height=1, fg_color=BORDER).pack(fill="x", padx=40, pady=(8, 20))

    card = make_card(scroll)
    ctk.CTkLabel(card, text="PATIENT PARAMETERS",
                 font=FONT_HEAD, text_color=TEXT_MUTED).grid(
        row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(16, 4))
    card.columnconfigure(0, weight=1)
    card.columnconfigure(1, weight=1)

    fields = [
        ("AGE (years)",           "Patient age"),
        ("SEX",                   "1 = Male, 0 = Female"),
        ("CHEST PAIN TYPE",       "0–3 scale"),
        ("RESTING BP (mmHg)",     "Resting blood pressure"),
        ("CHOLESTEROL (mg/dL)",   "Serum cholesterol"),
        ("FASTING BLOOD SUGAR",   "1 = >120 mg/dL, 0 = else"),
        ("RESTING ECG",           "0, 1 or 2"),
        ("MAX HEART RATE",        "Maximum heart rate achieved"),
        ("EXERCISE ANGINA",       "1 = Yes, 0 = No"),
        ("OLDPEAK",               "ST depression"),
        ("SLOPE",                 "Slope of peak ST segment"),
        ("CA",                    "Number of major vessels (0–3)"),
        ("THAL",                  "3 = Normal, 6 = Fixed, 7 = Reversable"),
    ]

    entries = []
    for i, (label, ph) in enumerate(fields):
        col = i % 2
        row_in_card = (i // 2) * 2 + 1

        lbl = ctk.CTkLabel(card, text=label, font=FONT_SMALL, text_color=TEXT_MUTED, anchor="w")
        lbl.grid(row=row_in_card, column=col, sticky="w", padx=20, pady=(12, 2))

        entry = ctk.CTkEntry(
            card, placeholder_text=ph,
            height=40, corner_radius=8,
            fg_color=BG_ENTRY, border_color=BORDER,
            border_width=1, text_color=TEXT_MAIN,
            placeholder_text_color=TEXT_MUTED,
            font=FONT_MONO
        )
        entry.grid(row=row_in_card + 1, column=col,
                   sticky="ew", padx=20, pady=(0, 4))
        entries.append(entry)

    result_card = make_card(scroll)
    result_inner = ctk.CTkFrame(result_card, fg_color="transparent")
    result_inner.pack(fill="x", padx=10, pady=10)

    result_placeholder = ctk.CTkLabel(
        result_inner, text="— Run prediction to see results —",
        font=FONT_BODY, text_color=TEXT_MUTED
    )
    result_placeholder.pack(pady=20)

    rec_card = make_card(scroll)
    rec_inner = ctk.CTkFrame(rec_card, fg_color="transparent")
    rec_inner.pack(fill="x", padx=10, pady=10)

    def check():
        try:
            values = [float(e.get()) for e in entries]
        except Exception:
            messagebox.showerror("Input Error", "Please enter valid numeric values in all fields.")
            return

        _, prob = predict_heart(values)
        risk = prob * 100

        if prob > 0.7:
            color, text = DANGER, "HIGH RISK"
        elif prob > 0.4:
            color, text = WARNING, "MODERATE RISK"
        else:
            color, text = SUCCESS, "LOW RISK"

        for w in result_inner.winfo_children():
            w.destroy()
        draw_risk_badge(result_inner, text, color, risk)

        recs = heart_recommendation(values[4], values[3], values[7])
        for w in rec_inner.winfo_children():
            w.destroy()

        ctk.CTkLabel(rec_inner, text="RECOMMENDATIONS",
                     font=FONT_HEAD, text_color=TEXT_MUTED).pack(anchor="w", padx=10, pady=(10, 6))
        for rec in recs:
            row = ctk.CTkFrame(rec_inner, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=3)
            ctk.CTkLabel(row, text="▸", font=FONT_BODY, text_color="#FF3D5A", width=18).pack(side="left")
            ctk.CTkLabel(row, text=rec, font=FONT_BODY, text_color=TEXT_MAIN,
                         wraplength=560, justify="left").pack(side="left")

    ctk.CTkButton(
        scroll, text="RUN ANALYSIS  →",
        command=check, height=48, corner_radius=10,
        fg_color="#FF3D5A", hover_color="#CC2040",
        text_color="#FFFFFF", font=("Courier New", 13, "bold")
    ).pack(padx=40, pady=(10, 30), fill="x")

# ── Sidebar Buttons ────────────────────────────────────────────────────
def make_nav_btn(label, icon, command):
    btn = ctk.CTkButton(
        sidebar, text=f"  {icon}  {label}",
        anchor="w", height=44,
        fg_color="transparent", hover_color="#152035",
        text_color=TEXT_MUTED,
        font=("Consolas", 12),
        corner_radius=8,
        command=command
    )
    btn.pack(fill="x", padx=12, pady=3)
    return btn

db_btn = make_nav_btn("DIABETES", "◈", lambda: show_frame(diabetes_page, db_btn))
ht_btn = make_nav_btn("CARDIAC",  "♥", lambda: show_frame(heart_page,    ht_btn))

# Bottom status bar
ctk.CTkFrame(sidebar, height=1, fg_color=BORDER).pack(fill="x", padx=20, pady=(0, 10), side="bottom")
ctk.CTkLabel(sidebar, text="v1.0  |  AI Powered",
             font=("Consolas", 8), text_color=TEXT_MUTED).pack(side="bottom", pady=(0, 8))

# Default view
show_frame(diabetes_page, db_btn)

app.mainloop()