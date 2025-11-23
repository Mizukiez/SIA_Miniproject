# music_app.py
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk
from PIL import Image, ImageTk
import requests, pygame, io, os, shutil, time
import db, theme
import api_services # <--- NEW IMPORT

pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
PLAYLIST_IMG_DIR = "playlist_covers"
if not os.path.exists(PLAYLIST_IMG_DIR): os.makedirs(PLAYLIST_IMG_DIR)

class MusicApp:
    def __init__(self, parent, user_row):
        self.parent = parent
        self.user = user_row
        self.current_song_path = None
        self.is_playing = False
        self.song_duration = 30
        self.current_pos = 0
        self.update_loop_id = None
        self.setup_ui()

    def setup_ui(self):
        self.body_frame = tk.Frame(self.parent, bg=theme.BG_COLOR)
        self.body_frame.pack(side="top", fill="both", expand=True)

        self.sidebar = tk.Frame(self.body_frame, bg=theme.SIDEBAR_COLOR, width=240)
        self.sidebar.pack(side="left", fill="y"); self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="LIBRARY", font=("Segoe UI", 9, "bold"), bg=theme.SIDEBAR_COLOR, fg=theme.SUBTEXT_COLOR).pack(anchor="w", padx=20, pady=(30, 10))
        self.create_nav_btn(self.sidebar, "🔍 Search Music", lambda: self.show_view("search"))
        self.create_nav_btn(self.sidebar, "❤️ Favorites", lambda: self.show_view("favorites"))

        tk.Label(self.sidebar, text="PLAYLISTS", font=("Segoe UI", 9, "bold"), bg=theme.SIDEBAR_COLOR, fg=theme.SUBTEXT_COLOR).pack(anchor="w", padx=20, pady=(30, 10))
        self.create_nav_btn(self.sidebar, "➕ Create Playlist", self.create_playlist_flow)
        self.playlist_frame = tk.Frame(self.sidebar, bg=theme.SIDEBAR_COLOR); self.playlist_frame.pack(fill="x", pady=5)
        self.refresh_sidebar_playlists()

        self.content = tk.Frame(self.body_frame, bg=theme.BG_COLOR)
        self.content.pack(side="right", fill="both", expand=True)

        self.player_bar = tk.Frame(self.parent, bg="white", height=90, highlightthickness=1, highlightbackground=theme.BORDER_COLOR)
        self.player_bar.pack(side="bottom", fill="x"); self.player_bar.pack_propagate(False)
        self.setup_player_bar()
        self.show_view("search")

    def setup_player_bar(self):
        self.pb_left = tk.Frame(self.player_bar, bg="white", width=250)
        self.pb_left.pack(side="left", fill="y", padx=10); self.pb_left.pack_propagate(False)
        self.lbl_cover = tk.Label(self.pb_left, bg="white"); self.lbl_cover.pack(side="left", padx=10, pady=10)
        self.info_frame = tk.Frame(self.pb_left, bg="white"); self.info_frame.pack(side="left", pady=20)
        self.lbl_title = tk.Label(self.info_frame, text="No Song Playing", font=("Segoe UI", 10, "bold"), bg="white", fg=theme.TEXT_COLOR, anchor="w"); self.lbl_title.pack(anchor="w")
        self.lbl_artist = tk.Label(self.info_frame, text="--", font=("Segoe UI", 9), bg="white", fg=theme.SUBTEXT_COLOR, anchor="w"); self.lbl_artist.pack(anchor="w")

        self.pb_center = tk.Frame(self.player_bar, bg="white"); self.pb_center.pack(side="left", fill="both", expand=True)
        ctrl_frame = tk.Frame(self.pb_center, bg="white"); ctrl_frame.pack(pady=(10, 0))
        self.btn_play = tk.Button(ctrl_frame, text="▶", font=("Segoe UI", 14), bg="white", bd=0, command=self.toggle_play); self.btn_play.pack(side="left", padx=10)

        slider_frame = tk.Frame(self.pb_center, bg="white"); slider_frame.pack(fill="x", padx=20)
        self.lbl_curr_time = tk.Label(slider_frame, text="0:00", bg="white", fg="#555", font=("Segoe UI", 8)); self.lbl_curr_time.pack(side="left")
        self.seek_var = tk.DoubleVar()
        self.slider = ttk.Scale(slider_frame, from_=0, to=30, orient="horizontal", variable=self.seek_var, command=self.on_seek_drag)
        self.slider.pack(side="left", fill="x", expand=True, padx=10)
        self.slider.bind("<ButtonRelease-1>", self.on_seek_release)
        self.lbl_total_time = tk.Label(slider_frame, text="0:30", bg="white", fg="#555", font=("Segoe UI", 8)); self.lbl_total_time.pack(side="left")

    def create_nav_btn(self, parent, text, command):
        tk.Button(parent, text=text, font=("Segoe UI", 10), anchor="w", bg=theme.SIDEBAR_COLOR, fg=theme.TEXT_COLOR, relief="flat", padx=20, pady=6, cursor="hand2", command=command).pack(fill="x", pady=1)

    # --- API (Refactored) ---
    def search_deezer(self):
        q = self.search_var.get().strip()
        if not q: return
        for w in self.scroll_frame.winfo_children(): w.destroy()

        # Call API Service
        results = api_services.search_deezer(q)

        if results: self.populate_song_list(results)
        else: tk.Label(self.scroll_frame, text="No songs found.", bg="white", fg="red").pack(pady=20)

    # --- PLAYBACK ---
    def play_music(self, song_data):
        self.stop_music()
        url = song_data.get('preview') or song_data.get('preview_path')
        if not url: messagebox.showwarning("Unavailable", "No preview available."); return

        self.lbl_title.config(text=song_data.get('title', 'Unknown')[:25])
        art = song_data.get('artist')
        if isinstance(art, dict): art = art.get('name')
        self.lbl_artist.config(text=art)

        cover_url = None
        if isinstance(song_data.get('album'), dict): cover_url = song_data['album'].get('cover_small')
        else: cover_url = song_data.get('cover_url')

        if cover_url:
            try:
                if cover_url.startswith("http"):
                    d = requests.get(cover_url).content; img = Image.open(io.BytesIO(d))
                else: img = Image.open(cover_url)
                img = img.resize((50, 50)); self.tk_cover = ImageTk.PhotoImage(img); self.lbl_cover.config(image=self.tk_cover)
            except: pass

        try:
            self.current_song_path = f"temp_song_{int(time.time())}.mp3"
            if url.startswith("http"):
                with open(self.current_song_path, 'wb') as f: f.write(requests.get(url).content)
            else: shutil.copy(url, self.current_song_path)
            pygame.mixer.music.load(self.current_song_path)
            pygame.mixer.music.play()
            self.is_playing = True; self.btn_play.config(text="⏸"); self.current_pos = 0; self.update_progress_bar()
        except Exception as e: messagebox.showerror("Playback Error", str(e))

    def stop_music(self):
        pygame.mixer.music.stop(); pygame.mixer.music.unload(); self.is_playing = False; self.btn_play.config(text="▶")
        if self.update_loop_id: self.parent.after_cancel(self.update_loop_id); self.update_loop_id = None
        if self.current_song_path and os.path.exists(self.current_song_path):
            try: os.remove(self.current_song_path)
            except: pass

    def toggle_play(self):
        if not pygame.mixer.music.get_busy() and not self.is_playing: return
        if self.is_playing: pygame.mixer.music.pause(); self.is_playing = False; self.btn_play.config(text="▶")
        else: pygame.mixer.music.unpause(); self.is_playing = True; self.btn_play.config(text="⏸"); self.update_progress_bar()

    def update_progress_bar(self):
        if self.is_playing:
            self.current_pos += 1; self.seek_var.set(self.current_pos)
            mins, secs = divmod(int(self.current_pos), 60); self.lbl_curr_time.config(text=f"{mins}:{secs:02d}")
            if self.current_pos >= self.song_duration: self.stop_music(); self.seek_var.set(0); self.lbl_curr_time.config(text="0:00")
            else: self.update_loop_id = self.parent.after(1000, self.update_progress_bar)

    def on_seek_drag(self, val):
        mins, secs = divmod(int(float(val)), 60); self.lbl_curr_time.config(text=f"{mins}:{secs:02d}")

    def on_seek_release(self, event):
        new_time = self.slider.get()
        if pygame.mixer.music.get_busy() or self.is_playing: pygame.mixer.music.play(start=new_time); self.current_pos = new_time

    # --- UI VIEWS ---
    def create_playlist_flow(self):
        name = simpledialog.askstring("New Playlist", "Enter playlist name:", parent=self.parent)
        if not name: return
        db.create_playlist(name, self.user['id'])
        if messagebox.askyesno("Cover Image", "Add a cover image?"):
            f = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
            if f:
                new_pl = db.get_playlists(self.user['id'])[-1]
                dest = os.path.join(PLAYLIST_IMG_DIR, f"playlist_{new_pl['id']}.jpg")
                try: Image.open(f).convert("RGB").save(dest)
                except: pass
        self.refresh_sidebar_playlists()

    def refresh_sidebar_playlists(self):
        for w in self.playlist_frame.winfo_children(): w.destroy()
        for p in db.get_playlists(self.user['id']):
            row = tk.Frame(self.playlist_frame, bg=theme.SIDEBAR_COLOR, cursor="hand2"); row.pack(fill="x", pady=2, padx=10)
            img_path = os.path.join(PLAYLIST_IMG_DIR, f"playlist_{p['id']}.jpg")
            if os.path.exists(img_path):
                img = Image.open(img_path).resize((30, 30)); tk_img = ImageTk.PhotoImage(img)
                lbl = tk.Label(row, image=tk_img, bg=theme.SIDEBAR_COLOR); lbl.image = tk_img; lbl.pack(side="left", padx=(0, 5))
            else: tk.Label(row, text="💿", bg=theme.SIDEBAR_COLOR).pack(side="left", padx=(0, 5))
            lbl = tk.Label(row, text=p['name'], font=("Segoe UI", 10), bg=theme.SIDEBAR_COLOR, fg=theme.TEXT_COLOR, anchor="w")
            lbl.pack(side="left", fill="x", expand=True)
            for w in [row, lbl]: w.bind("<Button-1>", lambda e, pl=p: self.show_view("playlist", pl))

    def show_view(self, view_type, data=None):
        for w in self.content.winfo_children(): w.destroy()
        if view_type == "search": self.setup_search_view()
        elif view_type == "favorites": self.setup_list_header("❤️ My Favorites"); self.populate_song_list(db.get_favorites())
        elif view_type == "playlist": self.setup_playlist_header(data); self.populate_song_list(db.get_playlist_songs(data['id']))

    def setup_search_view(self):
        top = tk.Frame(self.content, bg=theme.BG_COLOR); top.pack(fill="x", padx=40, pady=30)
        tk.Label(top, text="Find Music", font=("Segoe UI", 20, "bold"), bg=theme.BG_COLOR, fg=theme.TEXT_COLOR).pack(anchor="w")
        bar = tk.Frame(top, bg=theme.BG_COLOR); bar.pack(fill="x", pady=15)
        self.search_var = tk.StringVar()
        entry = tk.Entry(bar, textvariable=self.search_var, font=("Segoe UI", 12), width=40, relief="flat", highlightthickness=1, highlightbackground=theme.BORDER_COLOR)
        entry.pack(side="left", ipady=6); entry.bind("<Return>", lambda e: self.search_deezer())
        tk.Button(bar, text="Search", bg=theme.ACCENT_COLOR, fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=15, command=self.search_deezer).pack(side="left", padx=10)
        self.setup_scroll_area()

    def setup_list_header(self, title):
        tk.Label(self.content, text=title, font=("Segoe UI", 20, "bold"), bg=theme.BG_COLOR, fg=theme.TEXT_COLOR).pack(anchor="w", padx=40, pady=20)
        self.setup_scroll_area()

    def setup_playlist_header(self, p_data):
        header = tk.Frame(self.content, bg=theme.BG_COLOR); header.pack(fill="x", padx=40, pady=20)
        img_path = os.path.join(PLAYLIST_IMG_DIR, f"playlist_{p_data['id']}.jpg")
        if os.path.exists(img_path):
            img = Image.open(img_path).resize((120, 120)); tk_img = ImageTk.PhotoImage(img)
            lbl = tk.Label(header, image=tk_img, bg=theme.BG_COLOR); lbl.image = tk_img; lbl.pack(side="left", padx=(0, 20))
        else:
            f = tk.Frame(header, width=120, height=120, bg="#ddd"); f.pack(side="left", padx=(0, 20))
            tk.Label(f, text="💿", font=("Segoe UI", 40), bg="#ddd").place(relx=0.5, rely=0.5, anchor="center")
        info = tk.Frame(header, bg=theme.BG_COLOR); info.pack(side="left", fill="y")
        tk.Label(info, text="PLAYLIST", font=("Segoe UI", 9, "bold"), fg=theme.SUBTEXT_COLOR, bg=theme.BG_COLOR).pack(anchor="w")
        tk.Label(info, text=p_data['name'], font=("Segoe UI", 30, "bold"), fg=theme.TEXT_COLOR, bg=theme.BG_COLOR).pack(anchor="w")
        self.setup_scroll_area()

    def setup_scroll_area(self):
        self.canvas = tk.Canvas(self.content, bg=theme.BG_COLOR, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.content, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=theme.BG_COLOR)
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True, padx=40)
        self.scrollbar.pack(side="right", fill="y")

    def populate_song_list(self, songs):
        for i, song in enumerate(songs):
            row = tk.Frame(self.scroll_frame, bg="white", height=50, cursor="hand2"); row.pack(fill="x", pady=2); row.pack_propagate(False)
            tk.Label(row, text=str(i + 1), width=4, bg="white", fg="#888").pack(side="left")
            tk.Label(row, text=song.get('title', 'Unknown'), font=("Segoe UI", 10, "bold"), bg="white", fg="#333", anchor="w", width=30).pack(side="left")

            art = song.get('artist')
            if isinstance(art, dict): art = art.get('name')
            tk.Label(row, text=art, font=("Segoe UI", 10), bg="white", fg="#666", anchor="w", width=20).pack(side="left")

            dur = song.get('duration', '')
            if not dur: dur = "0:30"
            tk.Label(row, text=str(dur), font=("Segoe UI", 9), bg="white", fg="#888", width=6).pack(side="left")

            btn_frame = tk.Frame(row, bg="white"); btn_frame.pack(side="right", padx=10)
            tk.Button(btn_frame, text="+", font=("Segoe UI", 12), bg="white", bd=0, fg=theme.ACCENT_COLOR, command=lambda s=song: self.add_to_playlist_popup(s)).pack(side="right", padx=5)
            tk.Button(btn_frame, text="♥", font=("Segoe UI", 12), bg="white", bd=0, fg="#e11d48", command=lambda s=song: self.save_favorite(s)).pack(side="right", padx=5)
            row.bind("<Button-1>", lambda e, s=song: self.play_music(s))

    def save_favorite(self, song):
        art = song.get('artist')
        if isinstance(art, dict): art = art.get('name')
        alb = song.get('album')
        c_url = alb.get('cover_medium') if isinstance(alb, dict) else song.get('cover_url')
        a_name = alb.get('title') if isinstance(alb, dict) else song.get('album')
        sid = db.add_song(song['title'], art, a_name, song.get('preview') or song.get('preview_path'), c_url)
        db.toggle_song_favorite(sid); messagebox.showinfo("Liked", "Added to Favorites")

    def add_to_playlist_popup(self, song):
        playlists = db.get_playlists(self.user['id'])
        if not playlists: return messagebox.showwarning("No Playlists", "Create one first!")
        top = tk.Toplevel(self.parent); top.title("Add to..."); top.geometry("200x200")
        lb = tk.Listbox(top); lb.pack(fill="both", expand=True)
        for p in playlists: lb.insert("end", p['name'])
        def save():
            idx = lb.curselection()
            if not idx: return
            pid = playlists[idx[0]]['id']
            art = song.get('artist')
            if isinstance(art, dict): art = art.get('name')
            alb = song.get('album')
            c_url = alb.get('cover_medium') if isinstance(alb, dict) else song.get('cover_url')
            a_name = alb.get('title') if isinstance(alb, dict) else song.get('album')
            sid = db.add_song(song['title'], art, a_name, song.get('preview') or song.get('preview_path'), c_url)
            db.add_to_playlist(pid, sid); top.destroy(); messagebox.showinfo("Saved", "Song added to playlist.")
        tk.Button(top, text="Add", command=save).pack()