import socket
import threading

# --- Constants & Configuration ---
HOST = '127.0.0.1'
PORT = 55555

# --- Globals ---
clients = {}

# --- Helper Functions (Parsing & Validation) ---

def parse_chat_message(message, sender_nickname):
    """Parses the raw message string into target and content."""
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
    """Handles the handshake to get a unique nickname."""
    FORBIDDEN_NAMES = {"SYSTEM", "ERROR", "ONLINE_USERS"} | {user.upper() for user in list(clients)}

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

# --- Connection Management (Actions) ---

def close_connection(nickname):
    """Safely closes a client connection and removes from list."""
    if nickname not in clients:
        return

    client_socket = clients.pop(nickname)
    
    try:
        client_socket.close()
        print(f"Connection for {nickname} closed.")
    except Exception as e:
        print(f"Error closing socket for {nickname}: {e}")

def broadcast_online_users():
    """Sends the updated list of users to everyone."""
    user_list_msg = "ONLINE_USERS:" + ",".join(clients.keys())
    
    for client_name in list(clients.keys()):
        try:
            clients[client_name].send(user_list_msg.encode('utf-8'))
        except:
            try:
                client_socket = clients.pop(nickname)
                client_socket.close()
            except Exception as e:
                print(f"Error closing socket for {nickname}: {e}")
                

def kick_client(nickname):
    """Wrapper to close connection and update list."""
    close_connection(nickname)
    broadcast_online_users()

# --- Core Server Logic ---

def handle_client(client_socket, nickname):
    """Main loop for handling a single client's messages."""
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

def start_server():
    """Main entry point to start the server socket."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(10)
    print(f"Server is listening on {HOST}:{PORT}...")

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

# --- Main Execution ---
if __name__ == "__main__":
    start_server()