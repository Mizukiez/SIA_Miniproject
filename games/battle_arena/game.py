import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random, json, os
import db, theme, api_services

CHAR_TEMPLATES = [
    {"name": "Flameling", "class": "Mage", "hp": 80, "max_hp": 80, "color": "#ef4444",
     "skills": [("Fireball", 20), ("Ember", 12), ("Heal", 0)]},
    {"name": "Aquabud", "class": "Tank", "hp": 100, "max_hp": 100, "color": "#3b82f6",
     "skills": [("Splash", 10), ("Water Jet", 15), ("Shield", 0)]},
    {"name": "Leaflet", "class": "Rogue", "hp": 85, "max_hp": 85, "color": "#22c55e",
     "skills": [("Vine Whip", 18), ("Tackle", 12), ("Rest", 0)]},
]


class BattleArena:
    def __init__(self, parent, user_row):
        self.parent = parent
        self.user = user_row
        self.setup_ui()

    def setup_ui(self):
        header = tk.Frame(self.parent, bg=theme.BG_COLOR)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="Your Heroes", font=("Segoe UI", 14, "bold"), bg=theme.BG_COLOR).pack(side="left")

        btn_style = {"font": ("Segoe UI", 9, "bold"), "relief": "flat", "padx": 10, "pady": 4}
        tk.Button(header, text="☁ Web Import", bg="#e0e7ff", fg="#4338ca", command=self.open_api_search,
                  **btn_style).pack(side="right", padx=5)
        tk.Button(header, text="+ New Hero", bg=theme.ACCENT_COLOR, fg="white", command=self.create_hero_dialog,
                  **btn_style).pack(side="right", padx=5)

        self.scroll_frame = tk.Frame(self.parent, bg=theme.BG_COLOR)
        self.scroll_frame.pack(fill="both", expand=True)
        self.refresh_roster()

    def refresh_roster(self):
        for w in self.scroll_frame.winfo_children(): w.destroy()
        chars = db.list_characters(self.user['id'])
        if not chars:
            tk.Label(self.scroll_frame, text="No heroes found.", bg=theme.BG_COLOR, fg="#888").pack(pady=50)
            return

        # Simple Grid
        r, c = 0, 0
        for ch in chars:
            self.create_card(ch, r, c)
            c += 1
            if c > 4: c = 0; r += 1

    def create_card(self, char, r, c):
        f = tk.Frame(self.scroll_frame, bg="white", width=160, height=220, highlightthickness=1,
                     highlightbackground="#ddd")
        f.grid(row=r, column=c, padx=10, pady=10);
        f.pack_propagate(False)

        try:
            extra = json.loads(char['data'])
        except:
            extra = {}
        color = extra.get('color', theme.ACCENT_COLOR)

        # Image
        ipath = extra.get('image_path')
        if ipath and os.path.exists(ipath):
            try:
                img = Image.open(ipath).resize((160, 100))
                ti = ImageTk.PhotoImage(img)
                l = tk.Label(f, image=ti, bg="white");
                l.image = ti;
                l.pack()
            except:
                pass
        else:
            tk.Label(f, text="⚔️", font=("Segoe UI", 30), bg="white").pack(pady=10)

        tk.Label(f, text=char['name'], font=("Segoe UI", 10, "bold"), bg="white").pack()
        tk.Label(f, text=f"{char['hp']} HP", font=("Segoe UI", 9), bg="white", fg=color).pack()
        tk.Button(f, text="Battle", bg=color, fg="white", relief="flat", command=lambda: self.start_battle(char)).pack(
            side="bottom", fill="x", padx=5, pady=5)

    def start_battle(self, char):
        try:
            extra = json.loads(char['data'])
        except:
            return
        p = {"name": char['name'], "hp": char['hp'], "max_hp": extra.get("max_hp", 100),
             "skills": extra.get("skills", []), "color": extra.get("color", "#333")}

        enemies = [
            {"name": "Shadow Beast", "hp": 100, "max_hp": 100, "skills": [("Claw", 12)], "color": "#1f2937"},
            {"name": "Goblin", "hp": 60, "max_hp": 60, "skills": [("Stab", 8)], "color": "#16a34a"}
        ]
        self.open_battle(p, random.choice(enemies))

    def open_battle(self, p, o):
        win = tk.Toplevel(self.parent);
        win.configure(bg=theme.BG_COLOR);
        win.geometry("500x450")

        arena = tk.Frame(win, bg=theme.BG_COLOR);
        arena.pack(fill="both", expand=True, padx=20, pady=20)

        self.pf = tk.Frame(arena, bg=theme.BG_COLOR);
        self.pf.pack(side="left")
        tk.Label(self.pf, text=p['name'], font=("Segoe UI", 12, "bold"), bg=theme.BG_COLOR, fg=p['color']).pack()
        self.p_bar = self.draw_hp(self.pf, p['hp'], p['max_hp'], p['color'])

        self.of = tk.Frame(arena, bg=theme.BG_COLOR);
        self.of.pack(side="right")
        tk.Label(self.of, text=o['name'], font=("Segoe UI", 12, "bold"), bg=theme.BG_COLOR, fg=o['color']).pack()
        self.o_bar = self.draw_hp(self.of, o['hp'], o['max_hp'], o['color'])

        self.log = tk.Listbox(win, height=6);
        self.log.pack(fill="x", padx=20)
        bf = tk.Frame(win, bg=theme.BG_COLOR);
        bf.pack(pady=10)
        for s in p['skills']:
            tk.Button(bf, text=s[0], command=lambda sk=s: self.turn(p, o, sk, win)).pack(side="left", padx=5)

    def draw_hp(self, p, cur, mx, col):
        c = tk.Canvas(p, width=120, height=15, bg="#ddd", highlightthickness=0);
        c.pack()
        c.create_rectangle(0, 0, (cur / mx) * 120, 15, fill=col, width=0)
        return c

    def animate_float(self, parent, text, color):
        lbl = tk.Label(parent, text=text, font=("Segoe UI", 14, "bold"), fg=color, bg=theme.BG_COLOR)
        y = 0.5;
        lbl.place(relx=0.5, rely=y, anchor="center")

        def step(c):
            nonlocal y
            if c > 10: lbl.destroy(); return
            y -= 0.03;
            lbl.place(relx=0.5, rely=y)
            parent.after(40, lambda: step(c + 1))

        step(0)

    def turn(self, p, o, sk, win):
        dmg = sk[1] + random.randint(-2, 5)
        crit = random.randint(0, 100) > 80
        if sk[1] == 0:
            p['hp'] += 20;
            self.animate_float(self.pf, "+20", "green")
            self.log.insert("end", "Healed 20 HP")
        else:
            if crit: dmg *= 2
            o['hp'] -= dmg
            self.animate_float(self.of, f"-{dmg}", "red" if crit else "orange")
            self.log.insert("end", f"Hit {dmg} {'(CRIT!)' if crit else ''}")

        if o['hp'] > 0:
            edmg = 10 + random.randint(-2, 5)
            p['hp'] -= edmg
            self.animate_float(self.pf, f"-{edmg}", "red")
            self.log.insert("end", f"Enemy hit {edmg}")

        self.p_bar.delete("all");
        self.p_bar.create_rectangle(0, 0, max(0, p['hp'] / p['max_hp']) * 120, 15, fill=p['color'], width=0)
        self.o_bar.delete("all");
        self.o_bar.create_rectangle(0, 0, max(0, o['hp'] / o['max_hp']) * 120, 15, fill=o['color'], width=0)
        self.log.see("end")

        if p['hp'] <= 0 or o['hp'] <= 0:
            messagebox.showinfo("Over", "You Won!" if o['hp'] <= 0 else "Lost")
            win.destroy()

    def create_hero_dialog(self):
        # (Simplified creation for brevity)
        d = tk.Toplevel(self.parent);
        d.configure(bg=theme.BG_COLOR)
        tk.Label(d, text="Name:", bg=theme.BG_COLOR).pack()
        e = tk.Entry(d);
        e.pack()
        tk.Button(d, text="Save Mage", command=lambda: self._save_hero(d, e.get(), CHAR_TEMPLATES[0])).pack(pady=5)
        tk.Button(d, text="Save Tank", command=lambda: self._save_hero(d, e.get(), CHAR_TEMPLATES[1])).pack(pady=5)

    def _save_hero(self, d, name, tmpl):
        data = json.dumps({"skills": tmpl['skills'], "max_hp": tmpl['hp'], "color": tmpl['color']})
        db.save_character(self.user['id'], name or tmpl['name'], 1, tmpl['hp'], 0, data)
        d.destroy();
        self.refresh_roster()

    def open_api_search(self):
        # API logic calling api_services.search_rawg
        # (You can copy the logic from previous responses here if needed)
        messagebox.showinfo("Info", "Check api_services.py integration")