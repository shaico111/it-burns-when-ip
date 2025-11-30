import threading
import time
import re
from flask import Flask, render_template, jsonify, request, redirect, url_for
from client import ChatClient, KEYWORD_NAME_REQUEST, BUFFER_SIZE, ENCODING

# Clean Code: Separate Configuration
WEB_PORT = 5000
TEMPLATE_FOLDER = 'templates'

# Clean Code: Data Transfer Object for shared state
class ChatState:
    def __init__(self):
        self.messages = []
        self.active_users = set()
        self.is_connected = False

# Global state instance
chat_state = ChatState()

class WebAdaptedChatClient(ChatClient):
    """
    Adapter pattern: Extends the original ChatClient to work with a Web Interface
    instead of CLI input/output.
    """
    def __init__(self, host, port, nickname):
        super().__init__(host, port)
        self.target_nickname = nickname
        # Pattern to identify system messages about users
        self.join_pattern = re.compile(r"(.+) joined!")
        self.left_pattern = re.compile(r"(.+) left!")

    def _get_valid_nickname(self):
        """Override: Returns the nickname provided via Web instead of blocking input."""
        return self.target_nickname

    def _send_messages_loop(self):
        """Override: Does nothing. We send messages via HTTP requests, not a while loop."""
        pass 

    def _receive_messages_loop(self):
        """Override: Listens to socket and updates the shared Web state."""
        while self.is_running:
            try:
                message = self.client_socket.recv(BUFFER_SIZE).decode(ENCODING)
                
                # Handle handshake
                if message == KEYWORD_NAME_REQUEST:
                    self.client_socket.send(self.nickname.encode(ENCODING))
                    chat_state.is_connected = True
                else:
                    self._process_incoming_message(message)
                    
            except Exception as e:
                print(f"Connection lost: {e}")
                self.is_running = False
                chat_state.is_connected = False
                break

    def _process_incoming_message(self, message):
        """Parses message content to update UI and User List."""
        chat_state.messages.append(message)
        
        # Logic to track connected users based on server broadcast messages
        join_match = self.join_pattern.match(message)
        left_match = self.left_pattern.match(message)

        if join_match:
            user = join_match.group(1)
            chat_state.active_users.add(user)
        elif left_match:
            user = left_match.group(1)
            chat_state.active_users.discard(user)

    def send_web_message(self, text):
        """New Interface: Allows the Flask route to trigger sending."""
        if not self.is_running:
            return False
        try:
            formatted_msg = '{}: {}'.format(self.nickname, text)
            self.client_socket.send(formatted_msg.encode(ENCODING))
            return True
        except:
            return False

# --- Flask Web Application ---
app = Flask(__name__, template_folder=TEMPLATE_FOLDER)
client_instance = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/connect', methods=['POST'])
def connect():
    global client_instance
    nickname = request.form.get('nickname')
    host = request.form.get('host', '127.0.0.1')
    
    if not nickname:
        return "Nickname is required", 400

    # Initialize the adapter
    client_instance = WebAdaptedChatClient(host, 5500, nickname)
    
    # Run the client in a background thread to not block Flask
    t = threading.Thread(target=client_instance.start)
    t.daemon = True
    t.start()
    
    # Allow some time for handshake
    time.sleep(1) 
    
    return redirect(url_for('chat_ui'))

@app.route('/chat')
def chat_ui():
    if not client_instance or not client_instance.is_running:
        return redirect(url_for('index'))
    return render_template('chat.html', nickname=client_instance.nickname)

@app.route('/api/data')
def get_data():
    """API to fetch messages and users via AJAX."""
    return jsonify({
        'messages': chat_state.messages,
        'users': list(chat_state.active_users)
    })

@app.route('/api/send', methods=['POST'])
def send_message():
    data = request.json
    msg = data.get('message')
    if client_instance and msg:
        client_instance.send_web_message(msg)
        return jsonify({'status': 'sent'})
    return jsonify({'status': 'error'}), 400

if __name__ == '__main__':
    print("Starting Web Interface on http://127.0.0.1:5000")
    app.run(debug=True, port=WEB_PORT, use_reloader=False)