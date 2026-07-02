"""Design system central da aplicação.

Paleta, fontes e helpers de estilo reutilizáveis para dar um visual
consistente e moderno a toda a interface.
"""

import customtkinter as ctk

# ---------------------------------------------------------------------------
# Paleta de cores (formato (light, dark) aceito pelo CustomTkinter)
# ---------------------------------------------------------------------------

# Cor de destaque principal — índigo/violeta moderno
ACCENT = "#7c5cff"
ACCENT_HOVER = "#6a4bf0"
ACCENT_LIGHT = "#9b83ff"

# Superfícies
BG_APP = ("#f2f3f7", "#15161c")          # fundo geral da janela
BG_SURFACE = ("#ffffff", "#1e1f27")      # cartões / painéis
BG_SURFACE_2 = ("#e9ebf2", "#262832")    # painéis secundários / linhas alt.
BG_SIDEBAR = ("#ffffff", "#191a21")

# Texto
TEXT = ("#1b1c22", "#f4f5fb")
TEXT_MUTED = ("#6b6f80", "#9aa0b3")

# Estados semânticos
SUCCESS = "#22c55e"
SUCCESS_HOVER = "#16a34a"
DANGER = "#ef4444"
DANGER_HOVER = "#dc2626"
WARNING = "#f59e0b"
INFO = "#3b82f6"

# Cores de acento dos cartões do dashboard
CARD_COLORS = {
    "movies": "#7c5cff",
    "customers": "#3b82f6",
    "active": "#22c55e",
    "overdue": "#ef4444",
    "revenue": "#f59e0b",
}

# ---------------------------------------------------------------------------
# Ícones (símbolos Unicode que renderizam de forma confiável no Tk/Linux —
# emojis coloridos viram quadrados vazios, então usamos glifos geométricos)
# ---------------------------------------------------------------------------

ICON = {
    "refresh": "⟳",
    "add": "✚",
    "edit": "✎",
    "delete": "✕",
    "search": "⌕",
    "check": "✓",
    "save": "✓",
    "warning": "⚠",
    "logo": "⯈",
    # navegação
    "nav_dashboard": "▦",
    "nav_movies": "⯈",
    "nav_customers": "◉",
    "nav_rentals": "⟳",
    "nav_reports": "▤",
    # cartões do dashboard
    "card_movies": "⯈",
    "card_customers": "◉",
    "card_active": "⟳",
    "card_overdue": "⚠",
    "card_revenue": "◆",
}


# ---------------------------------------------------------------------------
# Fontes
# ---------------------------------------------------------------------------

# DejaVu Sans está sempre disponível no Linux e cobre os glifos de ícone acima.
FONT_FAMILY = "DejaVu Sans"


def font(size=14, weight="normal"):
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


def font_title():
    return ctk.CTkFont(family=FONT_FAMILY, size=28, weight="bold")


def font_heading():
    return ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold")


# ---------------------------------------------------------------------------
# Radii / espaçamentos
# ---------------------------------------------------------------------------

RADIUS = 14
RADIUS_SM = 10


def apply_global_theme():
    """Aplica configurações globais do CustomTkinter."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


# ---------------------------------------------------------------------------
# Fábricas de widgets estilizados
# ---------------------------------------------------------------------------

def primary_button(master, text, command, **kwargs):
    kwargs.setdefault("height", 40)
    kwargs.setdefault("corner_radius", RADIUS_SM)
    return ctk.CTkButton(
        master, text=text, command=command,
        fg_color=ACCENT, hover_color=ACCENT_HOVER,
        font=font(14, "bold"), **kwargs,
    )


def danger_button(master, text, command, **kwargs):
    kwargs.setdefault("height", 40)
    kwargs.setdefault("corner_radius", RADIUS_SM)
    return ctk.CTkButton(
        master, text=text, command=command,
        fg_color=DANGER, hover_color=DANGER_HOVER,
        font=font(14, "bold"), **kwargs,
    )


def success_button(master, text, command, **kwargs):
    kwargs.setdefault("height", 44)
    kwargs.setdefault("corner_radius", RADIUS_SM)
    return ctk.CTkButton(
        master, text=text, command=command,
        fg_color=SUCCESS, hover_color=SUCCESS_HOVER,
        font=font(15, "bold"), **kwargs,
    )


def ghost_button(master, text, command, **kwargs):
    kwargs.setdefault("height", 40)
    kwargs.setdefault("corner_radius", RADIUS_SM)
    return ctk.CTkButton(
        master, text=text, command=command,
        fg_color=BG_SURFACE_2, hover_color=("#d5d8e2", "#333644"),
        text_color=TEXT, font=font(14, "bold"), **kwargs,
    )


def page_title(master, text):
    return ctk.CTkLabel(master, text=text, font=font_title(), text_color=TEXT)


def search_entry(master, placeholder="Buscar...", **kwargs):
    kwargs.setdefault("width", 320)
    kwargs.setdefault("height", 38)
    kwargs.setdefault("corner_radius", RADIUS_SM)
    return ctk.CTkEntry(
        master, placeholder_text=placeholder,
        border_width=0, fg_color=BG_SURFACE, **kwargs,
    )
