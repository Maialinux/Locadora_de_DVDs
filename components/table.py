import customtkinter as ctk
from tkinter import ttk
from utils import theme


class Table(ctk.CTkFrame):
    def __init__(self, master, columns, column_widths=None, **kwargs):
        kwargs.setdefault("fg_color", theme.BG_SURFACE)
        kwargs.setdefault("corner_radius", theme.RADIUS)
        super().__init__(master, **kwargs)

        style = ttk.Style()
        style.theme_use("clam")

        surface = theme.BG_SURFACE[1]
        surface_alt = theme.BG_SURFACE_2[1]
        text_color = theme.TEXT[1]
        heading_bg = "#141520"

        style.configure(
            "Locadora.Treeview",
            background=surface,
            foreground=text_color,
            fieldbackground=surface,
            borderwidth=0,
            relief="flat",
            font=(theme.FONT_FAMILY, 12),
            rowheight=38,
        )
        # remove a borda/contorno padrão do Treeview
        style.layout("Locadora.Treeview", [
            ("Locadora.Treeview.treearea", {"sticky": "nswe"})
        ])
        style.configure(
            "Locadora.Treeview.Heading",
            background=heading_bg,
            foreground=theme.TEXT_MUTED[1],
            font=(theme.FONT_FAMILY, 11, "bold"),
            relief="flat",
            borderwidth=0,
            padding=(8, 10),
        )
        style.map(
            "Locadora.Treeview.Heading",
            background=[("active", heading_bg)],
        )
        style.map(
            "Locadora.Treeview",
            background=[("selected", theme.ACCENT)],
            foreground=[("selected", "#ffffff")],
        )

        self.tree = ttk.Treeview(
            self,
            columns=list(columns.keys()),
            show="headings",
            selectmode="browse",
            style="Locadora.Treeview",
        )

        for col_id, col_text in columns.items():
            self.tree.heading(col_id, text=col_text)
            if column_widths and col_id in column_widths:
                self.tree.column(col_id, width=column_widths[col_id], minwidth=50)
            else:
                self.tree.column(col_id, width=120, minwidth=50)

        # Linhas zebradas para leitura mais confortável
        self.tree.tag_configure("oddrow", background=surface)
        self.tree.tag_configure("evenrow", background=surface_alt)

        scrollbar = ctk.CTkScrollbar(
            self, orientation="vertical", command=self.tree.yview,
            fg_color="transparent", button_color=theme.BG_SURFACE_2,
            button_hover_color=theme.ACCENT,
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
        scrollbar.pack(side="right", fill="y", pady=8, padx=(2, 6))

        self._row_index = 0

    def insert(self, values, iid=None):
        tag = "evenrow" if self._row_index % 2 else "oddrow"
        self._row_index += 1
        if iid:
            self.tree.insert("", "end", iid=str(iid), values=values, tags=(tag,))
        else:
            self.tree.insert("", "end", values=values, tags=(tag,))

    def clear(self):
        self.tree.delete(*self.tree.get_children())
        self._row_index = 0

    def get_selected(self):
        selection = self.tree.selection()
        if not selection:
            return None
        item = self.tree.item(selection[0])
        return {"iid": selection[0], "values": item["values"]}

    def get_all_items(self):
        return [
            {"iid": iid, "values": self.tree.item(iid)["values"]}
            for iid in self.tree.get_children()
        ]
