import tkinter as tk
from tkinter import messagebox
import threading
import sys
import random
import socket

# --- SERVER LOGIC (Integrated to allow dynamic IP/Port) ---
clients = {}

def close_connection(nickname):
    if nickname not in clients:
        return
    client_socket = clients.pop(nickname)
    try:
        client_socket.close()
        print(f"Connection for {nickname} closed.")
    except Exception as e:
        print(f"Error closing socket for {nickname}: {e}")

def broadcast_online_users():
    user_list_msg = "ONLINE_USERS:" + ",".join(clients.keys())
    for client_name in list(clients.keys()):
        try:
            clients[client_name].send(user_list_msg.encode('utf-8'))
        except:
            close_connection(client_name)

def kick_client(nickname):
    close_connection(nickname)
    broadcast_online_users()

def parse_chat_message(message, sender_nickname):
    result = {"target": None, "content": None, "error": None}
    try:
        parts = message.split(":", 1)
        target = parts[0].strip()
        content = parts[1].strip()

        if target == sender_nickname:
            result["error"] = "You cannot send a message to yourself."
        elif not target or not content:
            result["error"] = "Name or message cannot be empty."
        else:
            result["target"] = target
            result["content"] = content
    except IndexError:
        result["error"] = "Invalid format. Use 'name:message'."
    except Exception:
        result["error"] = "Unknown parsing error."
    return result

def get_valid_nickname(client_socket):
    FORBIDDEN_NAMES = {"SYSTEM", "ADMIN", "ERROR"} | {user.upper() for user in list(clients)}
    while True:
        try:
            nickname = client_socket.recv(1024).decode('utf-8').strip()
            if not nickname:
                client_socket.send("ERROR: Nickname cannot be empty.".encode('utf-8'))
                continue
            if nickname.upper() in FORBIDDEN_NAMES:
                client_socket.send("ERROR: Please try another nickname.".encode('utf-8'))
                continue
            return nickname
        except:
            return None

def handle_client(client_socket, nickname):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print(f"Connection closed by {nickname}")
                break

            res = parse_chat_message(message, nickname)
            if res["error"]:
                client_socket.send(f"System: {res['error']}".encode('utf-8'))
                continue

            target, msg_content = res["target"], res["content"]
            if target not in clients:
                client_socket.send(f"System: User '{target}' not found.".encode('utf-8'))
                continue

            recipient_socket = clients[target]
            try:
                recipient_socket.send(f"[{nickname}]: {msg_content}".encode('utf-8'))
            except (socket.error, BrokenPipeError):
                print(f"Liveness Probe Failed: {target} is gone.")
                kick_client(target)
                client_socket.send(f"System: {target} is no longer online.".encode('utf-8'))
                
        except (ConnectionResetError, socket.error):
            break 
    kick_client(nickname)

