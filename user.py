import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from dashboard import Dashboard
import os
import sys
import datetime as dt
import re

class User:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.email = None
        self.name = None
        self.bg_image_path = os.path.join(os.path.dirname(__file__), "background.png")
        self.bg_image_tk = None
        
        # Color Palette from the SVG
        self.clr_deep_bg = "#0F2040"    # Dark navy background
        self.clr_card_bg = "#162C50"    # Slightly lighter navy for cards
        self.clr_accent = "#2196F3"     # Bright blue for buttons
        self.clr_text_main = "#FFFFFF"  # White text
        self.clr_text_dim = "#A0B0C0"   # Muted text for labels
        self.clr_border = "#1E3A60"

        self.show_home()

    def show_home(self):
        self.clear_window()
        self.root.configure(bg=self.clr_deep_bg)

        # Main Canvas for background image
        main_canvas = tk.Canvas(self.root, bg=self.clr_deep_bg, highlightthickness=0)
        main_canvas.pack(fill="both", expand=True)

        def _update_bg(event=None):
            main_canvas.delete("bg")
            if not os.path.exists(self.bg_image_path):
                return
            try:
                # Use current canvas size; fallback to current window size
                width = max(1, main_canvas.winfo_width())
                height = max(1, main_canvas.winfo_height())
                img = Image.open(self.bg_image_path).resize((width, height), Image.ANTIALIAS)
                self.bg_image_tk = ImageTk.PhotoImage(img)
                main_canvas.create_image(0, 0, image=self.bg_image_tk, anchor="nw", tags="bg")
                main_canvas.lower("bg")
            except Exception as e:
                print(f"Could not load background image: {e}")

        main_canvas.bind("<Configure>", _update_bg)
        _update_bg()

        container = tk.Frame(main_canvas, bg=self.clr_deep_bg)
        container.place(relx=0.5, rely=0.5, anchor="center", width=500)

        # 1. Header Section
        tk.Label(container, text="TRACKSY", font=("Arial", 22, "bold"), 
                 fg=self.clr_text_main, bg=self.clr_deep_bg).pack(pady=(10, 5))
        tk.Label(container, text="Smart money management at your fingertips", 
                 font=("Arial", 10), fg=self.clr_text_dim, bg=self.clr_deep_bg).pack()

        # 2. Stat Boxes (Income, Expense, Balance)
        stats_frame = tk.Frame(container, bg=self.clr_deep_bg)
        stats_frame.pack(pady=30, fill="x")
        
        # We can simulate the 3 boxes
        self.mini_stat(stats_frame, "Total Income", "$43,300", "#4CAF50").grid(row=0, column=0, padx=5)
        self.mini_stat(stats_frame, "Total Expenses", "$38,060", "#F44336").grid(row=0, column=1, padx=5)
        self.mini_stat(stats_frame, "Net Balance", "$5,240", "#2196F3").grid(row=0, column=2, padx=5)

        # 3. Login Card (The dark rounded box)
        login_card = tk.Frame(container, bg=self.clr_card_bg, padx=30, pady=30, 
                              highlightthickness=1, highlightbackground=self.clr_border)
        login_card.pack(fill="x", pady=10)

        tk.Label(login_card, text="Sign In to Your Account", font=("Arial", 14, "bold"), 
                 fg=self.clr_text_main, bg=self.clr_card_bg).pack(pady=(0, 20))

        # Email
        tk.Label(login_card, text="Email", font=("Arial", 9), fg=self.clr_text_dim, bg=self.clr_card_bg).pack(anchor="w")
        self.email_entry = self.dark_entry(login_card)
        self.email_entry.pack(fill="x", pady=(5, 15))

        # Password
        tk.Label(login_card, text="Password", font=("Arial", 9), fg=self.clr_text_dim, bg=self.clr_card_bg).pack(anchor="w")
        self.password_entry = self.dark_entry(login_card, show="*")
        self.password_entry.pack(fill="x", pady=(5, 20))

        # Login Button
        tk.Button(login_card, text="Login", bg=self.clr_accent, fg="white", font=("Arial", 11, "bold"),
                  relief="flat", pady=10, cursor="hand2", command=self.login).pack(fill="x")

        # 4. Footer Links
        footer = tk.Frame(container, bg=self.clr_deep_bg)
        footer.pack(pady=20)
        
        tk.Label(footer, text="Don't have an account?", font=("Arial", 9), 
                 fg=self.clr_text_dim, bg=self.clr_deep_bg).pack()
        tk.Button(footer, text="Create one now →", font=("Arial", 9, "underline"), 
                  fg=self.clr_accent, bg=self.clr_deep_bg, relief="flat", bd=0, 
                  cursor="hand2", command=self.show_register).pack()

    # --- UI Components ---
    def mini_stat(self, parent, label, value, color):
        f = tk.Frame(parent, bg=self.clr_card_bg, padx=10, pady=10, width=150,
                     highlightthickness=1, highlightbackground=self.clr_border)
        f.pack_propagate(False)
        tk.Label(f, text=label, font=("Arial", 8), fg=self.clr_text_dim, bg=self.clr_card_bg).pack()
        tk.Label(f, text=value, font=("Arial", 11, "bold"), fg=color, bg=self.clr_card_bg).pack()
        return f

    def dark_entry(self, parent, show=""):
        return tk.Entry(parent, font=("Arial", 11), bg="#0B1A33", fg="white",
                        insertbackground="white", relief="flat", 
                        highlightthickness=1, highlightbackground=self.clr_border, show=show)

    def show_register(self):
        self.clear_window()
        self.root.configure(bg=self.clr_deep_bg)

        container = tk.Frame(self.root, bg=self.clr_deep_bg)
        container.place(relx=0.5, rely=0.5, anchor="center", width=500)

        tk.Label(container, text="Create an Account", font=("Arial", 18, "bold"),
                 fg=self.clr_text_main, bg=self.clr_deep_bg).pack(pady=(10, 10))

        reg_card = tk.Frame(container, bg=self.clr_card_bg, padx=30, pady=20,
                            highlightthickness=1, highlightbackground=self.clr_border)
        reg_card.pack(fill="x")

        tk.Label(reg_card, text="Name", font=("Arial", 9), fg=self.clr_text_dim, bg=self.clr_card_bg).pack(anchor="w")
        name_entry = self.dark_entry(reg_card)
        name_entry.pack(fill="x", pady=(5, 10))

        tk.Label(reg_card, text="Email", font=("Arial", 9), fg=self.clr_text_dim, bg=self.clr_card_bg).pack(anchor="w")
        email_entry = self.dark_entry(reg_card)
        email_entry.pack(fill="x", pady=(5, 10))

        tk.Label(reg_card, text="Date of Birth (YYYY-MM-DD)", font=("Arial", 9), fg=self.clr_text_dim, bg=self.clr_card_bg).pack(anchor="w")
        dob_entry = self.dark_entry(reg_card)
        dob_entry.pack(fill="x", pady=(5, 10))

        tk.Label(reg_card, text="Password", font=("Arial", 9), fg=self.clr_text_dim, bg=self.clr_card_bg).pack(anchor="w")
        password_entry = self.dark_entry(reg_card, show="*")
        password_entry.pack(fill="x", pady=(5, 10))

        tk.Label(reg_card, text="Confirm Password", font=("Arial", 9), fg=self.clr_text_dim, bg=self.clr_card_bg).pack(anchor="w")
        password_confirm = self.dark_entry(reg_card, show="*")
        password_confirm.pack(fill="x", pady=(5, 15))

        def submit_registration():
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            dob = dob_entry.get().strip()
            password = password_entry.get().strip()
            password2 = password_confirm.get().strip()

            if not name or not email or not dob or not password or not password2:
                messagebox.showerror("Registration Error", "Please fill in all fields")
                return

            if not re.fullmatch(r"[A-Za-z0-9._%+-]+@gmail\.com", email, re.IGNORECASE):
                messagebox.showerror("Registration Error", "Please enter a valid Gmail address")
                return

            try:
                dob_date = dt.datetime.strptime(dob, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror("Registration Error", "Date of Birth must be in YYYY-MM-DD format")
                return

            today = dt.date.today()
            if dob_date > today:
                messagebox.showerror("Registration Error", "Date of Birth cannot be in the future")
                return

            if password != password2:
                messagebox.showerror("Registration Error", "Passwords do not match")
                return

            success, msg = self.db.register_user(name, email, dob, password)
            if success:
                messagebox.showinfo("Success", "Account created successfully. You may now login.")
                self.show_home()
            else:
                messagebox.showerror("Registration Error", msg)

        tk.Button(reg_card, text="Register", bg=self.clr_accent, fg="white",
                  font=("Arial", 11, "bold"), relief="flat", pady=10,
                  cursor="hand2", command=submit_registration).pack(fill="x", pady=(0, 8))

        tk.Button(reg_card, text="Back to Login", bg="#354A6A", fg="white",
                  font=("Arial", 9), relief="flat", pady=8,
                  cursor="hand2", command=self.show_home).pack(fill="x")

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        if self.db.validate_user(email, password):
            self.email = email
            self.name = self.db.get_user_name(email)
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid email or password")

    def show_dashboard(self):
        self.clear_window()
        Dashboard(self.root, self.db, self.email, self.name, self.logout)

    def logout(self):
        self.show_home()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()