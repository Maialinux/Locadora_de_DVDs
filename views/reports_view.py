import customtkinter as ctk
from database.models import RentalModel
from components.table import Table
from utils.helpers import format_currency, format_date
from utils import theme


class ReportsFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(30, 20))
        theme.page_title(
            header, f"{theme.ICON['nav_reports']}  Relatórios"
        ).pack(side="left", anchor="w")

        theme.primary_button(
            header, f"{theme.ICON['refresh']}  Atualizar Relatórios",
            self.refresh_all, width=220
        ).pack(side="right", anchor="e")

        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        tab_most = self.tab_view.add("Filmes Mais Locados")
        tab_customers = self.tab_view.add("Top Clientes")
        tab_overdue = self.tab_view.add("Locações em Atraso")
        tab_active = self.tab_view.add("Locações Ativas")

        self.setup_most_rented(tab_most)
        self.setup_top_customers(tab_customers)
        self.setup_overdue(tab_overdue)
        self.setup_active(tab_active)

        self.refresh_all()

    def setup_most_rented(self, parent):
        columns = {"pos": "#", "title": "Filme", "count": "Qtd. Locações"}
        widths = {"pos": 50, "title": 500, "count": 150}
        table_frame = ctk.CTkFrame(parent, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.most_rented_table = Table(table_frame, columns, widths)
        self.most_rented_table.pack(fill="both", expand=True)

    def setup_top_customers(self, parent):
        columns = {"pos": "#", "name": "Cliente", "count": "Qtd. Locações"}
        widths = {"pos": 50, "name": 500, "count": 150}
        table_frame = ctk.CTkFrame(parent, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.top_customers_table = Table(table_frame, columns, widths)
        self.top_customers_table.pack(fill="both", expand=True)

    def setup_overdue(self, parent):
        columns = {
            "id": "ID",
            "movie": "Filme",
            "customer": "Cliente",
            "expected": "Devolver até",
            "days": "Dias Atraso",
            "fine": "Multa Estimada",
        }
        widths = {
            "id": 50, "movie": 250, "customer": 250,
            "expected": 120, "days": 100, "fine": 120,
        }
        table_frame = ctk.CTkFrame(parent, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.overdue_table = Table(table_frame, columns, widths)
        self.overdue_table.pack(fill="both", expand=True)

    def setup_active(self, parent):
        columns = {
            "id": "ID",
            "movie": "Filme",
            "customer": "Cliente",
            "rental": "Locação",
            "expected": "Devolver até",
            "days": "Dias Restantes",
        }
        widths = {
            "id": 50, "movie": 250, "customer": 250,
            "rental": 100, "expected": 120, "days": 100,
        }
        table_frame = ctk.CTkFrame(parent, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.active_table = Table(table_frame, columns, widths)
        self.active_table.pack(fill="both", expand=True)

    def refresh_all(self):
        from datetime import date

        # Most rented
        self.most_rented_table.clear()
        for i, m in enumerate(RentalModel.most_rented_movies(), 1):
            self.most_rented_table.insert((i, m["title"], m["rental_count"]))

        # Top customers
        self.top_customers_table.clear()
        for i, c in enumerate(RentalModel.top_customers(), 1):
            self.top_customers_table.insert((i, c["name"], c["rental_count"]))

        # Overdue
        self.overdue_table.clear()
        today = date.today()
        for r in RentalModel.overdue_rentals():
            expected_date = r["expected_return"]
            overdue_days = (today - date.fromisoformat(expected_date)).days
            fine_estimate = overdue_days * r["fine_per_day"]
            self.overdue_table.insert((
                r["id"],
                r["movie_title"],
                r["customer_name"],
                format_date(expected_date),
                overdue_days,
                format_currency(fine_estimate),
            ))

        # Active rentals
        self.active_table.clear()
        for r in RentalModel.active_rentals_data():
            expected_date = r["expected_return"]
            remaining = (date.fromisoformat(expected_date) - today).days
            remaining_str = f"{remaining} dias" if remaining >= 0 else f"{abs(remaining)} dias atraso"
            self.active_table.insert((
                r["id"],
                r["movie_title"],
                r["customer_name"],
                format_date(r["rental_date"]),
                format_date(expected_date),
                remaining_str,
            ))
