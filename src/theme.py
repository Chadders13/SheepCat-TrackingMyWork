"""
SheepCat brand theme constants and ttk style configuration.

Colour tokens and typography match the SheepCat style guide so the desktop
application shares the same visual identity as the website.

Two built-in themes are available:
  "Classic"      – original dark slate/indigo palette
  "Glass Purple" – soft modern purple with rounded, soothing tones
"""
from tkinter import ttk

# ── Built-in theme palettes ───────────────────────────────────────────────────

THEMES = {
    "Classic": {
        "WINDOW_BG":  "#0f172a",
        "SURFACE_BG": "#1e1b4b",
        "INPUT_BG":   "#252250",
        "PRIMARY":    "#818cf8",
        "PRIMARY_D":  "#6366f1",
        "ACCENT":     "#fb923c",
        "GREEN":      "#4ade80",
        "RED":        "#f87171",
        "TEXT":       "#f1f5f9",
        "MUTED":      "#94a3b8",
        "BORDER":     "#2e2b5e",
    },
    "Glass Purple": {
        # Soft deep-purple background with a gentle, soothing feel
        "WINDOW_BG":  "#1a0e30",   # Rich midnight purple
        "SURFACE_BG": "#2d1a52",   # Frosted card surface
        "INPUT_BG":   "#3b2270",   # Slightly lighter input fields
        "PRIMARY":    "#c084fc",   # Soft lavender – buttons & accents
        "PRIMARY_D":  "#a855f7",   # Medium purple – hover / headings
        "ACCENT":     "#f0abfc",   # Pink-lilac – use sparingly
        "GREEN":      "#86efac",   # Mint green – success
        "RED":        "#fca5a5",   # Soft coral – danger
        "TEXT":       "#faf5ff",   # Warm near-white – body text
        "MUTED":      "#d8b4fe",   # Muted lavender – secondary text
        "BORDER":     "#5b21b6",   # Violet border
    },
}

THEME_NAMES = list(THEMES.keys())

# ── Active colour tokens (module-level – updated by apply_theme) ──────────────
WINDOW_BG   = THEMES["Classic"]["WINDOW_BG"]
SURFACE_BG  = THEMES["Classic"]["SURFACE_BG"]
INPUT_BG    = THEMES["Classic"]["INPUT_BG"]
PRIMARY     = THEMES["Classic"]["PRIMARY"]
PRIMARY_D   = THEMES["Classic"]["PRIMARY_D"]
ACCENT      = THEMES["Classic"]["ACCENT"]
GREEN       = THEMES["Classic"]["GREEN"]
RED         = THEMES["Classic"]["RED"]
TEXT        = THEMES["Classic"]["TEXT"]
MUTED       = THEMES["Classic"]["MUTED"]
BORDER      = THEMES["Classic"]["BORDER"]

# ── Typography ────────────────────────────────────────────────────────────────
_FONT = "Segoe UI"

FONT_BODY       = (_FONT, 10)
FONT_BODY_BOLD  = (_FONT, 10, "bold")
FONT_H1         = (_FONT, 18, "bold")
FONT_H2         = (_FONT, 14, "bold")
FONT_H3         = (_FONT, 12, "bold")
FONT_SMALL      = (_FONT, 9)
FONT_MONO       = ("Consolas", 10)


def apply_theme(name: str) -> None:
    """
    Switch the active colour tokens to the named theme.

    Must be called *before* any widgets are created (or before
    ``setup_ttk_styles`` is called) so that every widget picks up the
    correct colours when it is first built.

    Args:
        name: One of the keys in ``THEMES`` (e.g. "Classic", "Glass Purple").
              Falls back to "Classic" if the name is not recognised.
    """
    palette = THEMES.get(name, THEMES["Classic"])
    global WINDOW_BG, SURFACE_BG, INPUT_BG, PRIMARY, PRIMARY_D
    global ACCENT, GREEN, RED, TEXT, MUTED, BORDER
    WINDOW_BG  = palette["WINDOW_BG"]
    SURFACE_BG = palette["SURFACE_BG"]
    INPUT_BG   = palette["INPUT_BG"]
    PRIMARY    = palette["PRIMARY"]
    PRIMARY_D  = palette["PRIMARY_D"]
    ACCENT     = palette["ACCENT"]
    GREEN      = palette["GREEN"]
    RED        = palette["RED"]
    TEXT       = palette["TEXT"]
    MUTED      = palette["MUTED"]
    BORDER     = palette["BORDER"]


# ── ttk style setup ───────────────────────────────────────────────────────────

def setup_ttk_styles(root):
    """
    Configure ttk widget styles to match the SheepCat brand theme.

    Call once from the application root window before creating any pages.
    """
    style = ttk.Style(root)
    style.theme_use("clam")   # clam allows the most colour customisation

    # Frames & labels
    style.configure("TFrame", background=WINDOW_BG)
    style.configure("TLabel", background=WINDOW_BG, foreground=TEXT, font=FONT_BODY)

    # Scrollbar
    style.configure(
        "TScrollbar",
        background=SURFACE_BG,
        troughcolor=WINDOW_BG,
        arrowcolor=MUTED,
        bordercolor=WINDOW_BG,
        relief="flat",
    )
    style.map("TScrollbar", background=[("active", PRIMARY_D)])

    # Combobox
    style.configure(
        "TCombobox",
        fieldbackground=INPUT_BG,
        background=SURFACE_BG,
        foreground=TEXT,
        selectbackground=PRIMARY_D,
        selectforeground=TEXT,
        arrowcolor=TEXT,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", INPUT_BG)],
        foreground=[("readonly", TEXT)],
        selectbackground=[("readonly", PRIMARY_D)],
    )

    # Treeview
    style.configure(
        "Treeview",
        background=SURFACE_BG,
        foreground=TEXT,
        rowheight=26,
        fieldbackground=SURFACE_BG,
        font=FONT_BODY,
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=PRIMARY_D,
        foreground=TEXT,
        font=FONT_BODY_BOLD,
        relief="flat",
    )
    style.map(
        "Treeview",
        background=[("selected", PRIMARY_D)],
        foreground=[("selected", TEXT)],
    )
    style.map(
        "Treeview.Heading",
        background=[("active", PRIMARY)],
    )
