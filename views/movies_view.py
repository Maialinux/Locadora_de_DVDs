import customtkinter as ctk
from tkinter import filedialog, messagebox
from database.models import MovieModel
from components.table import Table
from utils.helpers import format_currency, read_image_file, load_ctk_image_from_blob
from utils import theme


class MoviesFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.cover_blob = None

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(30, 16))
        theme.page_title(
            header, f"{theme.ICON['nav_movies']}  Gerenciar Filmes"
        ).pack(side="left", anchor="w")

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(padx=40, fill="x", pady=(0, 16))

        self.search_entry = theme.search_entry(
            toolbar, f"{theme.ICON['search']}  Buscar filme..."
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh())

        theme.danger_button(
            toolbar, f"{theme.ICON['delete']}  Excluir", self.delete_movie, width=120
        ).pack(side="right")
        theme.ghost_button(
            toolbar, f"{theme.ICON['edit']}  Editar", self.edit_movie, width=110
        ).pack(side="right", padx=(0, 10))
        theme.primary_button(
            toolbar, f"{theme.ICON['add']}  Adicionar Filme", self.add_movie, width=180
        ).pack(side="right", padx=(0, 10))

        columns = {
            "id": "ID",
            "title": "Título",
            "year": "Ano",
            "genre": "Gênero",
            "director": "Diretor",
            "available": "Disponíveis",
            "quantity": "Total",
            "daily_rate": "Diária",
        }
        widths = {
            "id": 50, "title": 300, "year": 60, "genre": 120,
            "director": 200, "available": 100, "quantity": 70, "daily_rate": 100,
        }

        self.table = Table(self, columns, widths)
        self.table.pack(padx=40, pady=(0, 30), fill="both", expand=True)

        self.refresh()

    def refresh(self):
        self.table.clear()
        search = self.search_entry.get().strip()
        movies = MovieModel.all(search)
        for m in movies:
            self.table.insert((
                m["id"],
                m["title"],
                m["year"] or "-",
                m["genre"] or "-",
                m["director"] or "-",
                m["available"],
                m["quantity"],
                format_currency(m["daily_rate"]),
            ))

    def add_movie(self):
        MovieForm(self, self.app, None, self.refresh)

    def edit_movie(self):
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um filme para editar.")
            return
        movie_id = int(selected["values"][0])
        MovieForm(self, self.app, movie_id, self.refresh)

    def delete_movie(self):
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um filme para excluir.")
            return
        movie_id = int(selected["values"][0])
        count = MovieModel.rental_count(movie_id)

        if count > 0:
            confirmed = messagebox.askyesno(
                "Filme com histórico",
                f"Este filme possui {count} locação(ões) no histórico.\n\n"
                "Excluí-lo também removerá esses registros de locação "
                "permanentemente. Deseja continuar?",
                icon="warning",
            )
        else:
            confirmed = messagebox.askyesno(
                "Confirmar", "Excluir este filme permanentemente?"
            )

        if not confirmed:
            return

        try:
            MovieModel.delete(movie_id, force=count > 0)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível excluir o filme:\n{e}")
            return
        self.refresh()