def start_server_logic(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((host, port))
        server.listen(10)
        print(f"✨ Server started on {host}:{port} ✨")
        print("Waiting for BFFs to connect...")

        while True:
            try:
                client_socket, address = server.accept()
                nickname = get_valid_nickname(client_socket)
                
                if not nickname:
                    client_socket.close()
                    continue

                clients[nickname] = client_socket
                print(f"New User: {nickname} from {address}")
                client_socket.send("OK: Welcome".encode('utf-8'))

                broadcast_online_users()

                threading.Thread(target=handle_client, 
                                 args=(client_socket, nickname), 
                                 daemon=True).start()
            except Exception as e:
                print(f"Server Error: {e}")
                break
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to bind port. {e}")


# --- GUI IMPLEMENTATION ---

EMOJIS = ["✨", "💖", "🦋", "🎀", "👑", "💋", "🌸", "🦄", "💅", "🍒", "💄", "👛", "🧁", "💘"]

class Marquee(tk.Canvas):
    def __init__(self, parent, text, bg, fg):
        super().__init__(parent, bg=bg, height=30, highlightthickness=0)
        self.text = text
        self.fg = fg
        self.width = 600
        self.text_obj = self.create_text(0, 15, text=text, fill=fg, font=("Comic Sans MS", 12, "bold"), anchor='w')
        self.animate()

    def animate(self):
        self.move(self.text_obj, -2, 0)
        bbox = self.bbox(self.text_obj)
        if bbox[2] < 0:
            self.coords(self.text_obj, self.width, 15)
        self.after(50, self.animate)

class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        try:
            self.widget.configure(state="normal")
            self.widget.insert("end", str, (self.tag,))
            self.widget.see("end")
            self.widget.configure(state="disabled")
        except:
            pass # In case widget is destroyed
    
    def flush(self):
        pass

class PinkServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("✨👑 SERVER CONTROL ROOM 👑✨")
        self.root.geometry("700x550")
        
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
        
        # Fonts
        self.f_header = ("Comic Sans MS", 20, "bold")
        self.f_norm = ("Verdana", 10, "bold")
        self.f_console = ("Courier New", 10, "bold")
        
        # Entry Style (Like Client)
        self.entry_style = {
            "bg": "white", 
            "fg": self.palette["hot_pink"], 
            "font": ("Fixedsys", 12), 
            "justify": 'center'
        }

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start with Login Screen
        self.build_config_screen()

    def add_chaos(self, frame):
        for _ in range(20):
            lbl = tk.Label(frame, text=random.choice(EMOJIS), 
                           bg=frame.cget("bg"), fg="white",
                           font=("Arial", random.randint(14, 28)))
            x = random.uniform(0.02, 0.95)
            y = random.uniform(0.02, 0.95)
            lbl.place(relx=x, rely=y)

    def clear(self):
        for w in self.root.winfo_children(): w.destroy()

    # --- SCREEN 1: CONFIGURATION (Login Style) ---
    def build_config_screen(self):
        self.clear()
        
        # Container
        container = tk.Frame(self.root, bg=self.palette["salmon"], bd=10, relief="ridge")
        container.place(relx=0.5, rely=0.5, anchor="center", width=500, height=450)
        
        self.add_chaos(container)

        content_frame = tk.Frame(container, bg=self.palette["light_pink"], bd=4, relief="solid")
        content_frame.place(relx=0.5, rely=0.5, anchor="center", width=350, height=300)

        tk.Label(content_frame, text="👑 SERVER CONFIG 👑", bg=self.palette["light_pink"], 
                 fg=self.palette["hot_pink"], font=self.f_header).pack(pady=20)

        # IP Input
        tk.Label(content_frame, text="Binding IP Address:", bg=self.palette["light_pink"], 
                 fg=self.palette["deep_mauve"], font=self.f_norm).pack()
        self.ent_ip = tk.Entry(content_frame, **self.entry_style)
        self.ent_ip.insert(0, "127.0.0.1")
        self.ent_ip.pack(pady=5)

        # Port Input
        tk.Label(content_frame, text="Listening Port:", bg=self.palette["light_pink"], 
                 fg=self.palette["deep_mauve"], font=self.f_norm).pack()
        self.ent_port = tk.Entry(content_frame, **self.entry_style)
        self.ent_port.insert(0, "55555")
        self.ent_port.pack(pady=5)

        # Start Button
        btn = tk.Button(content_frame, text="✨ START SERVER ✨", 
                        bg=self.palette["hot_pink"], fg="white",
                        font=("Impact", 14), relief="raised", bd=4, 
                        command=self.start_server_action)
        btn.pack(pady=25)

    def start_server_action(self):
        ip = self.ent_ip.get().strip()
        port_str = self.ent_port.get().strip()

        if not ip or not port_str.isdigit():
            messagebox.showerror("Oops", "Invalid IP or Port!")
            return

        port = int(port_str)
        
        # Move to Console Screen
        self.build_console_screen()
        
        # Redirect Prints
        sys.stdout = TextRedirector(self.log_area, "stdout")
        sys.stderr = TextRedirector(self.log_area, "stderr")

        # Start Server Thread
        self.server_thread = threading.Thread(target=start_server_logic, args=(ip, port), daemon=True)
        self.server_thread.start()

    # --- SCREEN 2: CONSOLE ---
    def build_console_screen(self):
        self.clear()
        self.root.configure(bg=self.palette["salmon"])

        # 1. Marquee Top
        marquee_txt = "SERVER ONLINE 💖 NO HACKERS ALLOWED 💖 KEEP IT CLEAN 💖 IT BURNS WHEN IP"
        mq = Marquee(self.root, marquee_txt, self.palette["deep_mauve"], "white")
        mq.pack(side="top", fill="x")

        # 2. Main Container
        container = tk.Frame(self.root, bg=self.palette["light_pink"], bd=5, relief="ridge")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(container, text="💅 SYSTEM LOGS 💅", bg=self.palette["light_pink"], 
                 fg=self.palette["hot_pink"], font=self.f_header).pack(pady=10)

        # 3. Console Area
        console_frame = tk.Frame(container, bg=self.palette["hot_pink"], bd=2)
        console_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.log_area = tk.Text(console_frame, bg="white", fg=self.palette["deep_mauve"], 
                                font=self.f_console, state="disabled", bd=5, relief="flat")
        self.log_area.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(self.log_area, command=self.log_area.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_area['yscrollcommand'] = scrollbar.set

        # 4. Buttons
        btn_frame = tk.Frame(container, bg=self.palette["light_pink"])
        btn_frame.pack(fill="x", pady=10)

        btn_refresh = tk.Button(btn_frame, text="✨ WHO IS ONLINE? ✨", 
                                bg=self.palette["hot_pink"], fg="white",
                                font=("Impact", 12), relief="raised", bd=3,
                                command=self.show_users)
        btn_refresh.pack(side="bottom", pady=5)

    def show_users(self):
        print("\n💕 --- SQUAD CHECK --- 💕")
        if not clients:
            print("No BFFs online right now :(")
        else:
            for nickname, sock in clients.items():
                try:
                    addr = sock.getpeername()
                    print(f"🎀 {nickname} is here! (IP: {addr})")
                except:
                    print(f"🎀 {nickname} (Ghost mode)")
        print("💕 --------------------- 💕\n")

    def on_closing(self):
        sys.stdout = sys.__stdout__ # Restore console
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = PinkServerGUI(root)
    root.mainloop()