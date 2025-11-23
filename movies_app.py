# movies_app.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os, db
import theme
import api_services  # <--- NEW IMPORT

# CONFIGURATION
IMAGE_SAVE_DIR = "downloaded_posters"
if not os.path.exists(IMAGE_SAVE_DIR): os.makedirs(IMAGE_SAVE_DIR)

class MoviesApp:
    def __init__(self, parent, user_row):
        self.parent = parent
        self.user = user_row
        self.setup_ui()

    def setup_ui(self):
        # --- TOP SEARCH BAR ---
        top_bar = tk.Frame(self.parent, bg=theme.BG_COLOR)
        top_bar.pack(fill="x", padx=30, pady=20)

        self.search_var = tk.StringVar()
        entry_frame = tk.Frame(top_bar, bg=theme.INPUT_BG, highlightbackground=theme.BORDER_COLOR, highlightthickness=1)
        entry_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        entry = tk.Entry(entry_frame, textvariable=self.search_var, font=("Segoe UI", 11),
                         bg=theme.INPUT_BG, fg=theme.TEXT_COLOR, insertbackground=theme.TEXT_COLOR, relief="flat")
        entry.pack(fill="x", padx=10, ipady=8)
        entry.bind("<Return>", lambda e: self.refresh_grid())

        btn_style = {"font": ("Segoe UI", 10, "bold"), "relief": "flat", "padx": 15, "pady": 5}
        tk.Button(top_bar, text="🔍 Search", bg=theme.ACCENT_COLOR, fg="white",
                  command=self.refresh_grid, **btn_style).pack(side="left", padx=5)
        tk.Button(top_bar, text="☁ Add Online", bg="#e0e7ff", fg="#4338ca",
                  command=self.open_api_search_dialog, **btn_style).pack(side="left", padx=5)
        tk.Button(top_bar, text="+ Manual", bg="white", fg=theme.TEXT_COLOR,
                  command=self.add_movie_dialog, **btn_style).pack(side="left", padx=5)

        # --- SCROLLABLE GRID ---
        self.canvas = tk.Canvas(self.parent, bg=theme.BG_COLOR, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.parent, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=theme.BG_COLOR)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=30, pady=(0, 30))
        self.scrollbar.pack(side="right", fill="y")
        self.refresh_grid()

    def refresh_grid(self):
        for w in self.scrollable_frame.winfo_children(): w.destroy()
        query = self.search_var.get().strip()
        movies = db.list_movies(query)

        cols = 5
        row, col = 0, 0
        for m in movies:
            self.create_movie_card(m, row, col)
            col += 1
            if col >= cols: col = 0; row += 1

    def create_movie_card(self, movie, r, c):
        card = tk.Frame(self.scrollable_frame, bg=theme.CARD_COLOR, width=160, height=270,
                        highlightbackground=theme.BORDER_COLOR, highlightthickness=1)
        card.grid(row=r, column=c, padx=10, pady=10)
        card.pack_propagate(False)

        img_path = movie.get("image_path")
        tk_img = None
        if img_path and os.path.exists(img_path):
            try:
                i = Image.open(img_path)
                i.thumbnail((140, 210))
                tk_img = ImageTk.PhotoImage(i)
            except: pass

        img_lbl = tk.Label(card, bg=theme.CARD_COLOR)
        if tk_img:
            img_lbl.config(image=tk_img)
            img_lbl.image = tk_img
        else:
            img_lbl.config(text="No Image", fg="#ccc", font=("Segoe UI", 8))
        img_lbl.pack(pady=10)

        title = movie['title']
        if len(title) > 18: title = title[:16] + "..."
        tk.Label(card, text=title, font=("Segoe UI", 10, "bold"), bg=theme.CARD_COLOR, fg=theme.TEXT_COLOR).pack()

        tk.Button(card, text="Details", bg=theme.BG_COLOR, fg=theme.TEXT_COLOR, relief="flat", font=("Segoe UI", 8),
                  command=lambda: self.show_details(movie)).pack(side="bottom", fill="x", pady=5, padx=5)

    def show_details(self, mov):
        top = tk.Toplevel(self.parent)
        top.title("Movie Details")
        top.configure(bg=theme.BG_COLOR)
        top.geometry("400x500")

        tk.Label(top, text=mov['title'], font=("Segoe UI", 18, "bold"), bg=theme.BG_COLOR, fg=theme.TEXT_COLOR).pack(pady=20)
        tk.Label(top, text=f"Genre: {mov.get('genre')}", font=("Segoe UI", 11), bg=theme.BG_COLOR, fg=theme.SUBTEXT_COLOR).pack()

        btn_frame = tk.Frame(top, bg=theme.BG_COLOR)
        btn_frame.pack(pady=30)

        fav_txt = "★ Remove Favorite" if mov.get("is_favorite") else "☆ Add to Favorites"
        def toggle():
            db.toggle_favorite(mov['id'])
            self.refresh_grid()
            top.destroy()
        tk.Button(btn_frame, text=fav_txt, bg="#fffbeb", fg="#b45309", relief="flat", padx=10, pady=5, command=toggle).pack(fill="x", pady=5)

        def delete():
            if messagebox.askyesno("Confirm", "Delete this movie?"):
                db.delete_movie(mov['id'])
                self.refresh_grid()
                top.destroy()
        tk.Button(btn_frame, text="Delete Movie", bg="#fef2f2", fg="#ef4444", relief="flat", padx=10, pady=5, command=delete).pack(fill="x", pady=5)

    # --- API FUNCTIONS (USING api_services.py) ---
    def open_api_search_dialog(self):
        self.api_dlg = tk.Toplevel(self.parent)
        self.api_dlg.title("Search TMDb")
        self.api_dlg.configure(bg=theme.BG_COLOR)
        self.api_dlg.geometry("500x400")

        f = tk.Frame(self.api_dlg, bg=theme.BG_COLOR)
        f.pack(fill="x", padx=10, pady=10)

        self.api_entry = tk.Entry(f, bg="white", fg=theme.TEXT_COLOR)
        self.api_entry.pack(side="left", fill="x", expand=True)
        self.api_entry.bind("<Return>", lambda e: self.perform_api_search())
        tk.Button(f, text="Search", command=self.perform_api_search).pack(side="left", padx=5)

        self.api_listbox = tk.Listbox(self.api_dlg, bg="white", fg=theme.TEXT_COLOR)
        self.api_listbox.pack(fill="both", expand=True, padx=10)
        tk.Button(self.api_dlg, text="Save Selected", command=self.save_api_selection, bg=theme.ACCENT_COLOR, fg="white").pack(pady=10)
        self.api_results = []

    def perform_api_search(self):
        q = self.api_entry.get().strip()
        if not q: return
        # CLEANER: Call the new API file
        self.api_results = api_services.search_tmdb(q)

        self.api_listbox.delete(0, "end")
        for m in self.api_results:
            self.api_listbox.insert("end", f"{m.get('title')} ({m.get('release_date')})")

    def save_api_selection(self):
        sel = self.api_listbox.curselection()
        if not sel: return
        data = self.api_results[sel[0]]

        # CLEANER: Call the new API file for downloading
        local_path = api_services.download_tmdb_image(data.get('poster_path'), data['id'], IMAGE_SAVE_DIR)

        db.add_movie(data.get('title'), "Imported", local_path, self.user['id'])
        self.api_dlg.destroy()
        self.refresh_grid()

    def add_movie_dialog(self):
        dlg = tk.Toplevel(self.parent)
        dlg.configure(bg=theme.BG_COLOR)
        tk.Label(dlg, text="Title:", bg=theme.BG_COLOR).pack()
        t_e = tk.Entry(dlg); t_e.pack()
        tk.Label(dlg, text="Genre:", bg=theme.BG_COLOR).pack()
        g_e = tk.Entry(dlg); g_e.pack()
        def save():
            if t_e.get():
                db.add_movie(t_e.get(), g_e.get(), None, self.user['id'])
                self.refresh_grid()
                dlg.destroy()
        tk.Button(dlg, text="Save", command=save).pack(pady=10)