import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import calendar
import os

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas as pdf_canvas
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

# ============================================================
# Light finance dashboard redesign
# Keeps the original API:
# Dashboard(root, db, email, name, on_logout)
# ============================================================

# Light Mode Colors
LIGHT_MODE = {
    "APP_BG": "#F3F4F6",
    "SURFACE": "#FFFFFF",
    "SURFACE_ALT": "#F8FAFC",
    "BORDER": "#E5E7EB",
    "TEXT": "#1F2937",
    "TEXT_SOFT": "#64748B",
    "TEXT_MUTED": "#94A3B8",
    "PRIMARY": "#4564F2",
    "PRIMARY_DARK": "#3552DB",
    "INCOME": "#4CB7DA",
    "EXPENSE": "#FF4B4B",
    "SAVINGS": "#22C55E",
    "WARNING": "#F59E0B",
    "DARK_BUTTON": "#4B5563",
    "SIDEBAR_ACTIVE": "#4564F2",
    "CAL_DOT": "#93C5FD",
    "SELECTED_BG": "#E8EEFF",
    "TREEVIEW_BG": "#EDEFF5",
}

# Dark Mode Colors
DARK_MODE = {
    "APP_BG": "#0F172A",
    "SURFACE": "#1E293B",
    "SURFACE_ALT": "#334155",
    "BORDER": "#475569",
    "TEXT": "#F1F5F9",
    "TEXT_SOFT": "#CBD5E1",
    "TEXT_MUTED": "#94A3B8",
    "PRIMARY": "#6366F1",
    "PRIMARY_DARK": "#4F46E5",
    "INCOME": "#22D3EE",
    "EXPENSE": "#F87171",
    "SAVINGS": "#4ADE80",
    "WARNING": "#FBBF24",
    "DARK_BUTTON": "#1E293B",
    "SIDEBAR_ACTIVE": "#6366F1",
    "CAL_DOT": "#3B82F6",
    "SELECTED_BG": "#1E3A8A",
    "TREEVIEW_BG": "#0F172A",
}

# Default to light mode (kept for backward compatibility in global references)
APP_BG = LIGHT_MODE["APP_BG"]
SURFACE = LIGHT_MODE["SURFACE"]
SURFACE_ALT = LIGHT_MODE["SURFACE_ALT"]
BORDER = LIGHT_MODE["BORDER"]
TEXT = LIGHT_MODE["TEXT"]
TEXT_SOFT = LIGHT_MODE["TEXT_SOFT"]
TEXT_MUTED = LIGHT_MODE["TEXT_MUTED"]
PRIMARY = LIGHT_MODE["PRIMARY"]
PRIMARY_DARK = LIGHT_MODE["PRIMARY_DARK"]
INCOME = LIGHT_MODE["INCOME"]
EXPENSE = LIGHT_MODE["EXPENSE"]
SAVINGS = LIGHT_MODE["SAVINGS"]
WARNING = LIGHT_MODE["WARNING"]
DARK_BUTTON = LIGHT_MODE["DARK_BUTTON"]
SIDEBAR_ACTIVE = LIGHT_MODE["SIDEBAR_ACTIVE"]
CAL_DOT = LIGHT_MODE["CAL_DOT"]

CATEGORY_COLORS = [
    "#F65B7C",  # Food
    "#469CDB",  # Transportation
    "#F3C651",  # Housing
    "#53B6B8",  # Entertainment
    "#9B6CF2",  # Shopping
    "#22C55E",
    "#F97316",
    "#14B8A6",
    "#EF4444",
    "#8B5CF6",
]

MONTH_NAMES = [calendar.month_abbr[i] for i in range(1, 13)]


