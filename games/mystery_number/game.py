import tkinter as tk
import random
import theme


class NumberGuessGame:
    def __init__(self, parent):
        self.parent = parent
        self.target = random.randint(1, 100)
        self.attempts = 0

        f = tk.Frame(parent, bg="white", padx=40, pady=40)
        f.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(f, text="Guess (1-100)", font=("Segoe UI", 16, "bold"), bg="white").pack()
        self.entry = tk.Entry(f, font=("Segoe UI", 20), justify="center", width=5, bg="#f3f4f6")
        self.entry.pack(pady=15)
        self.entry.bind("<Return>", lambda e: self.check())

        self.btn = tk.Button(f, text="Guess", bg=theme.ACCENT_COLOR, fg="white", command=self.check)
        self.btn.pack(fill="x")

        self.lbl = tk.Label(f, text="", font=("Segoe UI", 12), bg="white")
        self.lbl.pack(pady=10)

    def check(self):
        try:
            v = int(self.entry.get())
        except:
            return
        self.attempts += 1
        if v == self.target:
            self.lbl.config(text=f"Correct! Took {self.attempts} tries.", fg="green")
            self.btn.config(text="Play Again", command=self.reset)
        elif v < self.target:
            self.lbl.config(text="Too Low 🔼", fg="orange")
        else:
            self.lbl.config(text="Too High 🔽", fg="red")
        self.entry.delete(0, "end")

    def reset(self):
        self.target = random.randint(1, 100);
        self.attempts = 0
        self.lbl.config(text="");
        self.btn.config(text="Guess", command=self.check)