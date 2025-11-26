import tkinter as tk
from tkinter import messagebox
import theme


class TicTacToeGame:
    def __init__(self, parent):
        self.parent = parent
        self.turn = 'X'
        self.board = [""] * 9
        self.game_over = False

        tk.Label(parent, text="Tic Tac Toe (2 Player)", font=("Segoe UI", 18, "bold"), bg=theme.BG_COLOR).pack(pady=20)
        self.status = tk.Label(parent, text=f"Player {self.turn}'s Turn", font=("Segoe UI", 12), bg=theme.BG_COLOR)
        self.status.pack(pady=(0, 20))

        # Grid
        grid_frame = tk.Frame(parent, bg=theme.BG_COLOR)
        grid_frame.pack()
        self.buttons = []
        for i in range(9):
            btn = tk.Button(grid_frame, text="", font=("Segoe UI", 20, "bold"), width=4, height=2, bg="white",
                            command=lambda idx=i: self.click(idx))
            btn.grid(row=i // 3, column=i % 3, padx=2, pady=2)
            self.buttons.append(btn)

        tk.Button(parent, text="Reset Game", bg=theme.ACCENT_COLOR, fg="white", command=self.reset).pack(pady=20)

    def click(self, idx):
        if self.board[idx] or self.game_over: return

        self.board[idx] = self.turn
        self.buttons[idx].config(text=self.turn, fg="#3b82f6" if self.turn == "X" else "#ef4444")

        if self.check_win():
            self.status.config(text=f"Player {self.turn} WINS!", fg="green")
            self.game_over = True
            messagebox.showinfo("Game Over", f"Player {self.turn} Wins!")
        elif "" not in self.board:
            self.status.config(text="It's a Draw!", fg="gray")
            self.game_over = True
        else:
            self.turn = "O" if self.turn == "X" else "X"
            self.status.config(text=f"Player {self.turn}'s Turn", fg="black")

    def check_win(self):
        wins = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
        for a, b, c in wins:
            if self.board[a] == self.board[b] == self.board[c] and self.board[a] != "":
                return True
        return False

    def reset(self):
        self.turn = 'X'
        self.board = [""] * 9
        self.game_over = False
        self.status.config(text=f"Player {self.turn}'s Turn", fg="black")
        for btn in self.buttons:
            btn.config(text="", bg="white")