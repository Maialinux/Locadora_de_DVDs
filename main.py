import customtkinter as ctk
from database.connection import init_db
from components.sidebar import Sidebar
from utils import theme

from views.dashboard import DashboardFrame
from views.movies_view import MoviesFrame
from views.customers_view import CustomersFrame
from views.rentals_view import RentalsFrame
from views.reports_view import ReportsFrame


import os
import sys
from PIL import Image, ImageTk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Locadora de DVDs")
        self.geometry("1200x700")
        self.minsize(1000, 600)

        # Configurar ícone da janela
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, "logo.ico")
        else:
            icon_path = os.path.join(os.path.dirname(__file__), "logo.ico")

        if os.path.exists(icon_path):
            try:
                # Compatibilidade avançada para Linux/Windows usando wm_iconphoto
                img = Image.open(icon_path)
                self.icon_photo = ImageTk.PhotoImage(img) # Mantém referência para evitar Garbage Collection
                self.wm_iconphoto(True, self.icon_photo)
            except Exception:
                try:
                    self.iconbitmap(icon_path)
                except Exception:
                    pass

        theme.apply_global_theme()
        self.configure(fg_color=theme.BG_APP)

        init_db()

        self.sidebar = Sidebar(self, self.switch_frame)
        self.sidebar.pack(side="left", fill="y")

        self.container = ctk.CTkFrame(self, corner_radius=0, fg_color=theme.BG_APP)
        self.container.pack(side="right", fill="both", expand=True)

        self.frames = {}
        for F, key in [
            (DashboardFrame, "dashboard"),
            (MoviesFrame, "movies"),
            (CustomersFrame, "customers"),
            (RentalsFrame, "rentals"),
            (ReportsFrame, "reports"),
        ]:
            frame = F(self.container, self)
            self.frames[key] = frame

        self.switch_frame("dashboard")

    def switch_frame(self, key):
        for frame in self.frames.values():
            frame.pack_forget()
        target = self.frames.get(key)
        if target:
            target.pack(fill="both", expand=True)
            self.sidebar.set_active(key)
            if hasattr(target, "refresh"):
                target.refresh()

    def refresh_current(self):
        for key, frame in self.frames.items():
            if frame.winfo_ismapped():
                if hasattr(frame, "refresh"):
                    frame.refresh()
                break


if __name__ == "__main__":
    app = App()
    app.mainloop()
