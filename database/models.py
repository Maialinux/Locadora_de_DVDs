from database.connection import db
from datetime import date, datetime


class MovieModel:
    @staticmethod
    def all(search=None):
        with db() as conn:
            if search:
                rows = conn.execute(
                    "SELECT * FROM movies WHERE title LIKE ? OR director LIKE ? OR genre LIKE ? ORDER BY title",
                    (f"%{search}%", f"%{search}%", f"%{search}%"),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM movies ORDER BY title").fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(movie_id):
        with db() as conn:
            row = conn.execute("SELECT * FROM movies WHERE id = ?", (movie_id,)).fetchone()
            return dict(row) if row else None

    @staticmethod
    def create(data, cover_blob=None):
        with db() as conn:
            cursor = conn.execute(
                """INSERT INTO movies (title, year, genre, director, synopsis, quantity, available, daily_rate, fine_per_day, cover_image)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    data["title"],
                    data.get("year"),
                    data.get("genre"),
                    data.get("director"),
                    data.get("synopsis"),
                    data.get("quantity", 1),
                    data.get("available", data.get("quantity", 1)),
                    data["daily_rate"],
                    data.get("fine_per_day", 2.00),
                    cover_blob,
                ),
            )
            return cursor.lastrowid

    @staticmethod
    def update(movie_id, data, cover_blob=None):
        with db() as conn:
            fields = [
                "title = ?",
                "year = ?",
                "genre = ?",
                "director = ?",
                "synopsis = ?",
                "quantity = ?",
                "available = ?",
                "daily_rate = ?",
                "fine_per_day = ?",
            ]
            values = [
                data["title"],
                data.get("year"),
                data.get("genre"),
                data.get("director"),
                data.get("synopsis"),
                data.get("quantity"),
                data.get("available"),
                data["daily_rate"],
                data.get("fine_per_day", 2.00),
            ]
            if cover_blob is not None:
                fields.append("cover_image = ?")
                values.append(cover_blob)
            values.append(movie_id)
            conn.execute(
                f"UPDATE movies SET {', '.join(fields)} WHERE id = ?", values
            )

    @staticmethod
    def rental_count(movie_id):
        with db() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS total FROM rentals WHERE movie_id = ?",
                (movie_id,),
            ).fetchone()
            return row["total"] if row else 0

    @staticmethod
    def delete(movie_id, force=False):
        with db() as conn:
            if force:
                # remove o histórico de locações vinculado antes do filme
                conn.execute("DELETE FROM rentals WHERE movie_id = ?", (movie_id,))
            conn.execute("DELETE FROM movies WHERE id = ?", (movie_id,))


class CustomerModel:
    @staticmethod
    def all(search=None):
        with db() as conn:
            if search:
                rows = conn.execute(
                    "SELECT * FROM customers WHERE name LIKE ? OR cpf LIKE ? OR phone LIKE ? ORDER BY name",
                    (f"%{search}%", f"%{search}%", f"%{search}%"),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM customers ORDER BY name").fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(customer_id):
        with db() as conn:
            row = conn.execute(
                "SELECT * FROM customers WHERE id = ?", (customer_id,)
            ).fetchone()
            return dict(row) if row else None

    @staticmethod
    def create(data):
        with db() as conn:
            cursor = conn.execute(
                """INSERT INTO customers (name, cpf, phone, email, address)
                   VALUES (?, ?, ?, ?, ?)""",
                (data["name"], data["cpf"], data.get("phone"), data.get("email"), data.get("address")),
            )
            return cursor.lastrowid

    @staticmethod
    def update(customer_id, data):
        with db() as conn:
            conn.execute(
                """UPDATE customers SET name = ?, cpf = ?, phone = ?, email = ?, address = ?
                   WHERE id = ?""",
                (data["name"], data["cpf"], data.get("phone"), data.get("email"), data.get("address"), customer_id),
            )

    @staticmethod
    def rental_count(customer_id):
        with db() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS total FROM rentals WHERE customer_id = ?",
                (customer_id,),
            ).fetchone()
            return row["total"] if row else 0

    @staticmethod
    def delete(customer_id, force=False):
        with db() as conn:
            if force:
                # remove o histórico de locações vinculado antes do cliente
                conn.execute("DELETE FROM rentals WHERE customer_id = ?", (customer_id,))
            conn.execute("DELETE FROM customers WHERE id = ?", (customer_id,))


class RentalModel:
    @staticmethod
    def all_active(search=None):
        with db() as conn:
            if search:
                rows = conn.execute(
                    """SELECT r.*, m.title AS movie_title, c.name AS customer_name
                       FROM rentals r
                       JOIN movies m ON r.movie_id = m.id
                       JOIN customers c ON r.customer_id = c.id
                       WHERE r.status = 'active'
                         AND (m.title LIKE ? OR c.name LIKE ?)
                       ORDER BY r.rental_date DESC""",
                    (f"%{search}%", f"%{search}%"),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT r.*, m.title AS movie_title, c.name AS customer_name
                       FROM rentals r
                       JOIN movies m ON r.movie_id = m.id
                       JOIN customers c ON r.customer_id = c.id
                       WHERE r.status = 'active'
                       ORDER BY r.rental_date DESC"""
                ).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def all_history(search=None):
        with db() as conn:
            if search:
                rows = conn.execute(
                    """SELECT r.*, m.title AS movie_title, c.name AS customer_name
                       FROM rentals r
                       JOIN movies m ON r.movie_id = m.id
                       JOIN customers c ON r.customer_id = c.id
                       WHERE m.title LIKE ? OR c.name LIKE ?
                       ORDER BY r.rental_date DESC""",
                    (f"%{search}%", f"%{search}%"),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT r.*, m.title AS movie_title, c.name AS customer_name
                       FROM rentals r
                       JOIN movies m ON r.movie_id = m.id
                       JOIN customers c ON r.customer_id = c.id
                       ORDER BY r.rental_date DESC"""
                ).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(rental_id):
        with db() as conn:
            row = conn.execute(
                """SELECT r.*, m.title AS movie_title, c.name AS customer_name
                   FROM rentals r
                   JOIN movies m ON r.movie_id = m.id
                   JOIN customers c ON r.customer_id = c.id
                   WHERE r.id = ?""",
                (rental_id,),
            ).fetchone()
            return dict(row) if row else None

    @staticmethod
    def create(data):
        with db() as conn:
            cursor = conn.execute(
                """INSERT INTO rentals (movie_id, customer_id, rental_date, expected_return, daily_rate, fine_per_day, status)
                   VALUES (?, ?, ?, ?, ?, ?, 'active')""",
                (
                    data["movie_id"],
                    data["customer_id"],
                    data["rental_date"],
                    data["expected_return"],
                    data["daily_rate"],
                    data.get("fine_per_day", 2.00),
                ),
            )
            conn.execute(
                "UPDATE movies SET available = available - 1 WHERE id = ?",
                (data["movie_id"],),
            )
            return cursor.lastrowid

    @staticmethod
    def return_movie(rental_id, return_date, total_amount):
        with db() as conn:
            rental = conn.execute(
                "SELECT movie_id FROM rentals WHERE id = ?", (rental_id,)
            ).fetchone()
            if rental:
                conn.execute(
                    """UPDATE rentals SET return_date = ?, total_amount = ?, status = 'returned'
                       WHERE id = ?""",
                    (return_date, total_amount, rental_id),
                )
                conn.execute(
                    "UPDATE movies SET available = available + 1 WHERE id = ?",
                    (rental["movie_id"],),
                )

    @staticmethod
    def count_active():
        with db() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS total FROM rentals WHERE status = 'active'"
            ).fetchone()
            return row["total"] if row else 0

    @staticmethod
    def count_overdue():
        with db() as conn:
            today = date.today().isoformat()
            row = conn.execute(
                "SELECT COUNT(*) AS total FROM rentals WHERE status = 'active' AND expected_return < ?",
                (today,),
            ).fetchone()
            return row["total"] if row else 0

    @staticmethod
    def revenue_month():
        with db() as conn:
            today = date.today()
            first_day = today.replace(day=1).isoformat()
            row = conn.execute(
                "SELECT COALESCE(SUM(total_amount), 0) AS total FROM rentals WHERE status = 'returned' AND return_date >= ?",
                (first_day,),
            ).fetchone()
            return row["total"] if row else 0

    @staticmethod
    def active_rentals_data():
        with db() as conn:
            rows = conn.execute(
                """SELECT r.*, m.title AS movie_title, c.name AS customer_name
                   FROM rentals r
                   JOIN movies m ON r.movie_id = m.id
                   JOIN customers c ON r.customer_id = c.id
                   WHERE r.status = 'active'
                   ORDER BY r.expected_return""",
            ).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def most_rented_movies(limit=10):
        with db() as conn:
            rows = conn.execute(
                """SELECT m.id, m.title, COUNT(r.id) AS rental_count
                   FROM movies m
                   LEFT JOIN rentals r ON m.id = r.movie_id
                   GROUP BY m.id
                   ORDER BY rental_count DESC
                   LIMIT ?""",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def top_customers(limit=10):
        with db() as conn:
            rows = conn.execute(
                """SELECT c.id, c.name, COUNT(r.id) AS rental_count
                   FROM customers c
                   LEFT JOIN rentals r ON c.id = r.customer_id
                   GROUP BY c.id
                   ORDER BY rental_count DESC
                   LIMIT ?""",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def overdue_rentals():
        with db() as conn:
            today = date.today().isoformat()
            rows = conn.execute(
                """SELECT r.*, m.title AS movie_title, c.name AS customer_name,
                          CAST(julianday(?) - julianday(r.expected_return) AS INTEGER) AS days_overdue
                   FROM rentals r
                   JOIN movies m ON r.movie_id = m.id
                   JOIN customers c ON r.customer_id = c.id
                   WHERE r.status = 'active' AND r.expected_return < ?
                   ORDER BY r.expected_return""",
                (today, today),
            ).fetchall()
            return [dict(r) for r in rows]
