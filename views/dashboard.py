import customtkinter as ctk
from database.models import MovieModel, CustomerModel, RentalModel
from utils.helpers import format_currency
from utils import theme


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app

        # ---- Cabeçalho --------------------------------------------------
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(30, 24))

        title = ctk.CTkLabel(
            header, text="Dashboard", font=theme.font_title(), text_color=theme.TEXT
        )
        title.pack(side="left", anchor="w")

        theme.primary_button(
            header, f"{theme.ICON['refresh']}  Atualizar", self.refresh, width=150
        ).pack(side="right", anchor="e")

        subtitle = ctk.CTkLabel(
            self, text="Visão geral da sua locadora",
            font=theme.font(14), text_color=theme.TEXT_MUTED,
        )
        subtitle.pack(padx=40, anchor="w", pady=(0, 20))

        # ---- Cartões ----------------------------------------------------
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(padx=40, fill="x")

        self.card_movies = self._create_card(
            cards_frame, theme.ICON["card_movies"], "Total de Filmes", "0",
            theme.CARD_COLORS["movies"], 0, 0
        )
        self.card_customers = self._create_card(
            cards_frame, theme.ICON["card_customers"], "Total de Clientes", "0",
            theme.CARD_COLORS["customers"], 0, 1
        )
        self.card_active = self._create_card(
            cards_frame, theme.ICON["card_active"], "Locações Ativas", "0",
            theme.CARD_COLORS["active"], 0, 2
        )
        self.card_overdue = self._create_card(
            cards_frame, theme.ICON["card_overdue"], "Em Atraso", "0",
            theme.CARD_COLORS["overdue"], 1, 0
        )
        self.card_revenue = self._create_card(
            cards_frame, theme.ICON["card_revenue"], "Receita do Mês", "R$ 0,00",
            theme.CARD_COLORS["revenue"], 1, 1, colspan=2,
        )

        for c in range(3):
            cards_frame.grid_columnconfigure(c, weight=1, uniform="cards")

        self.refresh()

    def _create_card(self, parent, icon, title, value, accent, row, col, colspan=1):
        frame = ctk.CTkFrame(
            parent, corner_radius=theme.RADIUS, height=140, fg_color=theme.BG_SURFACE
        )
        frame.grid_propagate(False)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew",
                   columnspan=colspan)

        # barra de acento colorida à esquerda
        accent_bar = ctk.CTkFrame(frame, width=5, corner_radius=3, fg_color=accent)
        accent_bar.place(relx=0, rely=0.5, anchor="w", relheight=0.62, x=14)

        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.place(relx=0, rely=0.5, anchor="w", x=34)

        top = ctk.CTkFrame(content, fg_color="transparent")
        top.pack(anchor="w")
        ctk.CTkLabel(
            top, text=icon, font=theme.font(20, "bold"), text_color=accent
        ).pack(side="left")
        ctk.CTkLabel(
            top, text=f"   {title}", font=theme.font(14),
            text_color=theme.TEXT_MUTED,
        ).pack(side="left")

        label = ctk.CTkLabel(
            content, text=value, font=theme.font(32, "bold"), text_color=accent
        )
        label.pack(anchor="w", pady=(8, 0))

        return label

    def refresh(self):
        movies = MovieModel.all()
        customers = CustomerModel.all()
        active = RentalModel.count_active()
        overdue = RentalModel.count_overdue()
        revenue = RentalModel.revenue_month()

        self.card_movies.configure(text=str(len(movies)))
        self.card_customers.configure(text=str(len(customers)))
        self.card_active.configure(text=str(active))
        self.card_overdue.configure(text=str(overdue))
        self.card_revenue.configure(text=format_currency(revenue))