class MovieForm(ctk.CTkToplevel):
    def __init__(self, master, app, movie_id=None, callback=None):
        super().__init__(master)
        self.app = app
        self.movie_id = movie_id
        self.callback = callback
        self.cover_blob = None
        self.cover_path = None
        self.cover_preview = None

        title_text = "Editar Filme" if movie_id else "Adicionar Filme"
        self.title(title_text)
        self.geometry("550x680")
        self.resizable(False, False)

        self.movie_data = None
        if movie_id:
            self.movie_data = MovieModel.get_by_id(movie_id)

        ctk.CTkLabel(
            self, text=title_text, font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 20))

        form = ctk.CTkScrollableFrame(self)
        form.pack(padx=30, fill="both", expand=True)

        self.entries = {}
        fields = [
            ("title", "Título *"),
            ("year", "Ano"),
            ("genre", "Gênero"),
            ("director", "Diretor"),
            ("synopsis", "Sinopse"),
        ]

        for key, label in fields:
            frame_row = ctk.CTkFrame(form, fg_color="transparent")
            frame_row.pack(fill="x", pady=5)
            ctk.CTkLabel(frame_row, text=label, width=100, anchor="w").pack(side="left")
            if key == "synopsis":
                entry = ctk.CTkTextbox(frame_row, height=80)
                entry.pack(side="left", fill="x", expand=True)
            else:
                entry = ctk.CTkEntry(frame_row)
                entry.pack(side="left", fill="x", expand=True)
            self.entries[key] = entry

        qty_frame = ctk.CTkFrame(form, fg_color="transparent")
        qty_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(qty_frame, text="Quantidade *", width=100, anchor="w").pack(side="left")
        self.entries["quantity"] = ctk.CTkEntry(qty_frame)
        self.entries["quantity"].pack(side="left", fill="x", expand=True)

        rate_frame = ctk.CTkFrame(form, fg_color="transparent")
        rate_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(rate_frame, text="Diária (R$) *", width=100, anchor="w").pack(side="left")
        self.entries["daily_rate"] = ctk.CTkEntry(rate_frame)
        self.entries["daily_rate"].pack(side="left", fill="x", expand=True)

        fine_frame = ctk.CTkFrame(form, fg_color="transparent")
        fine_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(fine_frame, text="Multa/dia (R$)", width=100, anchor="w").pack(side="left")
        self.entries["fine_per_day"] = ctk.CTkEntry(fine_frame)
        self.entries["fine_per_day"].pack(side="left", fill="x", expand=True)

        self.cover_frame = ctk.CTkFrame(form, fg_color="transparent")
        self.cover_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(self.cover_frame, text="Capa do Filme").pack(anchor="w")
        self.cover_label = ctk.CTkLabel(
            self.cover_frame, text="Nenhuma imagem selecionada",
            width=120, height=160, fg_color=("gray85", "gray25"),
            corner_radius=8,
        )
        self.cover_label.pack(pady=5)
        ctk.CTkButton(
            self.cover_frame, text="Selecionar Imagem", command=self.select_image
        ).pack()

        if self.movie_data:
            self.populate()

        btn_save = theme.primary_button(
            self, f"{theme.ICON['save']}  Salvar", self.save, height=44
        )
        btn_save.pack(pady=20, padx=30, fill="x")

        self.after(100, self.grab_set)

    def populate(self):
        data = self.movie_data
        self.entries["title"].insert(0, data["title"] or "")
        self.entries["year"].insert(0, str(data["year"] or ""))
        self.entries["genre"].insert(0, data["genre"] or "")
        self.entries["director"].insert(0, data["director"] or "")
        self.entries["synopsis"].insert("1.0", data["synopsis"] or "")
        self.entries["quantity"].insert(0, str(data["quantity"] or ""))
        self.entries["daily_rate"].insert(0, str(data["daily_rate"] or ""))
        self.entries["fine_per_day"].insert(0, str(data["fine_per_day"] or "2.00"))

        if data.get("cover_image"):
            self.cover_blob = data["cover_image"]
            img = load_ctk_image_from_blob(self.cover_blob, (120, 160))
            if img:
                self.cover_label.configure(image=img, text="")

    def select_image(self):
        filepath = filedialog.askopenfilename(
            title="Selecionar imagem da capa",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp *.gif")],
        )
        if filepath:
            self.cover_blob = read_image_file(filepath)
            img = load_ctk_image_from_blob(self.cover_blob, (120, 160))
            if img:
                self.cover_label.configure(image=img, text="")

    def save(self):
        title = self.entries["title"].get().strip()
        daily_rate_str = self.entries["daily_rate"].get().strip()

        if not title:
            messagebox.showerror("Erro", "O campo Título é obrigatório.")
            return
        if not daily_rate_str:
            messagebox.showerror("Erro", "O campo Diária é obrigatório.")
            return

        try:
            daily_rate = float(daily_rate_str.replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Diária deve ser um valor numérico.")
            return

        quantity_str = self.entries["quantity"].get().strip() or "1"
        try:
            quantity = int(quantity_str)
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número inteiro.")
            return

        fine_str = self.entries["fine_per_day"].get().strip() or "2.00"
        try:
            fine_per_day = float(fine_str.replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Multa deve ser um valor numérico.")
            return

        data = {
            "title": title,
            "year": self.entries["year"].get().strip() or None,
            "genre": self.entries["genre"].get().strip() or None,
            "director": self.entries["director"].get().strip() or None,
            "synopsis": self.entries["synopsis"].get("1.0", "end-1c").strip() or None,
            "quantity": quantity,
            "available": quantity,
            "daily_rate": daily_rate,
            "fine_per_day": fine_per_day,
        }

        if self.movie_id:
            if self.cover_blob and self.cover_blob != self.movie_data.get("cover_image"):
                MovieModel.update(self.movie_id, data, self.cover_blob)
            else:
                MovieModel.update(self.movie_id, data)
        else:
            MovieModel.create(data, self.cover_blob)

        if self.callback:
            self.callback()
        self.destroy()
