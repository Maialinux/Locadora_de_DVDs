import customtkinter as ctk
from utils import theme


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate):
        super().__init__(master, width=230, corner_radius=0, fg_color=theme.BG_SIDEBAR)
        self.pack_propagate(False)

        self.on_navigate = on_navigate
        self.nav_buttons = {}
        self.active_key = None

        # ---- Cabeçalho / marca ------------------------------------------
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(28, 30), padx=20)

        logo = ctk.CTkLabel(
            header,
            text=theme.ICON["logo"],
            width=58, height=58, corner_radius=16,
            fg_color=theme.ACCENT, text_color="#ffffff",
            font=theme.font(26, "bold"),
        )
        logo.pack()

        title = ctk.CTkLabel(
            header,
            text="Locadora DVD",
            font=theme.font(20, "bold"),
            text_color=theme.TEXT,
        )
        title.pack(pady=(6, 0))

        subtitle = ctk.CTkLabel(
            header,
            text="Sistema de Gestão",
            font=theme.font(11),
            text_color=theme.TEXT_MUTED,
        )
        subtitle.pack()

        # linha divisória sutil
        divider = ctk.CTkFrame(self, height=1, fg_color=theme.BG_SURFACE_2)
        divider.pack(fill="x", padx=20, pady=(0, 16))

        # ---- Navegação --------------------------------------------------
        nav_items = [
            ("dashboard", theme.ICON["nav_dashboard"], "Dashboard"),
            ("movies", theme.ICON["nav_movies"], "Filmes"),
            ("customers", theme.ICON["nav_customers"], "Clientes"),
            ("rentals", theme.ICON["nav_rentals"], "Locação"),
            ("reports", theme.ICON["nav_reports"], "Relatórios"),
        ]

        for key, icon, label in nav_items:
            btn = ctk.CTkButton(
                self,
                text=f"   {icon}   {label}",
                anchor="w",
                height=44,
                corner_radius=theme.RADIUS_SM,
                fg_color="transparent",
                text_color=theme.TEXT_MUTED,
                hover_color=theme.BG_SURFACE_2,
                font=theme.font(15),
                command=lambda k=key: self.on_navigate(k),
            )
            btn.pack(pady=4, padx=14, fill="x")
            self.nav_buttons[key] = btn

        version = ctk.CTkLabel(
            self,
            text="v1.0.0",
            font=theme.font(11),
            text_color=theme.TEXT_MUTED,
        )
        version.pack(side="bottom", pady=20)

    def set_active(self, key):
        """Destaca visualmente o item de navegação atual."""
        self.active_key = key
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(
                    fg_color=theme.ACCENT,
                    text_color="#ffffff",
                    hover_color=theme.ACCENT_HOVER,
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=theme.TEXT_MUTED,
                    hover_color=theme.BG_SURFACE_2,
                )
