import socket
import threading

# Configuration Constants
DEFAULT_HOST = '127.0.0.1'
PORT = 5500
BUFFER_SIZE = 1024
ENCODING = 'ascii'

# Protocol Constants
KEYWORD_NAME_REQUEST = 'NAME'
MSG_JOINED = '{} joined!'
MSG_LEFT = '{} left!'
MSG_CONNECTED = 'Connected to server!'

class ChatServer:
    """
    A multi-threaded chat server that handles multiple client connections
    and broadcasts messages to all connected users.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Dictionary to map client sockets to their nicknames
        self.connected_clients = {} 

    def start(self):
        """Starts the server and listens for incoming connections."""
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            print(f"Server started on {self.host}:{self.port}")
            self._accept_connections()
        except Exception as e:
            print(f"Failed to start server: {e}")
        finally:
            self._shutdown_server()

    def _accept_connections(self):
        """Main loop to accept new client connections."""
        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
                print(f"Connected with {client_address}")
                
                # Start a separate thread to handle the handshake and communication
                client_thread = threading.Thread(
                    target=self._handle_client_handshake, 
                    args=(client_socket,)
                )
                client_thread.start()
            except OSError:
                break

    def _handle_client_handshake(self, client_socket):
        """Performs the initial name negotiation with the client."""
        try:
            client_socket.send(KEYWORD_NAME_REQUEST.encode(ENCODING))
            nickname = client_socket.recv(BUFFER_SIZE).decode(ENCODING)
            
            self.connected_clients[client_socket] = nickname
            
            print(f"Nickname is {nickname}")
            self._broadcast_message(MSG_JOINED.format(nickname).encode(ENCODING))
            client_socket.send(MSG_CONNECTED.encode(ENCODING))
            
            # Proceed to main message handling loop
            self._handle_client_messages(client_socket)
        except Exception as e:
            print(f"Handshake error: {e}")
            client_socket.close()

    def _handle_client_messages(self, client_socket):
        """Listens for messages from a specific client and broadcasts them."""
        while True:
            try:
                message = client_socket.recv(BUFFER_SIZE)
                if not message:
                    break
                self._broadcast_message(message)
            except:
                self._remove_client(client_socket)
                break

    def _broadcast_message(self, message):
        """Sends a message to all connected clients."""
        for client_sock in list(self.connected_clients.keys()):
            try:
                client_sock.send(message)
            except:
                # If sending fails, assume client disconnected
                self._remove_client(client_sock)

    def _remove_client(self, client_socket):
        """Cleanly removes a client from the active list and notifies others."""
        if client_socket in self.connected_clients:
            nickname = self.connected_clients.pop(client_socket)
            client_socket.close()
            print(f"{nickname} disconnected.")
            self._broadcast_message(MSG_LEFT.format(nickname).encode(ENCODING))

    def _shutdown_server(self):
        """Closes the server socket."""
        print("Shutting down server...")
        self.server_socket.close()

if __name__ == '__main__':
    print("--- Server Configuration ---")
    # Prompt for IP, defaulting to DEFAULT_HOST if input is empty
    user_input = input(f"Enter IP to bind (default {DEFAULT_HOST}): ").strip()
    selected_host = user_input if user_input else DEFAULT_HOST
    
    chat_server = ChatServer(selected_host, PORT)
    chat_server.start()