class Dashboard:
    def __init__(self, root, db, email, name, on_logout):
        self.root = root
        self.db = db
        self.email = email
        self.name = name
        self.on_logout = on_logout
        self.dark_mode = False  # Default to light mode

        today = date.today()
        self.active_page = "Dashboard"
        self.selected_date = None
        self.calendar_year = today.year
        self.calendar_month = today.month
        self.report_year = today.year
        self.report_month = today.month
        self.search_var = tk.StringVar()
        self.month_filter_var = tk.StringVar(value="All months")
        self.year_filter_var = tk.StringVar(value="All years")

        self._style_ttk()
        self.setup_ui()

    # --------------------------------------------------------
    # Styling & Theme Management
    # --------------------------------------------------------
    def _get_theme_colors(self):
        """Get current theme colors based on dark_mode flag"""
        return DARK_MODE if self.dark_mode else LIGHT_MODE

    def _c(self, color_key):
        """Shorthand to get a color from current theme"""
        return self._get_theme_colors().get(color_key, "#FFFFFF")

    def _update_theme_globals(self):
        """Update global color variables based on current theme"""
        global APP_BG, SURFACE, SURFACE_ALT, BORDER, TEXT, TEXT_SOFT, TEXT_MUTED
        global PRIMARY, PRIMARY_DARK, INCOME, EXPENSE, SAVINGS, WARNING, DARK_BUTTON, SIDEBAR_ACTIVE, CAL_DOT
        
        colors = self._get_theme_colors()
        APP_BG = colors["APP_BG"]
        SURFACE = colors["SURFACE"]
        SURFACE_ALT = colors["SURFACE_ALT"]
        BORDER = colors["BORDER"]
        TEXT = colors["TEXT"]
        TEXT_SOFT = colors["TEXT_SOFT"]
        TEXT_MUTED = colors["TEXT_MUTED"]
        PRIMARY = colors["PRIMARY"]
        PRIMARY_DARK = colors["PRIMARY_DARK"]
        INCOME = colors["INCOME"]
        EXPENSE = colors["EXPENSE"]
        SAVINGS = colors["SAVINGS"]
        WARNING = colors["WARNING"]
        DARK_BUTTON = colors["DARK_BUTTON"]
        SIDEBAR_ACTIVE = colors["SIDEBAR_ACTIVE"]
        CAL_DOT = colors["CAL_DOT"]

    def toggle_dark_mode(self):
        """Toggle between light and dark mode and refresh UI"""
        self.dark_mode = not self.dark_mode
        self._update_theme_globals()
        self._style_ttk()
        self.setup_ui()

    def _style_ttk(self):
        colors = self._get_theme_colors()
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure(
            "Tracker.Treeview",
            background=colors["SURFACE"],
            fieldbackground=colors["SURFACE"],
            foreground=colors["TEXT"],
            rowheight=34,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Tracker.Treeview.Heading",
            background=colors["SURFACE_ALT"],
            foreground=colors["TEXT"],
            borderwidth=0,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        style.map(
            "Tracker.Treeview",
            background=[("selected", colors["SELECTED_BG"])],
            foreground=[("selected", colors["TEXT"])],
        )
        style.configure(
            "Tracker.Horizontal.TProgressbar",
            troughcolor=colors["TREEVIEW_BG"],
            background=colors["PRIMARY"],
            bordercolor=colors["TREEVIEW_BG"],
            lightcolor=colors["PRIMARY"],
            darkcolor=colors["PRIMARY"],
        )

    # --------------------------------------------------------
    # Data helpers
    # --------------------------------------------------------
    def _all_txns(self):
        try:
            txns = self.db.get_transactions(self.email)
        except Exception:
            txns = []

        clean = []
        for t in txns:
            try:
                amount = float(t.get("amount", 0))
                tx_type = str(t.get("type", "")).lower().strip()
                category = str(t.get("category", "Other")).strip() or "Other"
                raw_date = str(t.get("date", "")).strip()
                parsed_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
                clean.append({
                    "amount": amount,
                    "type": tx_type,
                    "category": category,
                    "date": raw_date,
                    "date_obj": parsed_date,
                })
            except Exception:
                continue
        clean.sort(key=lambda x: (x["date"], x["type"], x["category"], x["amount"]))
        return clean

    def _month_year_options(self):
        txns = self._all_txns()
        months = sorted({t["date_obj"].strftime("%b %Y") for t in txns})
        years = sorted({str(t["date_obj"].year) for t in txns})
        return months, years

    def _transactions_for_selected_month(self):
        txns = self._all_txns()
        return [
            t for t in txns
            if t["date_obj"].year == self.report_year and t["date_obj"].month == self.report_month
        ]

    def _filtered_txns(self):
        txns = self._all_txns()
        query = self.search_var.get().strip().lower()
        month_filter = self.month_filter_var.get()
        year_filter = self.year_filter_var.get()

        result = []
        for t in txns:
            if self.selected_date and t["date_obj"] != self.selected_date:
                continue
            if month_filter != "All months" and t["date_obj"].strftime("%b %Y") != month_filter:
                continue
            if year_filter != "All years" and str(t["date_obj"].year) != year_filter:
                continue
            if query:
                hay = f"{t['date']} {t['type']} {t['category']} {t['amount']}".lower()
                if query not in hay:
                    continue
            result.append(t)
        return result

    def _dashboard_txns(self):
        if self.selected_date:
            return [t for t in self._all_txns() if t["date_obj"] == self.selected_date]
        return self._transactions_for_selected_month()

    def _month_summary(self, txns):
        income = sum(t["amount"] for t in txns if t["type"] == "income")
        expense = sum(t["amount"] for t in txns if t["type"] == "expense")
        balance = income - expense
        savings_rate = ((balance / income) * 100) if income > 0 else 0
        return {
            "income": income,
            "expense": expense,
            "balance": balance,
            "savings_rate": max(savings_rate, 0),
        }

    def _current_summary(self):
        return self._month_summary(self._dashboard_txns())

    def _lifetime_savings(self):
        """
        Calculate lifetime savings as the cumulative sum of all months' balances.
        
        - Starts from previous months' cumulative balances
        - INCLUDES the current month's balance
        - Positive month balance (income > expenses): adds to lifetime savings
        - Negative month balance (expenses > income): subtracts from lifetime savings (draws from savings)
        
        Example:
        - Jan: +$2,000 → Lifetime Savings = $2,000
        - Feb: +$1,500 → Lifetime Savings = $3,500
        - Mar (current): -$4,050 (expenses over income) → Lifetime Savings = $3,500 - $4,050 = -$550
        """
        buckets = self._get_month_buckets()
        lifetime_savings = 0.0
        
        # Iterate through ALL months (in chronological order), including current month
        for (year, month), data in sorted(buckets.items()):
            # Calculate month balance (positive or negative)
            month_balance = data["income"] - data["expense"]
            # Add to lifetime savings (if negative, it will reduce the total)
            lifetime_savings += month_balance
        
        return lifetime_savings

    def _get_category_data(self, txns):
        categories = {}
        for t in txns:
            if t["type"] == "expense":
                categories[t["category"]] = categories.get(t["category"], 0) + t["amount"]
        return sorted(categories.items(), key=lambda x: x[1], reverse=True)

    def _get_month_buckets(self):
        buckets = {}
        for t in self._all_txns():
            key = (t["date_obj"].year, t["date_obj"].month)
            buckets.setdefault(key, {"income": 0.0, "expense": 0.0})
            if t["type"] == "income":
                buckets[key]["income"] += t["amount"]
            else:
                buckets[key]["expense"] += t["amount"]
        return buckets

    def _shift_month(self, year, month, delta):
        total = year * 12 + (month - 1) + delta
        new_year = total // 12
        new_month = total % 12 + 1
        return new_year, new_month

    def _overview_month_buckets(self, window=6):
        buckets = self._get_month_buckets()

        if self.selected_date:
            end_year, end_month = self.selected_date.year, self.selected_date.month
        elif buckets:
            end_year, end_month = sorted(buckets.keys())[-1]
        else:
            end_year, end_month = self.report_year, self.report_month

        months = []
        for offset in range(window - 1, -1, -1):
            y, m = self._shift_month(end_year, end_month, -offset)
            months.append((y, m))

        padded = {m: buckets.get(m, {"income": 0.0, "expense": 0.0}) for m in months}
        return months, padded

    def _format_axis_value(self, value):
        value = float(value)
        abs_val = abs(value)
        if abs_val >= 1_000_000_000:
            return f"{value/1_000_000_000:.1f}B"
        if abs_val >= 1_000_000:
            return f"{value/1_000_000:.1f}M"
        if abs_val >= 1_000:
            return f"{value/1_000:.0f}K"
        return f"{value:.0f}"

    def _recent_transactions(self, limit=6):
        txns = list(self._dashboard_txns())
        txns.sort(key=lambda x: x["date"], reverse=True)
        return txns[:limit]

    def _dates_with_transactions(self, year, month):
        days = set()
        for t in self._all_txns():
            if t["date_obj"].year == year and t["date_obj"].month == month:
                days.add(t["date_obj"].day)
        return days

    def _set_selected_date(self, new_date):
        self.selected_date = new_date
        if new_date:
            self.report_year = new_date.year
            self.report_month = new_date.month
            self.calendar_year = new_date.year
            self.calendar_month = new_date.month
        self.setup_ui()

    def _goto_month_from_report(self):
        self.calendar_year = self.report_year
        self.calendar_month = self.report_month
        self.selected_date = None
        self.active_page = "Calendar"
        self.setup_ui()

    # --------------------------------------------------------
    # Core layout
    # --------------------------------------------------------
    def clear_window(self):
        for child in self.root.winfo_children():
            child.destroy()

    def setup_ui(self):
        self.clear_window()
        self.root.title("TRACKSY")
        self.root.configure(bg=self._c("APP_BG"))
        self.root.geometry("1550x920")
        self.root.minsize(1320, 760)

        shell = tk.Frame(self.root, bg=self._c("APP_BG"))
        shell.pack(fill="both", expand=True)

        self._build_main(shell)

    def _build_main(self, parent):
        container = tk.Frame(parent, bg=self._c("APP_BG"))
        container.pack(fill="both", expand=True, padx=18, pady=12)

        self._build_top_header(container)

        content = tk.Frame(container, bg=self._c("APP_BG"))
        content.pack(fill="both", expand=True, pady=(12, 0))

        self._build_sidebar(content)

        page = tk.Frame(content, bg=self._c("APP_BG"))
        page.pack(side="left", fill="both", expand=True, padx=(18, 0))

        if self.active_page == "Transactions":
            self._build_transactions_page(page)
        elif self.active_page == "Reports":
            self._build_reports_page(page)
        elif self.active_page == "Calendar":
            self._build_calendar_page(page)
        elif self.active_page == "About":
            self._build_about_page(page)
        else:
            self._build_dashboard_page(page)

    def _build_top_header(self, parent):
        top = tk.Frame(parent, bg=self._c("APP_BG"))
        top.pack(fill="x")

        left = tk.Frame(top, bg=self._c("APP_BG"))
        left.pack(side="left")

        tk.Label(
            left,
            text="◪ TRACKSY",
            bg=self._c("APP_BG"),
            fg=self._c("PRIMARY"),
            font=("Segoe UI Symbol", 29, "bold")
        ).pack(anchor="w")
        tk.Label(
            left,
            text="Take control of your finances",
            bg=self._c("APP_BG"),
            fg=self._c("TEXT_SOFT"),
            font=("Segoe UI", 15)
        ).pack(anchor="w", pady=(2, 0))

        right = tk.Frame(top, bg=self._c("APP_BG"))
        right.pack(side="right", pady=6)

        # Dark Mode Toggle Button
        moon_btn = tk.Button(
            right,
            text="🌙" if not self.dark_mode else "☀️",
            command=self.toggle_dark_mode,
            bg=self._c("DARK_BUTTON"),
            fg="white",
            activebackground=self._c("DARK_BUTTON"),
            activeforeground="white",
            font=("Segoe UI", 16),
            relief="flat",
            bd=0,
            width=3,
            height=1,
            cursor="hand2"
        )
        moon_btn.pack(side="right", padx=(10, 0))

        close_btn = tk.Button(
            right,
            text="✕",
            command=self.root.destroy,
            bg=self._c("DARK_BUTTON"),
            fg="white",
            activebackground=self._c("DARK_BUTTON"),
            activeforeground="white",
            font=("Segoe UI", 18, "bold"),
            relief="flat",
            bd=0,
            width=3,
            cursor="hand2"
        )
        close_btn.pack(side="right", padx=10)

        tk.Frame(parent, bg=self._c("BORDER"), height=1).pack(fill="x", pady=(12, 0))

    def _build_sidebar(self, parent):
        
        sidebar_outer = tk.Frame(parent, bg=self._c("SURFACE"), width=250, highlightbackground=self._c("BORDER"), highlightthickness=1)
        sidebar_outer.pack(side="left", fill="y")
        sidebar_outer.pack_propagate(False)

        sb_canvas = tk.Canvas(sidebar_outer, bg=self._c("SURFACE"), highlightthickness=0, bd=0, width=248)
        sb_scroll = ttk.Scrollbar(sidebar_outer, orient="vertical", command=sb_canvas.yview)
        sb_canvas.configure(yscrollcommand=sb_scroll.set)

        sb_scroll.pack(side="right", fill="y")
        sb_canvas.pack(side="left", fill="both", expand=True)

        
        sidebar = tk.Frame(sb_canvas, bg=self._c("SURFACE"))
        sb_win = sb_canvas.create_window((0, 0), window=sidebar, anchor="nw")

        def _sb_configure(event):
            sb_canvas.configure(scrollregion=sb_canvas.bbox("all"))

        def _sb_canvas_configure(event):
            sb_canvas.itemconfig(sb_win, width=event.width)

        sidebar.bind("<Configure>", _sb_configure)
        sb_canvas.bind("<Configure>", _sb_canvas_configure)

        def _sb_mousewheel(event):
            sb_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        sb_canvas.bind_all("<MouseWheel>", _sb_mousewheel)

        # ── Sidebar content ──────────────────────────────────────
        avatar_box = tk.Frame(sidebar, bg=self._c("SURFACE"))
        avatar_box.pack(fill="x", pady=(28, 10))
        avatar = tk.Canvas(avatar_box, width=80, height=80, bg=self._c("SURFACE"), highlightthickness=0)
        avatar.pack()
        avatar.create_oval(6, 6, 74, 74, fill="#4B8BEA", outline="")
        avatar.create_oval(30, 20, 50, 40, fill="white", outline="")
        avatar.create_arc(22, 35, 58, 62, start=0, extent=180, fill="white", outline="white")

        tk.Label(sidebar, text="Welcome!", bg=self._c("SURFACE"), fg=self._c("TEXT"), font=("Segoe UI", 20, "bold")).pack(pady=(4, 6))
        tk.Label(sidebar, text=self.name, bg=self._c("SURFACE"), fg=self._c("TEXT"), font=("Segoe UI", 11, "bold")).pack()
        tk.Label(sidebar, text=self.email, bg=self._c("SURFACE"), fg=self._c("TEXT_SOFT"), font=("Segoe UI", 9)).pack(pady=(2, 18))

        menu = [
            ("Dashboard", "⌂"),
            ("Transactions", "⇄"),
            ("Reports", "◔"),
            ("Calendar", "◷"),
            ("About", "ⓘ"),
        ]
        for page, icon in menu:
            active = self.active_page == page
            bg = self._c("SIDEBAR_ACTIVE") if active else self._c("SURFACE")
            fg = "white" if active else self._c("TEXT")
            btn = tk.Label(
                sidebar,
                text=f" {icon}  {page}",
                bg=bg,
                fg=fg,
                font=("Segoe UI", 14, "bold" if active else "normal"),
                padx=22,
                pady=13,
                anchor="w",
                cursor="hand2",
            )
            btn.pack(fill="x", padx=18, pady=5)
            btn.bind("<Button-1>", lambda e, p=page: self._nav(p))

        shortcut_wrap = tk.Frame(sidebar, bg=self._c("SURFACE"))
        shortcut_wrap.pack(fill="x", padx=18, pady=(22, 10))

        self._action_button(shortcut_wrap, "+ Add Income", self._c("SIDEBAR_ACTIVE"), self.open_income_window).pack(fill="x", pady=4)
        self._action_button(shortcut_wrap, "- Add Expense", "#818CF8", self.open_expense_window).pack(fill="x", pady=4)
        self._action_button(shortcut_wrap, "Export Data", self._c("BORDER"), self._export_current_report_pdf, fg=self._c("TEXT")).pack(fill="x", pady=14)
        self._action_button(shortcut_wrap, "Logout", self._c("DARK_BUTTON"), self.logout).pack(fill="x", pady=4)


    def _action_button(self, parent, text, bg, command, fg="white"):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            relief="flat",
            bd=0,
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=12,
            cursor="hand2",
            highlightthickness=0,
        )
        return btn

    def _nav(self, page):
        self.active_page = page
        if page == "Calendar":
            self.selected_date = None
        self.setup_ui()


    def _rounded_button(self, parent, text, bg, command, fg="white", width=200, height=46, font=("Segoe UI", 11, "bold")):
        wrap = tk.Frame(parent, bg=parent.cget("bg"))
        canvas = tk.Canvas(wrap, width=width, height=height, bg=parent.cget("bg"), highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)

        r = height // 2
        # rounded pill
        canvas.create_oval(0, 0, 2*r, height, fill=bg, outline=bg)
        canvas.create_oval(width-2*r, 0, width, height, fill=bg, outline=bg)
        canvas.create_rectangle(r, 0, width-r, height, fill=bg, outline=bg)
        canvas.create_text(width//2, height//2, text=text, fill=fg, font=font)

        def trigger(event=None):
            command()

        wrap.bind("<Button-1>", trigger)
        canvas.bind("<Button-1>", trigger)
        return wrap

    def _card(self, parent, width=None, height=None, padx=18, pady=16):
        outer = tk.Frame(parent, bg=self._c("SURFACE"), highlightbackground=self._c("BORDER"), highlightthickness=1)
        if width:
            outer.configure(width=width)
            outer.pack_propagate(False)
        if height:
            outer.configure(height=height)
            outer.pack_propagate(False)
        body = tk.Frame(outer, bg=self._c("SURFACE"))
        body.pack(fill="both", expand=True, padx=padx, pady=pady)
        return outer, body

    # --------------------------------------------------------
    # Dashboard page
    # --------------------------------------------------------
    def _build_dashboard_page(self, parent):
        # ── Scrollable wrapper ──────────────────────────────────
        scroll_canvas = tk.Canvas(parent, bg=self._c("APP_BG"), highlightthickness=0, bd=0)
        v_scroll = ttk.Scrollbar(parent, orient="vertical", command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=v_scroll.set)

        v_scroll.pack(side="right", fill="y")
        scroll_canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(scroll_canvas, bg=self._c("APP_BG"))
        inner_window = scroll_canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_inner_configure(event):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))

        def _on_canvas_configure(event):
            scroll_canvas.itemconfig(inner_window, width=event.width)

        inner.bind("<Configure>", _on_inner_configure)
        scroll_canvas.bind("<Configure>", _on_canvas_configure)

        def _on_mousewheel(event):
            scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # All content now goes into `inner` instead of `parent`
        parent = inner
        # ────────────────────────────────────────────────────────

        txns = self._dashboard_txns()
        summary = self._current_summary()
        lifetime_savings = self._lifetime_savings()

        top_filters = tk.Frame(parent, bg=self._c("APP_BG"))
        top_filters.pack(fill="x", pady=(0, 14))

        date_label = "All dates" if self.selected_date is None else self.selected_date.strftime("%d %b %Y")

        date_btn = self._rounded_button(
            top_filters,
            f"{date_label}    ☷",
            SURFACE,
            lambda: self._nav("Calendar"),
            fg=self._c("TEXT"),
            width=126,
            height=44,
            font=("Segoe UI", 11),
        )
        date_btn.pack(side="right")

        stats_row = tk.Frame(parent, bg=self._c("APP_BG"))
        stats_row.pack(fill="x", pady=(0, 16))

        stats = [
            ("Lifetime Savings", lifetime_savings, "Total accumulated savings", SAVINGS, None),
            ("Total Balance", summary["balance"], "↑ 0% from last month", TEXT, None),
            ("Monthly Income", summary["income"], "☷ This month", INCOME, None),
            ("Monthly Expenses", summary["expense"], "☷ This month", EXPENSE, None),
            ("Savings Rate", summary["savings_rate"], "% of income", TEXT, "percent"),
        ]

        for i, (title, value, note, accent, mode) in enumerate(stats):
            card, body = self._card(stats_row)
            card.pack(side="left", fill="both", expand=True, padx=(0 if i == 0 else 12, 0))
            tk.Label(body, text=title, bg=self._c("SURFACE"), fg=self._c("TEXT_SOFT"), font=("Segoe UI", 11)).pack(anchor="w")
            display = f"{value:.1f}%" if mode == "percent" else f"${value:,.2f}"
            tk.Label(body, text=display, bg=self._c("SURFACE"), fg=accent, font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(12, 8))
            tk.Label(body, text=note, bg=self._c("SURFACE"), fg=self._c("INCOME") if "0%" in note else TEXT_SOFT, font=("Segoe UI", 10)).pack(anchor="w")

        mid = tk.Frame(parent, bg=self._c("APP_BG"))
        mid.pack(fill="both", expand=True)

        left_card, left_body = self._card(mid)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 14))
        tk.Label(left_body, text="Spending by Category", bg=self._c("SURFACE"), fg=self._c("PRIMARY"), font=("Segoe UI", 13, "bold")).pack(anchor="w")

        left_content = tk.Frame(left_body, bg=self._c("SURFACE"))
        left_content.pack(fill="both", expand=True, pady=(14, 0))

        donut_canvas = tk.Canvas(left_content, width=520, height=470, bg=self._c("SURFACE"), highlightthickness=0)
        donut_canvas.pack(side="left", fill="both", expand=True)
        self._draw_donut_chart(donut_canvas, self._get_category_data(txns))

        right_card, right_body = self._card(mid, width=520)
        right_card.pack(side="left", fill="both")
        tk.Label(right_body, text="Monthly Overview", bg=self._c("SURFACE"), fg=self._c("PRIMARY"), font=("Segoe UI", 13, "bold")).pack(anchor="w")
        bar_canvas = tk.Canvas(right_body, width=460, height=300, bg=self._c("SURFACE"), highlightthickness=0)
        bar_canvas.pack(fill="x", pady=(16, 0))
        self._draw_monthly_overview(bar_canvas)

        recent_wrap = tk.Frame(right_body, bg=self._c("SURFACE"))
        recent_wrap.pack(fill="both", expand=True, pady=(18, 0))
        tk.Label(recent_wrap, text="Recent Transactions", bg=self._c("SURFACE"), fg=self._c("PRIMARY"), font=("Segoe UI", 12, "bold")).pack(anchor="w")

        recent_host = tk.Frame(recent_wrap, bg=self._c("SURFACE"))
        recent_host.pack(fill="both", expand=True, pady=(8, 0))

        recent_canvas = tk.Canvas(recent_host, bg=self._c("SURFACE"), highlightthickness=0, bd=0, width=430)
        recent_scroll = ttk.Scrollbar(recent_host, orient="vertical", command=recent_canvas.yview)
        recent_canvas.configure(yscrollcommand=recent_scroll.set)
        recent_canvas.pack(side="left", fill="both", expand=True)
        recent_scroll.pack(side="right", fill="y")

        recent_inner = tk.Frame(recent_canvas, bg=self._c("SURFACE"))
        recent_canvas.create_window((0, 0), window=recent_inner, anchor="nw")

        def _recent_cfg(event):
            recent_canvas.configure(scrollregion=recent_canvas.bbox("all"))
        recent_inner.bind("<Configure>", _recent_cfg)

        recent = self._recent_transactions(100)
        if not recent:
            tk.Label(recent_inner, text="No transactions found", bg=self._c("SURFACE"), fg=self._c("TEXT_SOFT"), font=("Segoe UI", 11)).pack(anchor="w", pady=(14, 0))
        else:
            for t in recent:
                row = tk.Frame(recent_inner, bg=self._c("SURFACE"))
                row.pack(fill="x", pady=5)
                left = tk.Frame(row, bg=self._c("SURFACE"))
                left.pack(side="left")
                tk.Label(left, text=t["category"], bg=self._c("SURFACE"), fg=self._c("TEXT"), font=("Segoe UI", 11, "bold")).pack(anchor="w")
                tk.Label(left, text=t["date"], bg=self._c("SURFACE"), fg=self._c("TEXT_SOFT"), font=("Segoe UI", 9)).pack(anchor="w")
                color = INCOME if t["type"] == "income" else EXPENSE
                sign = "+" if t["type"] == "income" else "-"
                tk.Label(row, text=f"{sign}${t['amount']:,.2f}", bg=self._c("SURFACE"), fg=color, font=("Segoe UI", 11, "bold")).pack(side="right")

    # --------------------------------------------------------
    # Transactions page
    # --------------------------------------------------------
    def _build_transactions_page(self, parent):
        header = tk.Frame(parent, bg=self._c("APP_BG"))
        header.pack(fill="x", pady=(0, 14))
        tk.Label(header, text="Transactions", bg=self._c("APP_BG"), fg=self._c("PRIMARY"), font=("Segoe UI", 20, "bold")).pack(side="left")

        controls = tk.Frame(header, bg=self._c("APP_BG"))
        controls.pack(side="right")

        months, years = self._month_year_options()
        month_values = ["All months"] + months
        year_values = ["All years"] + years

        month_combo = ttk.Combobox(controls, textvariable=self.month_filter_var, values=month_values, state="readonly", width=14)
        month_combo.pack(side="left", padx=6)
        year_combo = ttk.Combobox(controls, textvariable=self.year_filter_var, values=year_values, state="readonly", width=10)
        year_combo.pack(side="left", padx=6)
        tk.Button(controls, text="Apply", command=self.setup_ui, bg=self._c("SIDEBAR_ACTIVE"), fg="white", relief="flat", bd=0, padx=16, pady=8, cursor="hand2").pack(side="left", padx=6)
        tk.Button(controls, text="Reset", command=self._reset_transaction_filters, bg="#E5E7EB", fg=self._c("TEXT"), relief="flat", bd=0, padx=16, pady=8, cursor="hand2").pack(side="left", padx=6)

        card, body = self._card(parent)
        card.pack(fill="both", expand=True)

        toolbar = tk.Frame(body, bg=self._c("SURFACE"))
        toolbar.pack(fill="x", pady=(0, 12))
        search = tk.Entry(toolbar, textvariable=self.search_var, font=("Segoe UI", 11), relief="flat", bd=0)
        search.pack(side="left", fill="x", expand=True, ipady=10)
        search.configure(highlightbackground=self._c("BORDER"), highlightthickness=1, bg=self._c("SURFACE_ALT"), insertbackground=self._c("TEXT"))
        tk.Button(toolbar, text="Search", command=self.setup_ui, bg=self._c("SIDEBAR_ACTIVE"), fg="white", relief="flat", bd=0, padx=16, pady=10, cursor="hand2").pack(side="left", padx=10)
        tk.Button(toolbar, text="+ Add Income", command=self.open_income_window, bg=self._c("SIDEBAR_ACTIVE"), fg="white", relief="flat", bd=0, padx=16, pady=10, cursor="hand2").pack(side="left", padx=4)
        tk.Button(toolbar, text="- Add Expense", command=self.open_expense_window, bg="#818CF8", fg="white", relief="flat", bd=0, padx=16, pady=10, cursor="hand2").pack(side="left", padx=4)

        cols = ("Date", "Type", "Category", "Amount")
        tree = ttk.Treeview(body, columns=cols, show="headings", style="Tracker.Treeview")
        for col, width in [("Date", 140), ("Type", 120), ("Category", 240), ("Amount", 150)]:
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(body, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree = tree
        self._load_transactions_tree()

    def _reset_transaction_filters(self):
        self.search_var.set("")
        self.month_filter_var.set("All months")
        self.year_filter_var.set("All years")
        self.selected_date = None
        self.setup_ui()

    def _load_transactions_tree(self):
        if not hasattr(self, "tree"):
            return
        for row in self.tree.get_children():
            self.tree.delete(row)
        for t in reversed(self._filtered_txns()):
            self.tree.insert(
                "",
                "end",
                values=(
                    t["date"],
                    t["type"].title(),
                    t["category"],
                    f"${t['amount']:,.2f}",
                ),
            )

    # --------------------------------------------------------
    # Reports page
    # --------------------------------------------------------
    def _build_reports_page(self, parent):
        header = tk.Frame(parent, bg=self._c("APP_BG"))
        header.pack(fill="x", pady=(0, 14))
        tk.Label(header, text="Monthly Reports", bg=self._c("APP_BG"), fg=self._c("PRIMARY"), font=("Segoe UI", 20, "bold")).pack(side="left")

        controls = tk.Frame(header, bg=self._c("APP_BG"))
        controls.pack(side="right")

        month_var = tk.StringVar(value=calendar.month_name[self.report_month])
        year_var = tk.StringVar(value=str(self.report_year))

        month_combo = ttk.Combobox(controls, textvariable=month_var, values=[calendar.month_name[i] for i in range(1, 13)], state="readonly", width=14)
        month_combo.pack(side="left", padx=6)
        year_values = sorted({str(t["date_obj"].year) for t in self._all_txns()} | {str(date.today().year)})
        year_combo = ttk.Combobox(controls, textvariable=year_var, values=year_values, state="readonly", width=10)
        year_combo.pack(side="left", padx=6)

        def apply_report_month():
            self.report_month = list(calendar.month_name).index(month_var.get())
            self.report_year = int(year_var.get())
            self.selected_date = None
            self.setup_ui()

        tk.Button(controls, text="Apply", command=apply_report_month, bg=self._c("SIDEBAR_ACTIVE"), fg="white", relief="flat", bd=0, padx=16, pady=8, cursor="hand2").pack(side="left", padx=6)
        tk.Button(controls, text="Open Calendar", command=self._goto_month_from_report, bg="#E5E7EB", fg=self._c("TEXT"), relief="flat", bd=0, padx=16, pady=8, cursor="hand2").pack(side="left", padx=6)
        tk.Button(controls, text="Download PDF", command=self._export_current_report_pdf, bg=self._c("DARK_BUTTON"), fg="white", relief="flat", bd=0, padx=16, pady=8, cursor="hand2").pack(side="left", padx=6)

        txns = self._transactions_for_selected_month()
        summary = self._month_summary(txns)
        lifetime_savings = self._lifetime_savings()

        summary_row = tk.Frame(parent, bg=self._c("APP_BG"))
        summary_row.pack(fill="x", pady=(0, 16))
        for i, (title, value, color, suffix) in enumerate([
            ("Lifetime Savings", lifetime_savings, SAVINGS, "$"),
            ("Income", summary["income"], INCOME, "$"),
            ("Expenses", summary["expense"], EXPENSE, "$"),
            ("Net", summary["balance"], PRIMARY, "$"),
            ("Savings Rate", summary["savings_rate"], SAVINGS, "%"),
        ]):
            card, body = self._card(summary_row)
            card.pack(side="left", fill="both", expand=True, padx=(0 if i == 0 else 12, 0))
            tk.Label(body, text=title, bg=self._c("SURFACE"), fg=self._c("TEXT_SOFT"), font=("Segoe UI", 11)).pack(anchor="w")
            disp = f"{value:,.1f}%" if suffix == "%" else f"${value:,.2f}"
            tk.Label(body, text=disp, bg=self._c("SURFACE"), fg=color, font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(12, 0))

        content = tk.Frame(parent, bg=self._c("APP_BG"))
        content.pack(fill="both", expand=True)

        left_card, left_body = self._card(content)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 14))
        tk.Label(left_body, text=f"Report for {calendar.month_name[self.report_month]} {self.report_year}", bg=self._c("SURFACE"), fg=self._c("PRIMARY"), font=("Segoe UI", 14, "bold")).pack(anchor="w")
        report_text = tk.Text(left_body, height=12, wrap="word", bg=self._c("SURFACE_ALT"), fg=self._c("TEXT"), relief="flat", font=("Segoe UI", 11))
        report_text.pack(fill="both", expand=True, pady=(14, 0))
        report_text.insert("1.0", self._build_monthly_report_text(txns, summary))
        report_text.configure(state="disabled")

        right_card, right_body = self._card(content, width=460)
        right_card.pack(side="left", fill="both")
        tk.Label(right_body, text="Expense Breakdown", bg=self._c("SURFACE"), fg=self._c("PRIMARY"), font=("Segoe UI", 13, "bold")).pack(anchor="w")
        chart = tk.Canvas(right_body, width=400, height=280, bg=self._c("SURFACE"), highlightthickness=0)
        chart.pack(fill="x", pady=(12, 0))
        self._draw_donut_chart(chart, self._get_category_data(txns), small=True)

        tk.Label(right_body, text="Transactions in selected report month", bg=self._c("SURFACE"), fg=self._c("TEXT_SOFT"), font=("Segoe UI", 10)).pack(anchor="w", pady=(12, 8))
        list_box = tk.Frame(right_body, bg=self._c("SURFACE"))
        list_box.pack(fill="both", expand=True)
        if not txns:
            tk.Label(list_box, text="No data for this month", bg=self._c("SURFACE"), fg=self._c("TEXT_SOFT"), font=("Segoe UI", 11)).pack(anchor="w")
        else:
            for t in txns[:8]:
                row = tk.Frame(list_box, bg=self._c("SURFACE"))
                row.pack(fill="x", pady=4)
                tk.Label(row, text=f"{t['date']}  ·  {t['category']}", bg=self._c("SURFACE"), fg=self._c("TEXT"), font=("Segoe UI", 10)).pack(side="left")
                col = INCOME if t["type"] == "income" else EXPENSE
                sign = "+" if t["type"] == "income" else "-"
                tk.Label(row, text=f"{sign}${t['amount']:,.2f}", bg=self._c("SURFACE"), fg=col, font=("Segoe UI", 10, "bold")).pack(side="right")

    def _build_monthly_report_text(self, txns, summary):
        category_data = self._get_category_data(txns)
        month_name = calendar.month_name[self.report_month]
        total_transactions = len(txns)
        top_category = category_data[0][0] if category_data else "None"
        top_category_amount = category_data[0][1] if category_data else 0
        lifetime_savings = self._lifetime_savings()
        report_lines = [
            f"Monthly Financial Report — {month_name} {self.report_year}",
            "",
            f"Lifetime Total Savings: ${lifetime_savings:,.2f}",
            f"Total income: ${summary['income']:,.2f}",
            f"Total expenses: ${summary['expense']:,.2f}",
            f"Net balance: ${summary['balance']:,.2f}",
            f"Savings rate: {summary['savings_rate']:.1f}%",
            f"Number of transactions: {total_transactions}",
            "",
            "Highlights:",
            f"• Highest spending category: {top_category} (${top_category_amount:,.2f})",
            f"• Report month synced with calendar: {month_name} {self.report_year}",
            f"• Report uses the same transaction dates shown in the calendar and dashboard overview.",
            "",
            "Category breakdown:",
        ]
        if category_data:
            total_expense = summary["expense"] or 1
            for name, amount in category_data:
                report_lines.append(f"• {name}: ${amount:,.2f} ({amount / total_expense * 100:.1f}%)")
        else:
            report_lines.append("• No expense data available for this month.")
        return "\n".join(report_lines)

    def _export_current_report_pdf(self):
        txns = self._transactions_for_selected_month()
        summary = self._month_summary(txns)
        lifetime_savings = self._lifetime_savings()
        default_name = f"monthly_report_{self.report_year}_{self.report_month:02d}.pdf"
        path = filedialog.asksaveasfilename(
            title="Save monthly report",
            defaultextension=".pdf",
            initialfile=default_name,
            filetypes=[("PDF Files", "*.pdf")],
        )
        if not path:
            return
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror("Export Error", "PDF export is not available because reportlab is not installed.")
            return

        try:
            pdf = pdf_canvas.Canvas(path, pagesize=A4)
            width, height = A4
            y = height - 50

            pdf.setTitle("Monthly Financial Report")
            pdf.setFont("Helvetica-Bold", 18)
            pdf.setFillColor(colors.HexColor(PRIMARY))
            pdf.drawString(50, y, "Monthly Financial Report")
            y -= 30

            pdf.setFont("Helvetica", 12)
            pdf.setFillColor(colors.black)
            pdf.drawString(50, y, f"User: {self.name} ({self.email})")
            y -= 20
            pdf.drawString(50, y, f"Period: {calendar.month_name[self.report_month]} {self.report_year}")
            y -= 28

            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(50, y, f"Lifetime Total Savings: ${lifetime_savings:,.2f}")
            y -= 18
            pdf.drawString(50, y, f"Income: ${summary['income']:,.2f}")
            y -= 18
            pdf.drawString(50, y, f"Expenses: ${summary['expense']:,.2f}")
            y -= 18
            pdf.drawString(50, y, f"Net Balance: ${summary['balance']:,.2f}")
            y -= 18
            pdf.drawString(50, y, f"Savings Rate: {summary['savings_rate']:.1f}%")
            y -= 30

            pdf.setFont("Helvetica-Bold", 13)
            pdf.drawString(50, y, "Transactions")
            y -= 20
            pdf.setFont("Helvetica", 10)

            for t in txns:
                line = f"{t['date']}   {t['type'].title()}   {t['category']}   ${t['amount']:,.2f}"
                pdf.drawString(50, y, line[:110])
                y -= 16
                if y < 70:
                    pdf.showPage()
                    y = height - 50
                    pdf.setFont("Helvetica", 10)

            y -= 10
            if y < 120:
                pdf.showPage()
                y = height - 50
            pdf.setFont("Helvetica-Bold", 13)
            pdf.drawString(50, y, "Summary")
            y -= 20
            pdf.setFont("Helvetica", 11)
            for line in self._build_monthly_report_text(txns, summary).splitlines():
                pdf.drawString(50, y, line[:110])
                y -= 16
                if y < 70:
                    pdf.showPage()
                    y = height - 50
                    pdf.setFont("Helvetica", 11)

            pdf.save()
            messagebox.showinfo("Export Complete", f"Monthly report saved successfully.\n\n{os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not create PDF.\n\n{e}")

    # --------------------------------------------------------
    # Calendar page
    # --------------------------------------------------------
    def _build_calendar_page(self, parent):
        header = tk.Frame(parent, bg=self._c("APP_BG"))
        header.pack(fill="x", pady=(0, 14))
        tk.Label(header, text="Calendar", bg=self._c("APP_BG"), fg=self._c("PRIMARY"), font=("Segoe UI", 20, "bold")).pack(side="left")

        nav = tk.Frame(header, bg=self._c("APP_BG"))
        nav.pack(side="right")

        def prev_month():
            self.calendar_year, self.calendar_month = self._shift_month(self.calendar_year, self.calendar_month, -1)
            self.setup_ui()

        def next_month():
            self.calendar_year, self.calendar_month = self._shift_month(self.calendar_year, self.calendar_month, 1)
            self.setup_ui()

        tk.Button(nav, text="◀", command=prev_month, bg=self._c("DARK_BUTTON"), fg="white", relief="flat", bd=0, width=4, cursor="hand2").pack(side="left", padx=4)
        month_year_label = tk.Label(nav, text=f"{calendar.month_name[self.calendar_month]} {self.calendar_year}", bg=self._c("APP_BG"), fg=self._c("TEXT"), font=("Segoe UI", 13, "bold"))
        month_year_label.pack(side="left", padx=12)
        tk.Button(nav, text="▶", command=next_month, bg=self._c("DARK_BUTTON"), fg="white", relief="flat", bd=0, width=4, cursor="hand2").pack(side="left", padx=4)

        card, body = self._card(parent)
        card.pack(fill="x", padx=(0, 0))

        # ── Days of week ────────────────────────────────────────
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day in weekdays:
            tk.Label(body, text=day, bg=self._c("SURFACE"), fg=self._c("TEXT_SOFT"), font=("Segoe UI", 10, "bold")).pack(side="left", fill="x", expand=True, padx=6, pady=(8, 12))

        # ── Calendar cells ──────────────────────────────────────
        cal = calendar.monthcalendar(self.calendar_year, self.calendar_month)
        txn_days = self._dates_with_transactions(self.calendar_year, self.calendar_month)

        for week in cal:
            week_frame = tk.Frame(body, bg=self._c("SURFACE"))
            week_frame.pack(fill="x", padx=(4, 4), pady=4)
            for day in week:
                if day == 0:
                    cell = tk.Frame(week_frame, bg=self._c("SURFACE"))
                else:
                    is_selected = self.selected_date and self.selected_date.day == day and self.selected_date.month == self.calendar_month and self.selected_date.year == self.calendar_year
                    has_txn = day in txn_days
                    
                    if is_selected:
                        bg = self._c("PRIMARY")
                        fg = "white"
                        border = self._c("PRIMARY")
                    elif has_txn:
                        bg = self._c("SURFACE_ALT")
                        fg = self._c("CAL_DOT")
                        border = self._c("CAL_DOT")
                    else:
                        bg = self._c("SURFACE_ALT")
                        fg = self._c("TEXT")
                        border = self._c("BORDER")
                    
                    cell = tk.Frame(week_frame, bg=bg, highlightbackground=border, highlightthickness=2 if (is_selected or has_txn) else 0)
                    cell.bind("<Button-1>", lambda e, d=day: self._set_selected_date(date(self.calendar_year, self.calendar_month, d)))
                    cell.configure(cursor="hand2")
                    day_label = tk.Label(
                        cell,
                        text=str(day),
                        bg=bg,
                        fg=fg,
                        font=("Segoe UI", 12, "bold"),
                        cursor="hand2"
                    )
                    day_label.pack(padx=8, pady=6)

                    for widget in (cell, day_label):
                        widget.bind(
                            "<Button-1>",
                            lambda e, d=day: self._set_selected_date(
                                date(self.calendar_year, self.calendar_month, d)
                            )
                        )
                cell.pack(side="left", fill="both", expand=True, padx=2, pady=2)

        info_frame = tk.Frame(parent, bg=self._c("APP_BG"))
        info_frame.pack(fill="x", pady=(10, 0))
        tk.Label(info_frame, text="◆ Dates with transactions", bg=self._c("APP_BG"), fg=self._c("CAL_DOT"), font=("Segoe UI", 10)).pack(anchor="w")

    # --------------------------------------------------------
    # About page
    # --------------------------------------------------------
    def _build_about_page(self, parent):
        card, body = self._card(parent)
        card.pack(fill="both", expand=True)

        tk.Label(body, text="About TRACKSY", bg=self._c("SURFACE"), fg=self._c("PRIMARY"), font=("Segoe UI", 20, "bold")).pack(anchor="w")

        text = """
TRACKSY is a modern finance dashboard designed to help you:

• Track income and expenses with ease
• Analyze spending patterns by category
• Monitor your financial health with key metrics
• Generate detailed monthly reports
• Export your financial data

Version: 1.0
Theme: Light Mode

Features:
• Real-time transaction logging
• Monthly financial summaries
• Category-based expense breakdown
• PDF report generation
• Calendar-based transaction view
• Lifetime savings tracking

Built with Python and Tkinter for a clean, responsive experience.

Start tracking your finances today and take control of your money!
        """
        tk.Label(body, text=text, justify="left", bg=self._c("SURFACE"), fg=self._c("TEXT"), font=("Segoe UI", 12)).pack(anchor="w", pady=(16, 0))

    # --------------------------------------------------------
    # Dialogs
    # --------------------------------------------------------
    def open_income_window(self):
        self._open_transaction_window("income")

    def open_expense_window(self):
        self._open_transaction_window("expense")

    def _open_transaction_window(self, mode):
        title = "Add Income" if mode == "income" else "Add Expense"
        accent = SIDEBAR_ACTIVE if mode == "income" else "#818CF8"

        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("460x440" if mode == "income" else "460x520")
        win.configure(bg=self._c("SURFACE"))
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        body = tk.Frame(win, bg=self._c("SURFACE"))
        body.pack(fill="both", expand=True, padx=24, pady=(24, 10))

        footer = tk.Frame(win, bg=self._c("SURFACE"))
        footer.pack(fill="x", side="bottom", padx=24, pady=(0, 24))

        tk.Label(body, text=title, bg=self._c("SURFACE"), fg=accent, font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tk.Label(body, text="Enter details below", bg=self._c("SURFACE"), fg=self._c("TEXT_SOFT"), font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 18))

        tk.Label(body, text="Amount", bg=self._c("SURFACE"), fg=self._c("TEXT"), font=("Segoe UI", 11, "bold")).pack(anchor="w")
        amount_entry = tk.Entry(body, font=("Segoe UI", 16), relief="flat", bd=0, bg=self._c("SURFACE_ALT"))
        amount_entry.pack(fill="x", ipady=10, pady=(8, 14))
        amount_entry.configure(highlightbackground=self._c("BORDER"), highlightthickness=1)
        amount_entry.focus()

        if mode == "expense":
            tk.Label(body, text="Category", bg=self._c("SURFACE"), fg=self._c("TEXT"), font=("Segoe UI", 11, "bold")).pack(anchor="w")
            categories = ["Food", "Transportation", "Housing", "Entertainment", "Shopping", "Bills", "Health", "Utilities", "Other"]
            category_var = tk.StringVar(value=categories[0])
            category_combo = ttk.Combobox(
                body,
                textvariable=category_var,
                values=categories,
                state="readonly",
                font=("Segoe UI", 11)
            )
            category_combo.pack(fill="x", pady=(8, 14), ipady=6)
        else:
            category_var = tk.StringVar(value="Income")

        tk.Label(body, text="Date (YYYY-MM-DD)", bg=self._c("SURFACE"), fg=self._c("TEXT"), font=("Segoe UI", 11, "bold")).pack(anchor="w")
        date_entry = tk.Entry(body, font=("Segoe UI", 14), relief="flat", bd=0, bg=self._c("SURFACE_ALT"))
        date_entry.pack(fill="x", ipady=10, pady=(8, 14))
        date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        date_entry.configure(highlightbackground=self._c("BORDER"), highlightthickness=1)

        def save():
            try:
                amount = float(amount_entry.get().strip())
                if amount <= 0:
                    raise ValueError
                chosen_date = datetime.strptime(date_entry.get().strip(), "%Y-%m-%d").strftime("%Y-%m-%d")
            except Exception:
                messagebox.showerror("Invalid input", "Please enter a valid amount and date in YYYY-MM-DD format.")
                return

            category = category_var.get().strip() or ("Income" if mode == "income" else "Other")
            if mode == "income":
                category = "Income"

            try:
                self.db.add_transaction(self.email, amount, category, mode, chosen_date)
            except Exception as e:
                messagebox.showerror("Save failed", f"Could not save transaction.\n\n{e}")
                return

            self.selected_date = datetime.strptime(chosen_date, "%Y-%m-%d").date()
            self.report_year = self.selected_date.year
            self.report_month = self.selected_date.month
            self.calendar_year = self.selected_date.year
            self.calendar_month = self.selected_date.month
            win.destroy()
            self.setup_ui()
            messagebox.showinfo("Saved", f"{title} saved successfully.")

        tk.Button(
            footer,
            text="Cancel",
            command=win.destroy,
            bg="#E5E7EB",
            fg=self._c("TEXT"),
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2"
        ).pack(side="right", padx=(10, 0))

        tk.Button(
            footer,
            text=title,
            command=save,
            bg=accent,
            fg="white",
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2"
        ).pack(side="right")

    # --------------------------------------------------------
    # Drawing helpers
    # --------------------------------------------------------
    def _draw_donut_chart(self, canvas, category_data, small=False):
        canvas.delete("all")
        w = int(canvas.cget("width"))
        h = int(canvas.cget("height"))
        cx = 220 if not small else 150
        cy = h // 2 + (10 if not small else 0)
        outer = 170 if not small else 105
        inner = 82 if not small else 52

        if not category_data:
            canvas.create_oval(cx - outer, cy - outer, cx + outer, cy + outer, fill="#EDF2FF", outline="")
            canvas.create_oval(cx - inner, cy - inner, cx + inner, cy + inner, fill=self._c("SURFACE"), outline="")
            canvas.create_text(cx, cy - 10, text="$0.00", fill=self._c("TEXT"), font=("Segoe UI", 18, "bold"))
            canvas.create_text(cx, cy + 14, text="No expenses", fill=self._c("TEXT_SOFT"), font=("Segoe UI", 11))
            return

        total = sum(v for _, v in category_data)
        start = 90
        for i, (name, amount) in enumerate(category_data):
            extent = (amount / total) * 360 if total else 0
            color = CATEGORY_COLORS[i % len(CATEGORY_COLORS)]
            canvas.create_arc(
                cx - outer, cy - outer, cx + outer, cy + outer,
                start=start, extent=extent, fill=color, outline=self._c("SURFACE"), width=2
            )
            start += extent
        canvas.create_oval(cx - inner, cy - inner, cx + inner, cy + inner, fill=self._c("SURFACE"), outline=self._c("SURFACE"))

        if not small:
            legend_x = 400
            legend_y = 180
            canvas.create_text(cx, cy - 8, text=f"${total:,.0f}", fill=self._c("TEXT"), font=("Segoe UI", 19, "bold"))
            canvas.create_text(cx, cy + 18, text="Expenses", fill=self._c("TEXT_SOFT"), font=("Segoe UI", 11))
            for i, (name, amount) in enumerate(category_data[:7]):
                y = legend_y + i * 34
                color = CATEGORY_COLORS[i % len(CATEGORY_COLORS)]
                canvas.create_rectangle(legend_x, y, legend_x + 18, y + 18, fill=color, outline="")
                canvas.create_text(legend_x + 28, y + 9, text=name, anchor="w", fill=self._c("TEXT_SOFT"), font=("Segoe UI", 11))
        else:
            canvas.create_text(cx, cy - 8, text=f"${total:,.0f}", fill=self._c("TEXT"), font=("Segoe UI", 14, "bold"))
            canvas.create_text(cx, cy + 14, text="Expenses", fill=self._c("TEXT_SOFT"), font=("Segoe UI", 10))

    def _draw_monthly_overview(self, canvas):
        canvas.delete("all")
        w = int(canvas.cget("width"))
        h = int(canvas.cget("height"))
        months, buckets = self._overview_month_buckets(6)

        left = 64
        right = w - 20
        top = 36
        bottom = h - 46

        canvas.create_rectangle(w - 190, 8, w - 150, 22, fill=self._c("INCOME"), outline="")
        canvas.create_text(w - 144, 15, text="Income", anchor="w", fill=self._c("TEXT_SOFT"), font=("Segoe UI", 10))
        canvas.create_rectangle(w - 90, 8, w - 50, 22, fill=self._c("EXPENSE"), outline="")
        canvas.create_text(w - 44, 15, text="Expenses", anchor="w", fill=self._c("TEXT_SOFT"), font=("Segoe UI", 10))

        values = [max(buckets[m]["income"], buckets[m]["expense"]) for m in months]
        max_val = max(values) if values else 0
        if max_val <= 0:
            max_val = 1

        for i in range(6):
            y = top + i * ((bottom - top) / 5)
            canvas.create_line(left, y, right, y, fill="#E5E7EB")
            value = max_val - (max_val / 5) * i
            canvas.create_text(left - 10, y, text=self._format_axis_value(value), anchor="e", fill=self._c("TEXT_SOFT"), font=("Segoe UI", 9))

        chart_w = right - left
        step = chart_w / max(len(months), 1)

        for idx, key in enumerate(months):
            x_center = left + step * idx + step / 2
            income_val = buckets[key]["income"]
            expense_val = buckets[key]["expense"]
            income_h = (income_val / max_val) * (bottom - top)
            expense_h = (expense_val / max_val) * (bottom - top)

            canvas.create_rectangle(x_center - 26, bottom - income_h, x_center - 2, bottom, fill=self._c("INCOME"), outline="")
            canvas.create_rectangle(x_center + 2, bottom - expense_h, x_center + 26, bottom, fill=self._c("EXPENSE"), outline="")
            canvas.create_text(x_center, bottom + 18, text=f"{calendar.month_abbr[key[1]]} {str(key[0])[-2:]}", fill=self._c("TEXT_SOFT"), font=("Segoe UI", 10))

    def logout(self):
        self.on_logout()