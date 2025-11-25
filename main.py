# main.py
import tkinter as tk
from login import LoginWindow
import db

def main():
    # initialize database (creates tables if not exist)
    db.initialize_db()

    root = tk.Tk()
    root.title("Entertainment Hub - Login")
    root.geometry("480x340")
    LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()