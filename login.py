# login.py
import tkinter as tk
from tkinter import messagebox
import db
from main_app import MainApp
import theme


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Entertainment Hub")
        self.root.geometry("400x500")
        self.root.configure(bg=theme.BG_COLOR)
        self.root.resizable(False, False)
        self.center_window(400, 500)

        # Main Container
        self.frame = tk.Frame(root, bg=theme.BG_COLOR)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        # Logo / Title area
        tk.Label(self.frame, text="Welcome Back", font=("Segoe UI", 24, "bold"),
                 bg=theme.BG_COLOR, fg=theme.TEXT_COLOR).pack(pady=(0, 10))
        tk.Label(self.frame, text="Login to your library", font=("Segoe UI", 10),
                 bg=theme.BG_COLOR, fg="#aaaaaa").pack(pady=(0, 30))

        # Inputs
        self.username_entry = self.create_input(self.frame, "Username")
        self.password_entry = self.create_input(self.frame, "Password", is_password=True)

        # Buttons
        btn_frame = tk.Frame(self.frame, bg=theme.BG_COLOR)
        btn_frame.pack(pady=20, fill="x")

        self.create_button(btn_frame, "Login", self.login, theme.ACCENT_COLOR).pack(fill="x", pady=5)
        self.create_button(btn_frame, "Create Account", self.open_register_window, "#9ca3af").pack(fill="x", pady=5)

    def create_input(self, parent, placeholder, is_password=False):
        tk.Label(parent, text=placeholder, font=("Segoe UI", 10, "bold"),
                 bg=theme.BG_COLOR, fg=theme.TEXT_COLOR).pack(anchor="w", pady=(10, 5))
        entry = tk.Entry(parent, font=("Segoe UI", 11), bg=theme.INPUT_BG,
                         fg=theme.TEXT_COLOR, insertbackground=theme.TEXT_COLOR, relief="flat", width=30)
        if is_password: entry.config(show="●")
        entry.pack(ipady=5, fill="x")
        # Add a subtle line below
        tk.Frame(parent, height=2, bg=theme.ACCENT_COLOR).pack(fill="x")
        return entry

    def create_button(self, parent, text, command, bg_color):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 11, "bold"),
                        bg=bg_color, fg="white", activebackground=bg_color,
                        activeforeground="white", relief="flat", command=command, cursor="hand2")
        return btn

    def center_window(self, w, h):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w // 2) - (w // 2)
        y = (screen_h // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showwarning("Missing", "Enter details")
            return
        user = db.find_user(username, password)
        if user:
            self.frame.destroy()
            MainApp(self.root, user)
        else:
            messagebox.showerror("Error", "Invalid credentials")

    # ---------------------------------------------------------
    # NEW REGISTRATION WINDOW
    # ---------------------------------------------------------
    def open_register_window(self):
        reg = tk.Toplevel(self.root)
        reg.title("Create Account")
        reg.geometry("450x650")
        reg.configure(bg=theme.BG_COLOR)

        # Header
        tk.Label(reg, text="Join Us", font=("Segoe UI", 22, "bold"),
                 bg=theme.BG_COLOR, fg=theme.TEXT_COLOR).pack(pady=(20, 5))

        # Form Container
        form = tk.Frame(reg, bg=theme.BG_COLOR, padx=30)
        form.pack(fill="both", expand=True)

        # Helper for clean inputs in popup
        def add_field(label, is_pass=False):
            tk.Label(form, text=label, font=("Segoe UI", 9, "bold"),
                     bg=theme.BG_COLOR, fg=theme.TEXT_COLOR).pack(anchor="w", pady=(10, 2))
            e = tk.Entry(form, font=("Segoe UI", 11), bg=theme.INPUT_BG,
                         fg=theme.TEXT_COLOR, insertbackground=theme.TEXT_COLOR, relief="flat")
            if is_pass: e.config(show="●")
            e.pack(fill="x", ipady=4)
            tk.Frame(form, height=1, bg=theme.ACCENT_COLOR).pack(fill="x")
            return e

        # Fields
        fname_e = add_field("First Name")
        lname_e = add_field("Last Name")
        email_e = add_field("Email Address")
        user_e = add_field("Username")
        pass_e = add_field("Password", True)
        conf_e = add_field("Confirm Password", True)

        def submit_registration():
            # Get values
            f = fname_e.get().strip()
            l = lname_e.get().strip()
            e = email_e.get().strip()
            u = user_e.get().strip()
            p = pass_e.get().strip()
            c = conf_e.get().strip()

            # Validation
            if not f or not l or not e or not u or not p:
                messagebox.showwarning("Missing Info", "Please fill in all fields.")
                return

            if p != c:
                messagebox.showerror("Password Error", "Passwords do not match.")
                return

            if len(p) < 4:
                messagebox.showwarning("Weak Password", "Password must be at least 4 characters.")
                return

            # Save to DB
            uid = db.create_user(f, l, e, u, p)

            if uid:
                messagebox.showinfo("Success", "Account created successfully! Please login.")
                reg.destroy()
            else:
                messagebox.showerror("Error", "Username already exists. Please choose another.")

        # Submit Button
        tk.Button(reg, text="Sign Up", bg=theme.ACCENT_COLOR, fg="white",
                  font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2",
                  command=submit_registration).pack(fill="x", padx=30, pady=30)