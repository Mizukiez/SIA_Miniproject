import tkinter as tk
import theme

# Import games from their specific folders
from games.battle_arena.game import BattleArena
from games.mystery_number.game import NumberGuessGame
from games.rps.game import RPSGame
from games.tic_tac_toe.game import TicTacToeGame


class GamesApp:
    def __init__(self, parent, user_row):
        self.parent = parent
        self.user = user_row
        self.show_menu()

    def show_menu(self):
        for w in self.parent.winfo_children(): w.destroy()

        # Header
        tk.Label(self.parent, text="Arcade Center", font=("Segoe UI", 26, "bold"),
                 bg=theme.BG_COLOR, fg=theme.TEXT_COLOR).pack(pady=(30, 10))
        tk.Label(self.parent, text="Select a game to start", font=("Segoe UI", 12),
                 bg=theme.BG_COLOR, fg=theme.SUBTEXT_COLOR).pack(pady=(0, 20))

        # Game Grid
        grid = tk.Frame(self.parent, bg=theme.BG_COLOR)
        grid.pack(expand=True)

        # -- Row 1 --
        self.create_card(grid, 0, 0, "⚔️ Battle Arena", "RPG Strategy", "#fee2e2",
                         lambda: self.launch("Battle Arena", BattleArena, needs_user=True))

        self.create_card(grid, 0, 1, "❌ Tic Tac Toe", "2-Player Strategy", "#fef3c7",
                         lambda: self.launch("Tic Tac Toe", TicTacToeGame))

        # -- Row 2 --
        self.create_card(grid, 1, 0, "🔢 Mystery Number", "Logic Puzzle", "#dbeafe",
                         lambda: self.launch("Mystery Number", NumberGuessGame))

        self.create_card(grid, 1, 1, "✂️ Rock Paper Scissors", "Classic Luck", "#dcfce7",
                         lambda: self.launch("RPS", RPSGame))

    def create_card(self, parent, r, c, title, sub, color, cmd):
        card = tk.Frame(parent, bg="white", width=220, height=180,
                        highlightthickness=1, highlightbackground=theme.BORDER_COLOR, cursor="hand2")
        card.grid(row=r, column=c, padx=15, pady=15)
        card.pack_propagate(False)

        def on_enter(e): card.config(bg=color)

        def on_leave(e): card.config(bg="white")

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        card.bind("<Button-1>", lambda e: cmd())

        inner = tk.Frame(card, bg="white")  # Transparent container
        inner.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(inner, text=title.split(" ")[0], font=("Segoe UI", 35), bg="white").pack(pady=5)
        tk.Label(inner, text=" ".join(title.split(" ")[1:]), font=("Segoe UI", 11, "bold"), bg="white",
                 fg=theme.TEXT_COLOR).pack()
        tk.Label(inner, text=sub, font=("Segoe UI", 9), bg="white", fg=theme.SUBTEXT_COLOR).pack()

        for w in inner.winfo_children(): w.bind("<Button-1>", lambda e: cmd())

    def launch(self, title, GameClass, needs_user=False):
        for w in self.parent.winfo_children(): w.destroy()

        # Nav Bar
        nav = tk.Frame(self.parent, bg="white", height=50, highlightthickness=1, highlightbackground=theme.BORDER_COLOR)
        nav.pack(fill="x");
        nav.pack_propagate(False)
        tk.Button(nav, text="⬅ Back to Arcade", font=("Segoe UI", 10, "bold"), bg="white", bd=0, fg=theme.ACCENT_COLOR,
                  command=self.show_menu, cursor="hand2").pack(side="left", padx=20)
        tk.Label(nav, text=title, font=("Segoe UI", 12, "bold"), bg="white").pack(side="left")

        container = tk.Frame(self.parent, bg=theme.BG_COLOR)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        if needs_user:
            GameClass(container, self.user)
        else:
            GameClass(container)