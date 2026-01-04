import tkinter as tk
from tkinter import messagebox
import random
from client import ChatLogic

# --- BIDI SUPPORT (Required for visual Hebrew alignment) ---
try:
    from bidi.algorithm import get_display
    HAS_BIDI = True
except ImportError:
    HAS_BIDI = False
    print("Warning: python-bidi not found. Please install via: pip install python-bidi")

def fix_text_bidi(text):
    """Fixes text for display only (does not change sent data)"""
    if not text: return ""
    if HAS_BIDI:
        return get_display(text)
    return text

def is_hebrew(text):
    """Checks if text contains Hebrew for right alignment"""
    return any("\u0590" <= c <= "\u05ea" for c in text)

# --- CONFIG & ASSETS ---
EMOJIS = ["✨", "💖", "🦋", "🎀", "👑", "💋", "🌸", "🦄", "💅", "🍒", "💄", "👛", "🧁", "💘"]

class Marquee(tk.Canvas):
    def __init__(self, parent, text, bg, fg):
        super().__init__(parent, bg=bg, height=30, highlightthickness=0)
        self.text = fix_text_bidi(text)
        self.fg = fg
        self.width = 800
        self.text_obj = self.create_text(0, 15, text=self.text, fill=fg, font=("Comic Sans MS", 12, "bold"), anchor='w')
        self.animate()

    def animate(self):
        self.move(self.text_obj, -2, 0)
        bbox = self.bbox(self.text_obj)
        if bbox[2] < 0:
            self.coords(self.text_obj, self.width, 15)
        self.after(50, self.animate)

