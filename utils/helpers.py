import re
from datetime import date, datetime
from io import BytesIO
from PIL import Image, ImageTk


def format_currency(value):
    return f"R$ {value:,.2f}"


def format_date(date_str):
    if not date_str:
        return "-"
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return d.strftime("%d/%m/%Y")


def validate_cpf(cpf):
    cpf = re.sub(r"\D", "", cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in range(9, 11):
        total = sum(int(cpf[j]) * (i + 1 - j) for j in range(i))
        digit = (total * 10 % 11) % 11
        if int(cpf[i]) != digit:
            return False
    return True


def calc_fine_days(return_date_str, expected_return_str, fine_per_day):
    return_date = datetime.strptime(return_date_str, "%Y-%m-%d").date()
    expected_date = datetime.strptime(expected_return_str, "%Y-%m-%d").date()
    overdue_days = (return_date - expected_date).days
    if overdue_days > 0:
        return overdue_days * fine_per_day
    return 0


def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d").date()
    d2 = datetime.strptime(d2, "%Y-%m-%d").date()
    return (d2 - d1).days


def load_image_from_blob(blob, size=(120, 160)):
    if not blob:
        return None
    try:
        img = Image.open(BytesIO(blob))
        img.thumbnail(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


def load_ctk_image_from_blob(blob, size=(120, 160)):
    if not blob:
        return None
    try:
        from customtkinter import CTkImage
        img = Image.open(BytesIO(blob))
        img.thumbnail(size, Image.LANCZOS)
        return CTkImage(img, size=img.size)
    except Exception:
        return None


def read_image_file(filepath):
    try:
        with open(filepath, "rb") as f:
            return f.read()
    except Exception:
        return None
