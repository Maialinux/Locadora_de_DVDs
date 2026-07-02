import sqlite3
import os
import sys
import shutil
from contextlib import contextmanager

# Detecta se a aplicação está rodando compilada pelo PyInstaller
if getattr(sys, 'frozen', False):
    # O diretório onde está o executável
    exe_dir = os.path.dirname(sys.executable)
    DB_PATH = os.path.join(exe_dir, "locadora.db")
    
    # Copia o banco de dados inicial empacotado para o diretório do executável, se ainda não existir
    if not os.path.exists(DB_PATH):
        bundled_db = os.path.join(sys._MEIPASS, "database", "locadora.db")
        if os.path.exists(bundled_db):
            try:
                shutil.copy2(bundled_db, DB_PATH)
            except Exception as e:
                print(f"Erro ao copiar o banco de dados inicial: {e}")
else:
    # Modo de desenvolvimento
    DB_PATH = os.path.join(os.path.dirname(__file__), "locadora.db")



def get_connection():
    # timeout=10 -> aguarda até 10s por um bloqueio antes de falhar.
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    # WAL permite que leituras e escritas ocorram simultaneamente sem se
    # bloquearem; busy_timeout reforça a espera em caso de concorrência.
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 10000")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def db():
    """Gerencia o ciclo de vida da conexão.

    Faz commit ao final, rollback em caso de erro e SEMPRE fecha a conexão —
    evitando conexões vazadas que mantêm o banco bloqueado.
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                year INTEGER,
                genre TEXT,
                director TEXT,
                synopsis TEXT,
                quantity INTEGER DEFAULT 1,
                available INTEGER DEFAULT 1,
                daily_rate REAL NOT NULL,
                fine_per_day REAL DEFAULT 2.00,
                cover_image BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                cpf TEXT UNIQUE NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS rentals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                rental_date DATE NOT NULL,
                expected_return DATE NOT NULL,
                return_date DATE,
                daily_rate REAL NOT NULL,
                fine_per_day REAL DEFAULT 2.00,
                total_amount REAL,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (movie_id) REFERENCES movies(id),
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            );
        """)
