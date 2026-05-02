import mysql.connector
import bcrypt
from datetime import datetime


class DatabaseManager:
    def __init__(self, host="localhost", user="root", password="", database="expenses", port=3306):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            autocommit=False,
        )
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                dob DATE NOT NULL,
                password_hash VARBINARY(255) NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                category VARCHAR(100) NOT NULL,
                `type` ENUM('income','expense') NOT NULL,
                date DATE NOT NULL,
                FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
            )
        """)

        self.conn.commit()
        cursor.close()

    def user_exists(self, email):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None

    def register_user(self, name, email, dob, password):
        try:
            name = name.strip()
            email = email.strip().lower()
            password = password.strip()
            dob = dob.strip()

            if not name or not email or not dob or not password:
                return False, "All fields are required."

            if self.user_exists(email):
                return False, "Email already exists."

            # Validate DOB format: YYYY-MM-DD
            try:
                dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
            except ValueError:
                return False, "DOB must be in YYYY-MM-DD format."

            password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO users (name, email, dob, password_hash)
                VALUES (%s, %s, %s, %s)
            """, (name, email, dob_date, password_hash))

            self.conn.commit()
            cursor.close()
            return True, "Account created successfully."

        except mysql.connector.Error as e:
            self.conn.rollback()
            return False, f"Database error: {e}"

        except Exception as e:
            self.conn.rollback()
            return False, f"Error: {e}"

    def validate_user(self, email, password):
        try:
            email = email.strip().lower()
            password = password.strip()

            cursor = self.conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()
            cursor.close()

            if result:
                password_hash = result[0]
                return bcrypt.checkpw(password.encode("utf-8"), password_hash)

            return False

        except Exception:
            return False

    def get_user_name(self, email):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM users WHERE email = %s", (email.strip().lower(),))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else ""

    def add_transaction(self, email, amount, category, trans_type, date):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (user_email, amount, category, `type`, date)
            VALUES (%s, %s, %s, %s, %s)
        """, (email.strip().lower(), amount, category.strip(), trans_type, date))
        self.conn.commit()
        cursor.close()

    def get_transactions(self, email):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT amount, category, `type`, date
            FROM transactions
            WHERE user_email = %s
            ORDER BY date DESC, id DESC
        """, (email.strip().lower(),))
        rows = cursor.fetchall()
        cursor.close()

        return [
            {
                "amount": row[0],
                "category": row[1],
                "type": row[2],
                "date": row[3]
            }
            for row in rows
        ]

    def get_summary_by_category(self, email):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT category, SUM(amount)
            FROM transactions
            WHERE user_email = %s AND `type` = 'expense'
            GROUP BY category
        """, (email.strip().lower(),))
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_totals(self, email):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN `type` = 'income' THEN amount ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN `type` = 'expense' THEN amount ELSE 0 END), 0)
            FROM transactions
            WHERE user_email = %s
        """, (email.strip().lower(),))
        result = cursor.fetchone()
        cursor.close()
        return result if result else (0, 0)

    def close(self):
        if self.conn.is_connected():
            self.conn.close()