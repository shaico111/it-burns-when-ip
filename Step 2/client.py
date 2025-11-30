import socket
import threading
import sys

# Configuration Constants
DEFAULT_SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5500
BUFFER_SIZE = 1024
ENCODING = 'ascii'
KEYWORD_NAME_REQUEST = 'NAME'

class ChatClient:
    """
    A client application that connects to the chat server,
    sends messages, and receives broadcasts.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = ""
        self.is_running = False

    def start(self):
        """Initiates the connection process."""
        self.nickname = self._get_valid_nickname()
        try:
            self.client_socket.connect((self.host, self.port))
            self.is_running = True
            
            # Start threads for simultaneous listening and writing
            receive_thread = threading.Thread(target=self._receive_messages_loop)
            write_thread = threading.Thread(target=self._send_messages_loop)
            
            receive_thread.start()
            write_thread.start()
            
            # Keep main thread alive to allow child threads to run
            receive_thread.join()
            write_thread.join()
            
        except ConnectionRefusedError:
            print("Could not connect to the server. Is it running?")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self._close_connection()

    def _get_valid_nickname(self):
        """Prompts user for a non-empty nickname."""
        while True:
            name = input("Choose your name for the chat: ").strip()
            if name:
                return name
            print("Name cannot be empty.")

    def _receive_messages_loop(self):
        """Continuously listens for messages from the server."""
        while self.is_running:
            try:
                message = self.client_socket.recv(BUFFER_SIZE).decode(ENCODING)
                if message == KEYWORD_NAME_REQUEST:
                    self.client_socket.send(self.nickname.encode(ENCODING))
                else:
                    print(message)
            except OSError:
                # Socket likely closed or connection lost
                print("Disconnected from server.")
                self.is_running = False
                self.client_socket.close()
                break
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.is_running = False
                break

    def _send_messages_loop(self):
        """Continuously waits for user input and sends it to the server."""
        while self.is_running:
            try:
                text = input('')
                # Handle command to exit locally (optional UX improvement)
                if text.lower() == 'quit':
                    self.is_running = False
                    break
                
                message = '{}: {}'.format(self.nickname, text)
                self.client_socket.send(message.encode(ENCODING))
            except Exception as e:
                print(f"Error sending message: {e}")
                self.is_running = False
                break
        
        self._close_connection()

    def _close_connection(self):
        """Safely closes the socket."""
        try:
            self.client_socket.close()
            # Force exit since input() in the other thread might be blocking
            sys.exit(0) 
        except:
            pass

if __name__ == '__main__':
    print("--- Connection Configuration ---")
    # Prompt for Server IP, defaulting to DEFAULT_SERVER_HOST if input is empty
    user_input = input(f"Enter server IP (default {DEFAULT_SERVER_HOST}): ").strip()
    target_host = user_input if user_input else DEFAULT_SERVER_HOST
    
    print(f"Connecting to {target_host}:{SERVER_PORT}...")
    
    client = ChatClient(target_host, SERVER_PORT)
    client.start()