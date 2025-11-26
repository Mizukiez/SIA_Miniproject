import tkinter as tk
import random
import theme


class RPSGame:
    def __init__(self, parent):
        self.parent = parent
        tk.Label(parent, text="Choose Hand", font=("Segoe UI", 20, "bold"), bg=theme.BG_COLOR).pack(pady=30)

        bf = tk.Frame(parent, bg=theme.BG_COLOR);
        bf.pack()
        for m, i in [("Rock", "🪨"), ("Paper", "📄"), ("Scissors", "✂️")]:
            tk.Button(bf, text=f"{i}\n{m}", font=("Segoe UI", 14), width=8, bg="white",
                      command=lambda x=m: self.play(x)).pack(side="left", padx=10)

        self.lbl = tk.Label(parent, text="", font=("Segoe UI", 16), bg=theme.BG_COLOR)
        self.lbl.pack(pady=30)

    def play(self, u):
        c = random.choice(["Rock", "Paper", "Scissors"])
        if u == c:
            res, col = "Draw!", "gray"
        elif (u == "Rock" and c == "Scissors") or (u == "Paper" and c == "Rock") or (u == "Scissors" and c == "Paper"):
            res, col = "You Win!", "green"
        else:
            res, col = "You Lose!", "red"
        self.lbl.config(text=f"CPU: {c}\n{res}", fg=col)