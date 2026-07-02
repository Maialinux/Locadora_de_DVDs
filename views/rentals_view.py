import customtkinter as ctk
from tkinter import messagebox
from datetime import date, timedelta
from database.models import MovieModel, CustomerModel, RentalModel
from components.table import Table
from utils.helpers import format_currency, format_date
from utils import theme


class RentalsFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app

        theme.page_title(
            self, f"{theme.ICON['nav_rentals']}  Locação"
        ).pack(padx=40, pady=(30, 10), anchor="w")

        self.tab_view = ctk.CTkTabview(
            self, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS,
            segmented_button_selected_color=theme.ACCENT,
            segmented_button_selected_hover_color=theme.ACCENT_HOVER,
        )
        self.tab_view.pack(fill="both", expand=True, padx=40, pady=(10, 30))

        self.tab_rent = self.tab_view.add("Locar Filme")
        self.tab_return = self.tab_view.add("Devolver")
        self.tab_history = self.tab_view.add("Histórico")

        self.setup_rent_tab()
        self.setup_return_tab()
        self.setup_history_tab()

    def setup_rent_tab(self):
        tab = self.tab_rent

        header = ctk.CTkLabel(
            tab, text="Nova Locação", font=ctk.CTkFont(size=22, weight="bold")
        )
        header.pack(pady=(20, 20), anchor="w")

        form = ctk.CTkFrame(tab, fg_color=theme.BG_SURFACE_2, corner_radius=theme.RADIUS)
        form.pack(padx=20, fill="x", pady=(0, 10))

        ctk.CTkLabel(form, text="Filme *").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.movie_combo = ctk.CTkComboBox(form, values=[], width=350, state="readonly")
        self.movie_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(form, text="Cliente *").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.customer_combo = ctk.CTkComboBox(form, values=[], width=350, state="readonly")
        self.customer_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(form, text="Dias *").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.days_entry = ctk.CTkEntry(form, width=100)
        self.days_entry.insert(0, "3")
        self.days_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.info_label = ctk.CTkLabel(
            form, text="", font=ctk.CTkFont(size=13),
            text_color=("gray30", "gray70"),
        )
        self.info_label.grid(row=3, column=0, columnspan=2, padx=5, pady=10, sticky="w")

        self.movie_combo.bind("<<ComboboxSelected>>", self.update_info)
        self.days_entry.bind("<KeyRelease>", self.update_info)

        theme.success_button(
            tab, f"{theme.ICON['check']}  Confirmar Locação", self.confirm_rental, width=250
        ).pack(pady=20)

        form.grid_columnconfigure(1, weight=1)

        self.refresh_combos()

    def setup_return_tab(self):
        tab = self.tab_return

        header = ctk.CTkLabel(
            tab, text="Devolução de Filme", font=ctk.CTkFont(size=22, weight="bold")
        )
        header.pack(pady=(20, 20), anchor="w")

        search_frame = ctk.CTkFrame(tab, fg_color="transparent")
        search_frame.pack(padx=20, fill="x", pady=(0, 10))

        ctk.CTkLabel(
            search_frame, text=theme.ICON["search"], font=theme.font(16),
            text_color=theme.TEXT_MUTED,
        ).pack(side="left", padx=(0, 8))
        self.return_search_entry = ctk.CTkEntry(search_frame, width=300)
        self.return_search_entry.pack(side="left", padx=(0, 10))
        self.return_search_entry.bind("<KeyRelease>", lambda e: self.refresh_return_table())

        columns = {
            "id": "ID",
            "movie": "Filme",
            "customer": "Cliente",
            "rental_date": "Data Locação",
            "expected": "Devolver até",
        }
        widths = {"id": 50, "movie": 250, "customer": 250, "rental_date": 120, "expected": 120}

        table_frame = ctk.CTkFrame(tab, fg_color="transparent")
        table_frame.pack(padx=20, fill="both", expand=True)

        self.return_table = Table(table_frame, columns, widths)
        self.return_table.pack(fill="both", expand=True)

        details_frame = ctk.CTkFrame(tab, fg_color=theme.BG_SURFACE_2, corner_radius=theme.RADIUS)
        details_frame.pack(padx=20, pady=15, fill="x")

        self.return_info = ctk.CTkLabel(details_frame, text="", justify="left")
        self.return_info.pack()

        theme.success_button(
            tab, f"{theme.ICON['check']}  Confirmar Devolução", self.confirm_return, width=250
        ).pack(pady=(0, 20))

        self.refresh_return_table()

    def setup_history_tab(self):
        tab = self.tab_history

        header = ctk.CTkLabel(
            tab, text="Histórico de Locações", font=ctk.CTkFont(size=22, weight="bold")
        )
        header.pack(pady=(20, 20), anchor="w")

        search_frame = ctk.CTkFrame(tab, fg_color="transparent")
        search_frame.pack(padx=20, fill="x", pady=(0, 10))

        ctk.CTkLabel(
            search_frame, text=theme.ICON["search"], font=theme.font(16),
            text_color=theme.TEXT_MUTED,
        ).pack(side="left", padx=(0, 8))
        self.history_search_entry = ctk.CTkEntry(search_frame, width=300)
        self.history_search_entry.pack(side="left", padx=(0, 10))
        self.history_search_entry.bind("<KeyRelease>", lambda e: self.refresh_history())

        columns = {
            "id": "ID",
            "movie": "Filme",
            "customer": "Cliente",
            "rental_date": "Locação",
            "return_date": "Devolução",
            "amount": "Valor",
            "status": "Status",
        }
        widths = {
            "id": 50, "movie": 200, "customer": 200,
            "rental_date": 100, "return_date": 100, "amount": 100, "status": 100,
        }

        table_frame = ctk.CTkFrame(tab, fg_color="transparent")
        table_frame.pack(padx=20, fill="both", expand=True)

        self.history_table = Table(table_frame, columns, widths)
        self.history_table.pack(fill="both", expand=True)

        self.refresh_history()

    def refresh_combos(self):
        movies = MovieModel.all()
        self.movie_map = {}
        movie_names = []
        for m in movies:
            if m["available"] > 0:
                label = f"{m['title']} ({m['available']} disp.)"
                self.movie_map[label] = m
                movie_names.append(label)
        if movie_names:
            self.movie_combo.configure(values=movie_names)
            self.movie_combo.set(movie_names[0])
        else:
            self.movie_combo.configure(values=["Nenhum filme disponível"])
            self.movie_combo.set("Nenhum filme disponível")

        customers = CustomerModel.all()
        self.customer_map = {}
        customer_names = []
        for c in customers:
            label = f"{c['name']} - {c['cpf']}"
            self.customer_map[label] = c
            customer_names.append(label)
        if customer_names:
            self.customer_combo.configure(values=customer_names)
            self.customer_combo.set(customer_names[0])
        else:
            self.customer_combo.configure(values=["Nenhum cliente cadastrado"])
            self.customer_combo.set("Nenhum cliente cadastrado")

        self.update_info()

    def update_info(self, event=None):
        movie_label = self.movie_combo.get()
        movie = self.movie_map.get(movie_label)
        if not movie:
            self.info_label.configure(text="")
            return

        days_str = self.days_entry.get().strip()
        try:
            days = int(days_str)
            if days < 1:
                days = 1
        except ValueError:
            days = 0

        daily_rate = movie["daily_rate"]
        total = daily_rate * days
        today = date.today()
        expected = today + timedelta(days=days)

        self.info_label.configure(
            text=(
                f"Filme: {movie['title']}  |  "
                f"Diária: {format_currency(daily_rate)}  |  "
                f"Dias: {days}  |  "
                f"Total: {format_currency(total)}  |  "
                f"Devolução: {expected.strftime('%d/%m/%Y')}"
            )
        )

    def confirm_rental(self):
        movie_label = self.movie_combo.get()
        customer_label = self.customer_combo.get()

        movie = self.movie_map.get(movie_label)
        customer = self.customer_map.get(customer_label)

        if not movie or not customer:
            messagebox.showerror("Erro", "Selecione um filme e um cliente válidos.")
            return

        try:
            days = int(self.days_entry.get().strip())
            if days < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Dias deve ser um número inteiro positivo.")
            return

        today = date.today()
        expected = today + timedelta(days=days)
        total = movie["daily_rate"] * days

        if not messagebox.askyesno(
            "Confirmar Locação",
            f"Filme: {movie['title']}\n"
            f"Cliente: {customer['name']}\n"
            f"Data: {today.strftime('%d/%m/%Y')}\n"
            f"Devolução: {expected.strftime('%d/%m/%Y')}\n"
            f"Total: {format_currency(total)}",
        ):
            return

        RentalModel.create({
            "movie_id": movie["id"],
            "customer_id": customer["id"],
            "rental_date": today.isoformat(),
            "expected_return": expected.isoformat(),
            "daily_rate": movie["daily_rate"],
            "fine_per_day": movie["fine_per_day"],
        })

        messagebox.showinfo("Sucesso", "Locação registrada com sucesso!")
        self.refresh_combos()
        self.refresh_return_table()
        self.refresh_history()

    def refresh_return_table(self):
        self.return_table.clear()
        search = self.return_search_entry.get().strip()
        rentals = RentalModel.all_active(search)
        for r in rentals:
            self.return_table.insert((
                r["id"],
                r["movie_title"],
                r["customer_name"],
                format_date(r["rental_date"]),
                format_date(r["expected_return"]),
            ))

    def confirm_return(self):
        selected = self.return_table.get_selected()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma locação ativa.")
            return

        rental_id = int(selected["values"][0])
        rental = RentalModel.get_by_id(rental_id)
        if not rental:
            return

        today = date.today()
        expected = rental["expected_return"]
        overdue_days = (today - date.fromisoformat(expected)).days if expected < today.isoformat() else 0
        fine_amount = overdue_days * rental["fine_per_day"]
        days_rented = max(1, (today - date.fromisoformat(rental["rental_date"])).days)
        base_amount = rental["daily_rate"] * days_rented
        total = base_amount + fine_amount

        details = (
            f"Filme: {rental['movie_title']}\n"
            f"Cliente: {rental['customer_name']}\n"
            f"Data locação: {format_date(rental['rental_date'])}\n"
            f"Previsão devolução: {format_date(rental['expected_return'])}\n"
            f"Data devolução: {today.strftime('%d/%m/%Y')}\n"
        )
        if overdue_days > 0:
            details += (
                f"\n⚠ Dias em atraso: {overdue_days}\n"
                f"Multa: {format_currency(fine_amount)}\n"
            )
        details += f"\nTotal a pagar: {format_currency(total)}"

        if not messagebox.askyesno("Confirmar Devolução", details):
            return

        RentalModel.return_movie(rental_id, today.isoformat(), total)
        messagebox.showinfo("Sucesso", f"Devolução concluída!\nTotal: {format_currency(total)}")
        self.refresh_return_table()
        self.refresh_combos()
        self.refresh_history()

    def refresh_history(self):
        self.history_table.clear()
        search = self.history_search_entry.get().strip()
        rentals = RentalModel.all_history(search)
        for r in rentals:
            status_map = {"active": "● Ativo", "returned": "✓ Devolvido"}
            self.history_table.insert((
                r["id"],
                r["movie_title"],
                r["customer_name"],
                format_date(r["rental_date"]),
                format_date(r["return_date"]),
                format_currency(r["total_amount"]) if r["total_amount"] else "-",
                status_map.get(r["status"], r["status"]),
            ))
