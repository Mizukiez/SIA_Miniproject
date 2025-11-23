# games_app.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random, json, os
import db, theme
import api_services # <--- NEW IMPORT

# CONFIGURATION
IMAGE_SAVE_DIR = "game_images"
if not os.path.exists(IMAGE_SAVE_DIR): os.makedirs(IMAGE_SAVE_DIR)

# Default Templates
CHAR_TEMPLATES = [
    {"name": "Flameling", "class": "Mage", "hp": 80, "max_hp": 80, "color": "#ef4444",
     "skills": [("Fireball", 20), ("Ember", 12), ("Heal", 0)]},
    {"name": "Aquabud", "class": "Tank", "hp": 100, "max_hp": 100, "color": "#3b82f6",
     "skills": [("Splash", 10), ("Water Jet", 15), ("Bubble Shield", 0)]},
    {"name": "Leaflet", "class": "Rogue", "hp": 85, "max_hp": 85, "color": "#22c55e",
     "skills": [("Vine Whip", 18), ("Tackle", 12), ("Photosynthesis", 0)]},
]

class GamesApp:
    def __init__(self, parent, user_row):
        self.parent = parent
        self.user = user_row
        self.setup_ui()

    def setup_ui(self):
        header = tk.Frame(self.parent, bg=theme.BG_COLOR)
        header.pack(fill="x", padx=30, pady=20)
        tk.Label(header, text="Battle Arena", font=("Segoe UI", 22, "bold"),
                 bg=theme.BG_COLOR, fg=theme.TEXT_COLOR).pack(side="left")

        btn_style = {"font": ("Segoe UI", 10, "bold"), "relief": "flat", "padx": 15, "pady": 5}
        tk.Button(header, text="☁ Add from Web", bg="#e0e7ff", fg="#4338ca",
                  command=self.open_api_search, **btn_style).pack(side="right", padx=5)
        tk.Button(header, text="+ Custom Hero", bg=theme.ACCENT_COLOR, fg="white",
                  command=self.create_character_dialog, **btn_style).pack(side="right", padx=5)

        self.content = tk.Frame(self.parent, bg=theme.BG_COLOR)
        self.content.pack(fill="both", expand=True, padx=30)

        self.canvas = tk.Canvas(self.content, bg=theme.BG_COLOR, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.content, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=theme.BG_COLOR)

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.refresh_roster()

    def refresh_roster(self):
        for w in self.scroll_frame.winfo_children(): w.destroy()
        chars = db.list_characters(self.user['id'])
        if not chars:
            tk.Label(self.scroll_frame, text="No heroes yet.", bg=theme.BG_COLOR, fg="#888").pack(pady=50)
            return

        row, col = 0, 0
        for c in chars:
            self.create_card(c, row, col)
            col += 1
            if col > 3: col = 0; row += 1

    def create_card(self, char, r, c):
        card = tk.Frame(self.scroll_frame, bg="white", width=200, height=280,
                        highlightthickness=1, highlightbackground=theme.BORDER_COLOR)
        card.grid(row=r, column=c, padx=10, pady=10)
        card.pack_propagate(False)

        try: extra = json.loads(char['data'])
        except: extra = {}
        color = extra.get('color', theme.ACCENT_COLOR)
        img_path = extra.get('image_path')

        img_frame = tk.Frame(card, bg="white", height=120)
        img_frame.pack(fill="x")
        img_frame.pack_propagate(False)

        has_img = False
        if img_path and os.path.exists(img_path):
            try:
                pil_img = Image.open(img_path); pil_img.thumbnail((200, 120))
                tk_img = ImageTk.PhotoImage(pil_img)
                lbl = tk.Label(img_frame, image=tk_img, bg="white"); lbl.image = tk_img
                lbl.pack()
                has_img = True
            except: pass

        if not has_img:
            tk.Label(img_frame, text="⚔️", font=("Segoe UI", 40), bg="white", fg=color).pack(expand=True)

        tk.Label(card, text=char['name'], font=("Segoe UI", 11, "bold"), bg="white", fg=theme.TEXT_COLOR).pack(pady=(10, 0))
        tk.Label(card, text=f"HP: {char['hp']}", font=("Segoe UI", 11, "bold"), bg="white", fg=color).pack(pady=5)

        btn_frame = tk.Frame(card, bg="white")
        btn_frame.pack(side="bottom", fill="x", pady=10)
        tk.Button(btn_frame, text="Battle", bg=color, fg="white", relief="flat",
                  command=lambda: self.start_battle(char)).pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(btn_frame, text="×", bg="#fee2e2", fg="red", relief="flat", width=3,
                  command=lambda: self.delete_char(char['id'])).pack(side="right", padx=5)

    def delete_char(self, cid): pass

    # --- API INTEGRATION (Refactored) ---
    def open_api_search(self):
        self.api_dlg = tk.Toplevel(self.parent)
        self.api_dlg.title("Import Game Hero")
        self.api_dlg.geometry("500x450")
        self.api_dlg.configure(bg=theme.BG_COLOR)

        f = tk.Frame(self.api_dlg, bg=theme.BG_COLOR)
        f.pack(fill="x", padx=10, pady=10)
        self.api_entry = tk.Entry(f, font=("Segoe UI", 11), width=30)
        self.api_entry.pack(side="left", padx=5)
        self.api_entry.bind("<Return>", lambda e: self.perform_api_search())
        tk.Button(f, text="Search RAWG", bg=theme.ACCENT_COLOR, fg="white", command=self.perform_api_search).pack(side="left")

        self.api_listbox = tk.Listbox(self.api_dlg, width=60, height=15)
        self.api_listbox.pack(padx=10, pady=5)
        tk.Button(self.api_dlg, text="Import Selected", bg="#10b981", fg="white", command=self.save_api_selection).pack(pady=10)
        self.api_results = []

    def perform_api_search(self):
        query = self.api_entry.get().strip()
        if not query: return
        # Call new API Service
        self.api_results = api_services.search_rawg(query)
        self.api_listbox.delete(0, "end")
        for game in self.api_results:
            self.api_listbox.insert("end", f"{game['name']} (Released: {game.get('released', 'N/A')})")

    def save_api_selection(self):
        sel = self.api_listbox.curselection()
        if not sel: return
        game = self.api_results[sel[0]]

        # Call new API Service to download
        local_path = api_services.download_rawg_image(game.get('background_image'), game['id'], IMAGE_SAVE_DIR)

        hp = random.randint(80, 150)
        genres = [g['name'] for g in game.get('genres', [])]
        skills = [("Basic Attack", 10)]
        color = "#3b82f6"

        if "Shooter" in genres: skills += [("Headshot", 25), ("Grenade", 15)]; color = "#f59e0b"
        elif "RPG" in genres: skills += [("Magic Blast", 20), ("Heal", 0)]; color = "#8b5cf6"
        elif "Action" in genres: skills += [("Combo Strike", 18), ("Dodge", 0)]; color = "#ef4444"
        else: skills += [("Special Move", 20)]

        data_json = json.dumps({"skills": skills, "max_hp": hp, "color": color, "image_path": local_path, "origin": "Imported"})
        db.save_character(self.user['id'], game['name'], 1, hp, 0, data_json)
        self.api_dlg.destroy()
        self.refresh_roster()
        messagebox.showinfo("Success", f"{game['name']} has joined the arena!")

    # --- CREATION & BATTLE ---
    def create_character_dialog(self):
        dlg = tk.Toplevel(self.parent)
        dlg.configure(bg=theme.BG_COLOR)
        tk.Label(dlg, text="Name:", bg=theme.BG_COLOR).pack()
        name_e = tk.Entry(dlg); name_e.pack()
        v = tk.StringVar(value=CHAR_TEMPLATES[0]['name'])
        for t in CHAR_TEMPLATES:
            tk.Radiobutton(dlg, text=t['name'], variable=v, value=t['name'], bg=theme.BG_COLOR).pack()
        def save():
            tmpl = next(t for t in CHAR_TEMPLATES if t['name'] == v.get())
            extra = {"skills": tmpl['skills'], "max_hp": tmpl['hp'], "color": tmpl['color']}
            db.save_character(self.user['id'], name_e.get() or "Hero", 1, tmpl['hp'], 0, json.dumps(extra))
            dlg.destroy()
            self.refresh_roster()
        tk.Button(dlg, text="Create", command=save).pack(pady=10)

    def start_battle(self, char):
        try:
            extra = json.loads(char['data'])
            player = {"name": char['name'], "hp": char['hp'], "max_hp": extra.get("max_hp", 100),
                      "skills": extra.get("skills", []), "color": extra.get("color", "#333")}
        except: return
        opp = {"name": "Shadow Beast", "hp": 100, "max_hp": 100, "skills": [("Claw", 12)], "color": "#333"}
        self.open_battle_window(player, opp)

    def open_battle_window(self, p, o):
        win = tk.Toplevel(self.parent)
        win.configure(bg=theme.BG_COLOR); win.geometry("600x500")
        arena = tk.Frame(win, bg=theme.BG_COLOR); arena.pack(fill="both", expand=True, padx=20, pady=20)

        pf = tk.Frame(arena, bg=theme.BG_COLOR); pf.pack(side="left")
        tk.Label(pf, text=p['name'], font=("Segoe UI", 16, "bold"), bg=theme.BG_COLOR, fg=p['color']).pack()
        self.p_bar = self.draw_hp(pf, p['hp'], p['max_hp'], p['color'])

        of = tk.Frame(arena, bg=theme.BG_COLOR); of.pack(side="right")
        tk.Label(of, text=o['name'], font=("Segoe UI", 16, "bold"), bg=theme.BG_COLOR, fg=o['color']).pack()
        self.o_bar = self.draw_hp(of, o['hp'], o['max_hp'], o['color'])

        self.log = tk.Listbox(win, height=8); self.log.pack(fill="x", padx=20)
        bf = tk.Frame(win, bg=theme.BG_COLOR); bf.pack(pady=10)
        for s in p['skills']:
            tk.Button(bf, text=s[0], command=lambda sk=s: self.turn(p, o, sk, win)).pack(side="left", padx=5)

    def draw_hp(self, p, cur, mx, col):
        c = tk.Canvas(p, width=150, height=15, bg="#ddd", highlightthickness=0); c.pack()
        c.create_rectangle(0, 0, (cur/mx)*150, 15, fill=col, width=0)
        return c

    def turn(self, p, o, sk, win):
        dmg = sk[1] + random.randint(-2, 5)
        if sk[1] == 0: p['hp'] += 20; self.log.insert("end", f"Healed 20 HP")
        else: o['hp'] -= dmg; self.log.insert("end", f"Dealt {dmg} dmg to enemy")

        dmg_e = 10 + random.randint(-2, 5)
        p['hp'] -= dmg_e
        self.log.insert("end", f"Enemy dealt {dmg_e} dmg"); self.log.see("end")

        self.p_bar.delete("all"); self.p_bar.create_rectangle(0, 0, (p['hp']/p['max_hp'])*150, 15, fill=p['color'], width=0)
        self.o_bar.delete("all"); self.o_bar.create_rectangle(0, 0, (o['hp']/o['max_hp'])*150, 15, fill=o['color'], width=0)

        if p['hp'] <= 0 or o['hp'] <= 0: messagebox.showinfo("End", "Battle Over"); win.destroy()