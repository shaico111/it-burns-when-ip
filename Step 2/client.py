import socket
import threading
import sys

# --- Configuration & Constants ---
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 55555
BUFFER_SIZE = 1024
ENCODING = 'utf-8'

# --- Core Client Logic ---
class ChatLogic:
    """Handles socket connection, sending, and receiving messages."""
    
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = ""
        self.running = False

    # -- Connection Management --

    def connect(self, nickname):
        """Attempts to connect to server and perform handshake."""
        try:
            self.client.connect((self.host, self.port))
            self.client.send(nickname.encode(ENCODING))
            
            response = self.client.recv(BUFFER_SIZE).decode(ENCODING)
            
            if response.startswith("ERROR:"):
                self.client.close()
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Reset socket
                return False, response
            
            self.nickname = nickname
            self.running = True
            return True, "Connected successfully"
        except Exception as e:
            return False, str(e)

    def disconnect(self):
        """Closes the connection cleanly."""
        self.running = False
        try:
            self.client.close()
        except:
            pass

    # -- Messaging --

    def send_private_message(self, target, message):
        """Formats and sends a message to a specific user."""
        try:
            if not self.running: return
            full_msg = f"{target}:{message}"
            self.client.send(full_msg.encode(ENCODING))
        except socket.error:
            print("Failed to send message. Connection lost.")
            self.disconnect()

    def start_receiving(self, callback):
        """Starts a background thread to listen for incoming messages."""
        def receive_loop():
            while self.running:
                try:
                    data = self.client.recv(BUFFER_SIZE).decode(ENCODING)
                    if not data:
                        break
                    callback(data)
                except:
                    break
            
            self.disconnect()
            callback("System: Disconnected from server.")

        threading.Thread(target=receive_loop, daemon=True).start()

# --- CLI / User Interface ---

def run_cli_mode():
    """Main entry point for command-line interface interaction."""
    
    # 1. Setup Connection Details
    host = input(f"Host IP (default {DEFAULT_HOST}): ").strip() or DEFAULT_HOST
    port_input = input(f"Port (default {DEFAULT_PORT}): ").strip() or str(DEFAULT_PORT)
    
    try:
        port = int(port_input)
    except ValueError:
        print("Invalid port.")
        return

    nickname = input("Choose a Nickname: ").strip()
    if not nickname:
        print("Nickname cannot be empty.")
        return

    # 2. Initialize Logic
    logic = ChatLogic(host, port)
    success, msg = logic.connect(nickname)

    if not success:
        print(f"Connection failed: {msg}")
        return

    print(f"Connected! Usage: 'TargetName: Your Message'")
    print(f"Type 'exit' to quit.")

    # 3. Define Output Handler
    def cli_callback(message):
        print(f"\n{message}\n> ", end="")

    logic.start_receiving(cli_callback)

    # 4. Input Loop
    while True:
        try:
            user_input = input("> ")
            if user_input.lower() == 'exit':
                logic.disconnect()
                break
            
            if ":" in user_input:
                target, content = user_input.split(":", 1)
                logic.send_private_message(target.strip(), content.strip())
            else:
                print("Invalid format! Use: TargetName: Message")
                
        except KeyboardInterrupt:
            logic.disconnect()
            break

# --- Main Execution ---
if __name__ == "__main__":
    run_cli_mode()