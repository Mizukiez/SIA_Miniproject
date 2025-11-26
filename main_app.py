# main_app.py
import tkinter as tk
from tkinter import messagebox
import theme
import db

# --- IMPORTS ---
# Movies and Music are imported from the main folder (Unchanged)
import movies_app
import music_app

# Games are now imported from the new "games" folder
from games.games_app import GamesApp


class MainApp:
    def __init__(self, root, user_row):
        self.root = root
        self.user = user_row
        self.root.geometry("1200x800")
        self.root.configure(bg=theme.BG_COLOR)
        self.root.title(f"Entertainment Hub")

        self.main_frame = tk.Frame(self.root, bg=theme.BG_COLOR)
        self.main_frame.pack(fill="both", expand=True)

        self.show_main_menu()

    def show_main_menu(self):
        for w in self.main_frame.winfo_children(): w.destroy()

        # --- HEADER ---
        header = tk.Frame(self.main_frame, bg=theme.BG_COLOR)
        header.pack(fill="x", pady=40, padx=40)

        # Welcome Text
        tk.Label(header, text=f"Welcome back, {self.user['username']}", font=theme.FONT_TITLE,
                 bg=theme.BG_COLOR, fg=theme.TEXT_COLOR).pack(anchor="w")
        tk.Label(header, text="Select an app to launch", font=("Segoe UI", 12),
                 bg=theme.BG_COLOR, fg=theme.SUBTEXT_COLOR).pack(anchor="w")

        # Logout Button
        tk.Button(header, text="Log Out", bg="#fee2e2", fg="#b91c1c", relief="flat", padx=15, pady=5,
                  font=("Segoe UI", 10, "bold"), cursor="hand2",
                  command=self.logout).place(relx=1.0, rely=0.1, anchor="ne")

        # --- APPS GRID ---
        grid_frame = tk.Frame(self.main_frame, bg=theme.BG_COLOR)
        grid_frame.pack(expand=True, pady=20)

        apps = [
            # 1. Music (Original File)
            {"name": "Music & Audio", "icon": "🎵",
             "cmd": lambda: self.open_app(music_app.MusicApp),
             "color": "#ecfdf5"},

            # 2. Movies (Original File)
            {"name": "Movies & TV", "icon": "🎬",
             "cmd": lambda: self.open_app(movies_app.MoviesApp),
             "color": "#eff6ff"},

            # 3. Games (NEW Folder Import)
            {"name": "Arcade Center", "icon": "🕹️",
             "cmd": lambda: self.open_app(GamesApp),
             "color": "#f5f3ff"}
        ]

        for i, app in enumerate(apps):
            self.create_app_card(grid_frame, app, i)

    def create_app_card(self, parent, app, col):
        card = tk.Frame(parent, bg=theme.CARD_COLOR, width=260, height=220,
                        highlightbackground=theme.BORDER_COLOR, highlightthickness=1)
        card.grid(row=0, column=col, padx=25, pady=25)
        card.pack_propagate(False)

        def on_enter(e):
            card.config(bg=app.get("color", theme.HOVER_COLOR))

        def on_leave(e):
            card.config(bg=theme.CARD_COLOR)

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        content_box = tk.Frame(card, bg=theme.CARD_COLOR)
        content_box.place(relx=0.5, rely=0.5, anchor="center")

        icon = tk.Label(content_box, text=app['icon'], font=("Segoe UI", 45),
                        bg=theme.CARD_COLOR, fg=theme.TEXT_COLOR)
        icon.pack(pady=(0, 15))

        title = tk.Label(content_box, text=app['name'], font=("Segoe UI", 13, "bold"),
                         bg=theme.CARD_COLOR, fg=theme.TEXT_COLOR)
        title.pack()

        lbl_btn = tk.Label(content_box, text="Open App →", font=("Segoe UI", 9),
                           bg=theme.CARD_COLOR, fg=theme.ACCENT_COLOR, pady=10)
        lbl_btn.pack()

        def propagate_hover(bg_col):
            card.config(bg=bg_col)
            content_box.config(bg=bg_col)
            icon.config(bg=bg_col)
            title.config(bg=bg_col)
            lbl_btn.config(bg=bg_col)

        card.bind("<Enter>", lambda e: propagate_hover(app.get("color", theme.HOVER_COLOR)))
        card.bind("<Leave>", lambda e: propagate_hover(theme.CARD_COLOR))

        for widget in [card, content_box, icon, title, lbl_btn]:
            widget.bind("<Button-1>", lambda e: app['cmd']())

    def open_app(self, AppClass):
        for w in self.main_frame.winfo_children(): w.destroy()

        nav = tk.Frame(self.main_frame, bg="white", height=60,
                       highlightbackground=theme.BORDER_COLOR, highlightthickness=1)
        nav.pack(fill="x")
        nav.pack_propagate(False)

        tk.Button(nav, text="⬅ Dashboard", bg="white", fg=theme.TEXT_COLOR, relief="flat",
                  font=("Segoe UI", 11), command=self.show_main_menu, cursor="hand2").pack(side="left", padx=20,
                                                                                           pady=15)

        app_container = tk.Frame(self.main_frame, bg=theme.BG_COLOR)
        app_container.pack(fill="both", expand=True, padx=20, pady=20)

        AppClass(app_container, self.user)

    def logout(self):
        for w in self.root.winfo_children(): w.destroy()
        from login import LoginWindow
        LoginWindow(self.root)