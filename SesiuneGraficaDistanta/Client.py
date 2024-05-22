import socket
import pickle


def create_client(server_host='localhost', server_port=12346, user_name='User'):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))
    print("Connected to server")

    # Register user
    send_data(client_socket, {'action': 'register', 'name': user_name})

    # Main loop to interact with server
    while True:
        print("\nAvailable commands: list, request [username], quit")
        command = input("Enter command: ")
        if command == 'list':
            send_data(client_socket, {'action': 'list'})
        elif command.startswith('request'):
            _, target_name = command.split()
            send_data(client_socket, {'action': 'request_session', 'target': target_name})
        elif command == 'quit':
            break
        else:
            print("Unknown command")

        # Receive and handle response from the server
        response = receive_data(client_socket)
        handle_response(response)

    client_socket.close()
    print("Disconnected from server")


def send_data(socket, data):
    socket.sendall(pickle.dumps(data))


def receive_data(socket):
    return pickle.loads(socket.recv(4096))


def handle_response(response):
    if response['status'] == 'error':
        print(f"Error: {response['message']}")
    elif response['status'] == 'ok':
        if 'message' in response:
            print(response['message'])
        if 'users' in response:
            print("Connected users:", ', '.join(response['users']))
        if 'session_data' in response:
            print("Received session data:", response['session_data'])


if __name__ == '__main__':
    user_name = input("Enter your user name: ")
    create_client(user_name=user_name)
