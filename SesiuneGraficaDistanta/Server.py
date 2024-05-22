
import socket
import threading
import pickle
import time

class Server:
    def __init__(self, host='localhost', port=12346):
        self.host = host
        self.port = port
        self.clients = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server started and listening on {host}:{port}")

    def handle_client(self, client_socket, client_address):
        client_name = None
        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                data = pickle.loads(data)
                action = data['action']
                if action == 'register':
                    client_name = data['name']
                    if self.register_client(client_name, client_socket):
                        self.broadcast_users_list()
                elif action == 'list':
                    self.list_clients(client_socket)
                elif action == 'request_session':
                    self.send_session_to_client(data['target'], client_socket)
                elif action == 'quit':
                    break
        finally:
            client_socket.close()
            if client_name:
                self.unregister_client(client_name)


    def register_client(self, name, client_socket):
        if name in self.clients:
            client_socket.sendall(pickle.dumps({'status': 'error', 'message': 'Name already taken'}))
            return False
        else:
            self.clients[name] = client_socket
            client_socket.sendall(pickle.dumps({'status': 'ok', 'message': 'Registered successfully'}))
            return True

    def unregister_client(self, name):
        if name in self.clients:
            del self.clients[name]
            self.broadcast_users_list()
            print(f"User {name} disconnected")

    def list_clients(self, client_socket):
        client_socket.sendall(pickle.dumps({'status': 'ok', 'users': list(self.clients.keys())}))

    def send_session_to_client(self, target, requester_socket):
        if target in self.clients:
            target_socket = self.clients[target]
            def session_update_loop():
                while target in self.clients:
                    session_data = f"Updated session data from {target}"
                    try:
                        requester_socket.sendall(pickle.dumps({'status': 'ok', 'session_data': session_data}))
                        time.sleep(5)  # Send updates every 5 seconds
                    except Exception as e:
                        break
            threading.Thread(target=session_update_loop).start()
        else:
            requester_socket.sendall(pickle.dumps({'status': 'error', 'message': 'User not found'}))

    def broadcast_users_list(self):
        users_list = list(self.clients.keys())
        for socket in self.clients.values():
            socket.sendall(pickle.dumps({'status': 'ok', 'action': 'update_users', 'users': users_list}))

    def start(self):
        print("Server is running...")
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                print(f"Received connection from {client_address}")
                threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()
        finally:
            self.server_socket.close()

if __name__ == '__main__':
    server = Server()
    server.start()
