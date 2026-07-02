import customtkinter as ctk
from tkinter import messagebox
from database.models import CustomerModel
from components.table import Table
from utils.helpers import validate_cpf
from utils import theme


class CustomersFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(30, 16))
        theme.page_title(
            header, f"{theme.ICON['nav_customers']}  Gerenciar Clientes"
        ).pack(side="left", anchor="w")

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(padx=40, fill="x", pady=(0, 16))

        self.search_entry = theme.search_entry(
            toolbar, f"{theme.ICON['search']}  Buscar cliente..."
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh())

        theme.danger_button(
            toolbar, f"{theme.ICON['delete']}  Excluir", self.delete_customer, width=120
        ).pack(side="right")
        theme.ghost_button(
            toolbar, f"{theme.ICON['edit']}  Editar", self.edit_customer, width=110
        ).pack(side="right", padx=(0, 10))
        theme.primary_button(
            toolbar, f"{theme.ICON['add']}  Adicionar Cliente", self.add_customer, width=190
        ).pack(side="right", padx=(0, 10))

        columns = {
            "id": "ID",
            "name": "Nome",
            "cpf": "CPF",
            "phone": "Telefone",
            "email": "E-mail",
        }
        widths = {"id": 50, "name": 300, "cpf": 150, "phone": 150, "email": 250}

        self.table = Table(self, columns, widths)
        self.table.pack(padx=40, pady=(0, 30), fill="both", expand=True)

        self.refresh()

    def refresh(self):
        self.table.clear()
        search = self.search_entry.get().strip()
        customers = CustomerModel.all(search)
        for c in customers:
            self.table.insert((
                c["id"],
                c["name"],
                c["cpf"],
                c["phone"] or "-",
                c["email"] or "-",
            ))

    def add_customer(self):
        CustomerForm(self, self.app, None, self.refresh)

    def edit_customer(self):
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um cliente para editar.")
            return
        customer_id = int(selected["values"][0])
        CustomerForm(self, self.app, customer_id, self.refresh)

    def delete_customer(self):
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um cliente para excluir.")
            return
        customer_id = int(selected["values"][0])
        count = CustomerModel.rental_count(customer_id)

        if count > 0:
            confirmed = messagebox.askyesno(
                "Cliente com histórico",
                f"Este cliente possui {count} locação(ões) no histórico.\n\n"
                "Excluí-lo também removerá esses registros de locação "
                "permanentemente. Deseja continuar?",
                icon="warning",
            )
        else:
            confirmed = messagebox.askyesno(
                "Confirmar", "Excluir este cliente permanentemente?"
            )

        if not confirmed:
            return

        try:
            CustomerModel.delete(customer_id, force=count > 0)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível excluir o cliente:\n{e}")
            return
        self.refresh()


class CustomerForm(ctk.CTkToplevel):
    def __init__(self, master, app, customer_id=None, callback=None):
        super().__init__(master)
        self.app = app
        self.customer_id = customer_id
        self.callback = callback

        title_text = "Editar Cliente" if customer_id else "Adicionar Cliente"
        self.title(title_text)
        self.geometry("500x450")
        self.resizable(False, False)

        self.customer_data = None
        if customer_id:
            self.customer_data = CustomerModel.get_by_id(customer_id)

        ctk.CTkLabel(
            self, text=title_text, font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 20))

        form = ctk.CTkFrame(self)
        form.pack(padx=30, fill="both", expand=True)

        self.entries = {}
        fields = [
            ("name", "Nome *"),
            ("cpf", "CPF *"),
            ("phone", "Telefone"),
            ("email", "E-mail"),
            ("address", "Endereço"),
        ]

        for key, label in fields:
            frame_row = ctk.CTkFrame(form, fg_color="transparent")
            frame_row.pack(fill="x", pady=5)
            ctk.CTkLabel(frame_row, text=label, width=100, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(frame_row)
            entry.pack(side="left", fill="x", expand=True)
            self.entries[key] = entry

        if self.customer_data:
            self.populate()

        theme.primary_button(
            self, f"{theme.ICON['save']}  Salvar", self.save, height=44
        ).pack(pady=20, padx=30, fill="x")

        self.after(100, self.grab_set)

    def populate(self):
        data = self.customer_data
        self.entries["name"].insert(0, data["name"] or "")
        self.entries["cpf"].insert(0, data["cpf"] or "")
        self.entries["phone"].insert(0, data["phone"] or "")
        self.entries["email"].insert(0, data["email"] or "")
        self.entries["address"].insert(0, data["address"] or "")

    def save(self):
        name = self.entries["name"].get().strip()
        cpf = self.entries["cpf"].get().strip()

        if not name:
            messagebox.showerror("Erro", "O campo Nome é obrigatório.")
            return
        if not cpf:
            messagebox.showerror("Erro", "O campo CPF é obrigatório.")
            return

        data = {
            "name": name,
            "cpf": cpf,
            "phone": self.entries["phone"].get().strip() or None,
            "email": self.entries["email"].get().strip() or None,
            "address": self.entries["address"].get().strip() or None,
        }

        try:
            if self.customer_id:
                CustomerModel.update(self.customer_id, data)
            else:
                CustomerModel.create(data)
        except Exception as e:
            messagebox.showerror("Erro", f"CPF já cadastrado ou erro no banco:\n{e}")
            return

        if self.callback:
            self.callback()
        self.destroy()