class Y2KPinkPaletteGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("✨🎀 PURE PINK CHAT 🎀✨")
        self.root.geometry("950x700") 
        
        self.palette = {
            "light_pink": "#FFCFD8",
            "soft_pink":  "#FFA6CA",
            "hot_pink":   "#FF1695",
            "salmon":     "#FF9CB4",
            "rose":       "#F47EAB",
            "deep_mauve": "#DA4F8E",
            "white":      "#FFFFFF"
        }

        self.root.configure(bg=self.palette["light_pink"])
        
        self.f_header = ("Comic Sans MS", 20, "bold")
        self.f_norm = ("Verdana", 10, "bold")
        self.f_cute = ("Courier New", 11, "bold")
        
        self.login_entry_style = {
            "bg": "white", 
            "fg": self.palette["hot_pink"], 
            "font": ("Fixedsys", 12), 
            "justify": 'center'
        }

        self.logic = None 
        self.nickname = ""
        self.current_chat_partner = None
        self.chat_history = {} 
        self.online_users = [] 

        # Track the last message sent for potential rollback
        self.last_optimistic_msg_indices = None

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.build_login()

    def add_chaos(self, frame, color_list):
        for _ in range(20):
            lbl = tk.Label(frame, text=random.choice(EMOJIS), 
                           bg=frame.cget("bg"), fg=random.choice(color_list),
                           font=("Arial", random.randint(14, 28)))
            x = random.uniform(0.02, 0.95)
            y = random.uniform(0.02, 0.95)
            lbl.place(relx=x, rely=y)

    # --- SCREENS ---
    def build_login(self):
        self.clear()
        
        container = tk.Frame(self.root, bg=self.palette["salmon"], bd=10, relief="ridge")
        container.place(relx=0.5, rely=0.5, anchor="center", width=500, height=500)
        
        self.add_chaos(container, [self.palette["hot_pink"], self.palette["deep_mauve"], "white"])

        content_frame = tk.Frame(container, bg=self.palette["light_pink"], bd=4, relief="solid")
        content_frame.place(relx=0.5, rely=0.5, anchor="center", width=350, height=400)

        tk.Label(content_frame, text="💖 LOGIN 💖", bg=self.palette["light_pink"], 
                 fg=self.palette["hot_pink"], font=self.f_header).pack(pady=10)
        
        tk.Label(content_frame, text="Nickname:", bg=self.palette["light_pink"], 
                 fg=self.palette["deep_mauve"], font=self.f_norm).pack()
        self.entry_nick = tk.Entry(content_frame, **self.login_entry_style)
        self.entry_nick.pack(pady=5)

        tk.Label(content_frame, text="Server IP:", bg=self.palette["light_pink"], 
                 fg=self.palette["deep_mauve"], font=self.f_norm).pack()
        self.entry_ip = tk.Entry(content_frame, **self.login_entry_style)
        self.entry_ip.insert(0, "127.0.0.1") 
        self.entry_ip.pack(pady=5)

        tk.Label(content_frame, text="Port:", bg=self.palette["light_pink"], 
                 fg=self.palette["deep_mauve"], font=self.f_norm).pack()
        self.entry_port = tk.Entry(content_frame, **self.login_entry_style)
        self.entry_port.insert(0, "55555") 
        self.entry_port.pack(pady=5)

        btn = tk.Button(content_frame, text="~*~ ENTER ~*~", 
                        bg=self.palette["hot_pink"], fg="white",
                        font=("Impact", 14), relief="raised", bd=4, command=self.connect)
        btn.pack(pady=20)

    def connect(self):
        nick = self.entry_nick.get().strip()
        host = self.entry_ip.get().strip()
        port_str = self.entry_port.get().strip()

        if not nick:
            messagebox.showwarning("Oops", "Nickname missing!")
            return
        
        if not host or not port_str.isdigit():
            messagebox.showwarning("Oops", "Invalid IP or Port!")
            return

        self.logic = ChatLogic(host, int(port_str))
        
        success, msg = self.logic.connect(nick)
        if success:
            self.nickname = nick
            self.logic.start_receiving(self.on_msg)
            self.build_chat()
        else:
            messagebox.showerror("FAIL", msg)

    def build_chat(self):
        self.clear()
        
        self.root.minsize(600, 450)
        
        marquee_txt = f"Welcome {self.nickname}!!! 💖 IT BURNS WHEN IP! 💖 NEW MSG 💖 xoxo Gossip Girl"
        mq = Marquee(self.root, marquee_txt, self.palette["deep_mauve"], "white")
        mq.pack(side="top", fill="x")

        sidebar = tk.Frame(self.root, bg=self.palette["salmon"], width=280, bd=5, relief="groove")
        sidebar.pack(side="left", fill="y", padx=5, pady=5)
        
        profile_frame = tk.Frame(sidebar, bg=self.palette["light_pink"], bd=3, relief="ridge", pady=10)
        profile_frame.pack(fill="x", padx=5, pady=(5, 10))

        tk.Label(profile_frame, text="💅", bg=self.palette["light_pink"], font=("Arial", 35)).pack()
        
        display_nick = fix_text_bidi(self.nickname)
        tk.Label(profile_frame, text=display_nick, bg=self.palette["light_pink"], 
                 fg=self.palette["hot_pink"], font=("Comic Sans MS", 14, "bold")).pack()
        
        tk.Label(profile_frame, text="~ my mood ~", bg=self.palette["light_pink"], 
                 fg=self.palette["deep_mauve"], font=("Verdana", 8)).pack(pady=(5,0))
        
        self.status_ent = tk.Entry(profile_frame, bg="white", fg=self.palette["deep_mauve"], 
                                   font=("Arial", 9, "italic"), justify="center", bd=1)
        self.status_ent.insert(0, "burning for you...")
        self.status_ent.pack(fill="x", padx=10, pady=2)

        tk.Frame(sidebar, bg="white", height=2).pack(fill="x", padx=10, pady=5)

        tk.Label(sidebar, text="★ SQUAD ★", bg=self.palette["salmon"], fg="white", 
                 font=("Comic Sans MS", 16, "bold")).pack(pady=5)
        
        self.lst_users = tk.Listbox(sidebar, bg=self.palette["light_pink"], fg=self.palette["deep_mauve"], 
                                    font=self.f_cute, selectbackground=self.palette["hot_pink"], 
                                    selectforeground="white", relief="sunken", bd=0)
        self.lst_users.pack(fill="both", expand=True, padx=10, pady=5)
        self.lst_users.bind("<<ListboxSelect>>", self.on_select_user)

        main_area = tk.Frame(self.root, bg=self.palette["light_pink"])
        main_area.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        input_frame = tk.Frame(main_area, bg=self.palette["rose"], bd=5, relief="flat", pady=8, padx=8)
        input_frame.pack(side="bottom", fill="x", pady=0)

        self.ent_msg = tk.Entry(input_frame, font=self.f_norm, bg=self.palette["light_pink"], 
                                fg=self.palette["deep_mauve"], bd=0, justify='right')
        self.ent_msg.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=5)
        self.ent_msg.bind("<Return>", lambda e: self.send())

        btn_send = tk.Button(input_frame, text="SEND 💋", bg=self.palette["hot_pink"], fg="white", 
                             font=("Impact", 12), command=self.send, bd=0, padx=15)
        btn_send.pack(side="right")

        self.lbl_target = tk.Label(main_area, text="Choose a BFF to chat! <3", 
                                   bg=self.palette["light_pink"], fg=self.palette["hot_pink"], 
                                   font=("Comic Sans MS", 18, "bold"))
        self.lbl_target.pack(side="top", pady=10)

        self.txt_chat = tk.Text(main_area, bg="white", fg=self.palette["deep_mauve"],
                                font=("Comic Sans MS", 11), state="disabled", 
                                relief="flat", bd=5)
        self.txt_chat.pack(side="top", fill="both", expand=True, padx=5)
        
        self.txt_chat.tag_config("me_ltr", foreground=self.palette["hot_pink"], font=("Verdana", 10, "bold"), justify="left")
        self.txt_chat.tag_config("them_ltr", foreground=self.palette["deep_mauve"], font=("Verdana", 10, "bold"), justify="left")
        self.txt_chat.tag_config("me_rtl", foreground=self.palette["hot_pink"], font=("Verdana", 10, "bold"), justify="right")
        self.txt_chat.tag_config("them_rtl", foreground=self.palette["deep_mauve"], font=("Verdana", 10, "bold"), justify="right")
        self.txt_chat.tag_config("sys", foreground="gray", justify="center", font=("Arial", 9, "italic"))
        self.txt_chat.tag_config("error", foreground="red", justify="center", font=("Arial", 10, "bold"))
        self.txt_chat.tag_config("join", foreground="green", justify="center", font=("Arial", 8, "bold"))
        self.txt_chat.tag_config("leave", foreground="red", justify="center", font=("Arial", 8, "bold"))

    def on_msg(self, msg):
        if msg.startswith("ONLINE_USERS:"):
            users_str = msg.replace("ONLINE_USERS:", "")
            new_users = users_str.split(",") if users_str else []
            new_users = [u for u in new_users if u != self.nickname] 
            
            old_set = set(self.online_users)
            new_set = set(new_users)
            
            joined = new_set - old_set
            left = old_set - new_set
            
            self.online_users = new_users
            self.root.after(0, lambda: self.update_list_and_notify(joined, left))
        
        # --- Server Error Handling ---
        elif msg.startswith("System:"):
            error_content = msg.split(":", 1)[1].strip()
            
            # --- Check if the error is "User not found" ---
            # If so, remove the message we just optimistically added to the screen
            if "not found" in error_content or "no longer online" in error_content:
                self.root.after(0, self.delete_last_optimistic_message)

            # Show alert to user
            messagebox.showerror("Oops!", error_content)
            # And write to log in red
            self.root.after(0, lambda: self.display_system_msg(f"❌ {error_content}", "error"))

        elif ":" in msg:
            try:
                parts = msg.split(":", 1)
                sender = parts[0].strip("[] ")
                content = parts[1].strip()
                
                self.save_msg(sender, content, "them")
                if self.current_chat_partner == sender:
                    self.root.after(0, self.display_chat_message, sender, content, "them")
            except: pass

    def delete_last_optimistic_message(self):
        """Rolls back the last message from UI and history if server rejected it."""
        if self.last_optimistic_msg_indices:
            start_idx, end_idx = self.last_optimistic_msg_indices
            
            # Remove from visual chat
            self.txt_chat.config(state="normal")
            try:
                self.txt_chat.delete(start_idx, end_idx)
            except tk.TclError:
                pass # Text widget might have changed, ignore safety
            self.txt_chat.config(state="disabled")
            
            # Remove from history so it doesn't come back on refresh
            if self.current_chat_partner in self.chat_history:
                if self.chat_history[self.current_chat_partner]:
                    self.chat_history[self.current_chat_partner].pop()
            
            self.last_optimistic_msg_indices = None

    def update_list_and_notify(self, joined, left):
        self.lst_users.delete(0, tk.END)
        for u in self.online_users:
            self.lst_users.insert(tk.END, "🎀 " + fix_text_bidi(u))
            
        if self.current_chat_partner:
            for u in joined:
                if u == self.current_chat_partner:
                    self.display_system_msg(f"~*~ {fix_text_bidi(u)} is ONLINE ~*~\n", "join")
            
            for u in left:
                if u == self.current_chat_partner:
                    self.display_system_msg(f"~*~ {fix_text_bidi(u)} disconnected :( ~*~\n", "leave")

    def on_select_user(self, e):
        sel = self.lst_users.curselection()
        if not sel: return
        real_name = self.online_users[sel[0]]
        self.current_chat_partner = real_name
        self.lbl_target.config(text=f"~*~ {fix_text_bidi(real_name)} ~*~")
        self.refresh_chat()

    def refresh_chat(self):
        self.txt_chat.config(state="normal")
        self.txt_chat.delete("1.0", tk.END)
        if self.current_chat_partner in self.chat_history:
            for m in self.chat_history[self.current_chat_partner]:
                self.display_chat_message(m['sender'], m['content'], m['type'], insert_mode=True)
        self.txt_chat.see(tk.END)
        self.txt_chat.config(state="disabled")

    def save_msg(self, partner, content, type_):
        if partner not in self.chat_history: self.chat_history[partner] = []
        name = "Me" if type_ == "me" else partner
        self.chat_history[partner].append({"sender": name, "content": content, "type": type_})

    def send(self):
        if not self.current_chat_partner:
            messagebox.showinfo("Oops!", "Pick a friend first! 💕")
            return
        
        # --- No online check here! Relying on server ---
        
        txt = self.ent_msg.get().strip()
        if not txt: return
        
        self.logic.send_private_message(self.current_chat_partner, txt)
        self.save_msg(self.current_chat_partner, txt, "me")
        
        # Optimistic update (displays immediately; if fails, we get System msg)
        # Capture indices to allow deletion if server rejects it
        start_idx = self.txt_chat.index("end-1c")
        self.display_chat_message("Me", txt, "me")
        end_idx = self.txt_chat.index("end-1c")
        self.last_optimistic_msg_indices = (start_idx, end_idx)
        
        self.ent_msg.delete(0, tk.END)

    def display_chat_message(self, sender, raw_content, base_type, insert_mode=False):
        if not insert_mode:
            self.txt_chat.config(state="normal")
        
        is_rtl_content = is_hebrew(raw_content)
        align_suffix = "_rtl" if is_rtl_content else "_ltr"
        final_tag = base_type + align_suffix
        visual_content = fix_text_bidi(raw_content)
        
        full_line = f"{sender}: {visual_content}\n"
        self.txt_chat.insert(tk.END, full_line, final_tag)
        
        if not insert_mode:
            self.txt_chat.see(tk.END)
            self.txt_chat.config(state="disabled")

    def display_system_msg(self, txt, tag):
        self.txt_chat.config(state="normal")
        self.txt_chat.insert(tk.END, txt + "\n", tag)
        self.txt_chat.see(tk.END)
        self.txt_chat.config(state="disabled")

    def clear(self):
        for w in self.root.winfo_children(): w.destroy()

    def on_closing(self):
        if self.logic:
            self.logic.disconnect()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = Y2KPinkPaletteGUI(root)
    root.mainloop()