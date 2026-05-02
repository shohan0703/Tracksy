import os
import tkinter as tk
from tkinter import messagebox
from database import DatabaseManager
from user import User


def main():
    root = tk.Tk()
    root.title("Tracksy")
    root.geometry("600x600")
    root.configure(bg="#2059A3")

    try:
        db = DatabaseManager(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "expenses"),
            port=int(os.getenv("DB_PORT", 3306)),
        )
    except Exception as e:
        messagebox.showerror(
            "Database Error",
            f"Could not connect to MySQL.\n\n{e}\n\n"
            "Check your DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, and DB_PORT."
        )
        root.destroy()
        return

    User(root, db)
    root.mainloop()


if __name__ == "__main__":
    main()