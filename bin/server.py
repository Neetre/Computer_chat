import socket
import threading
import logging
import time
import signal
import sys
import json
import os
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

SERVER_IP = config.get('Server', 'IP', fallback='127.0.0.1')
SERVER_PORT = config.getint('Server', 'Port', fallback=8765)
LOG_FILE = config.get('Paths', 'LogFile', fallback='../data/chat.csv')
KEYS_FILE = config.get('Paths', 'KeysFile', fallback='../data/registered.csv')
CHATS_FILE = config.get('Paths', 'ChatsFile', fallback='../data/chats.json')


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client_connections = []
nicknames = []

def handle_client(client_socket, client_address, server_socket):
    while True:
        try:
            try:
                data = client_socket.recv(1024).decode('utf-8').strip()
            except ConnectionResetError:
                logging.error("Connection forcibly closed by the remote host.")
                client_socket.close()

            if not data:
                logging.info(f"Connection closed by {client_address}")
                break

            logging.info(f"From {client_address}: {data}")
            log_chat(client_address, data)
            
            if data.lower() == "close":
                stop_server(server_socket, client_connections)
                return

            broadcast_message(data, client_socket)

        except OSError as e:
            logging.error(f"Error handling client {client_address}: {e}")
            client_connections.remove(client_socket)
            client_socket.close()
            
        except Exception as e:
            index = client_connections.index(client_socket)
            client_connections.pop(index)
            client_socket.close()
            nickname = nicknames[index]
            broadcast_message(f"{nickname} left the chat.", client_socket)
            nicknames.remove(nickname)
            break


def broadcast_message(message, sender_socket):
    for connection in client_connections:
        if connection != sender_socket:
            try:
                connection.send(message.encode('utf-8'))
            except Exception as e:
                logging.error(f"Error broadcasting message: {e}")


def stop_server(server_socket):
    logging.info("Turning off the server...")
    for client_socket in client_connections:
        try:
            client_socket.close()
        except Exception as e:
            logging.error(f"Error closing client socket: {e}")
    server_socket.close()
    logging.info("Server turned off.")
    sys.exit(0)


def log_chat(client_address, data):
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as file:
            file.write(f"{time.time()},{client_address},{data}\n")
    except IOError as e:
        logging.error(f"Error writing to chat log: {e}")
        
        
def get_keys():
    try:
        with open(KEYS_FILE, "r") as file:
            reader = file.readlines()[1:]
            return [line.strip().split(",") for line in reader]
    except IOError as e:
        logging.error(f"Error reading keys file: {e}")
        return []
    

def get_chats():
    try:
        with open(CHATS_FILE, "r") as file:
            return json.load(file)
    except IOError as e:
        logging.error(f"Error reading chats file: {e}")
        return {}


def authenticate_client(client_socket):
    client_socket.send("Give your key to access the chat.\n".encode('utf-8'))
    client_socket.send("Key:".encode('utf-8'))
    try:
        data = client_socket.recv(1024).decode('utf-8').strip()
        print(data)
    except ConnectionResetError:
        logging.error("Connection forcibly closed by the remote host.")
        client_socket.close()
        return False
    
    if data.split()[1].lower() == "admin":
        client_socket.send("Give your admin key to access the chat.".encode('utf-8'))
        client_socket.send("Key:".encode('utf-8'))
        try:
            data = client_socket.recv(1024).decode('utf-8').strip()
        except ConnectionResetError:
            logging.error("Connection forcibly closed by the remote host.")
            client_socket.close()
            return False
        
        if data.split()[1] == config.get('Server', 'AdminKey'):
            logging.info(f"Admin access granted to {client_socket.getpeername()}")
            client_socket.send("Admin access granted.".encode('utf-8'))
            return True
        else:
            logging.info(f"Admin access denied to {client_socket.getpeername()}")
            client_socket.send("Admin access denied.".encode('utf-8'))
            return False

    keys = get_keys()
    for key, username in keys:
        if data.split()[1] == key.strip():
            logging.info(f"Access granted to {client_socket.getpeername()}")
            client_socket.send("Access granted.".encode('utf-8'))
            broadcast_message(f"Welcome back {username}".encode('utf-8'), client_socket)
            client_socket.send("You are now connected.".encode('utf-8'))
            nicknames.append(username)
            return True
    logging.info(f"Access denied to {client_socket.getpeername()}")
    client_socket.send("Access denied.".encode('utf-8'))
    return False


def chat_room():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    print(f"Server listening on: {SERVER_IP}:{SERVER_PORT}...")

    signal.signal(signal.SIGINT, lambda sig, frame: stop_server(server_socket))

    while True:
        client_socket, client_address = server_socket.accept()
        logging.info(f"Connection accepted from {client_address}")
        
        if authenticate_client(client_socket):
            client_connections.append(client_socket)
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, server_socket))
            client_thread.start()
        else:
            client_socket.close()

def main():
    chat_room()


if __name__ == "__main__":
    main()
