import socket
import threading
import logging
import time
import signal
import sys

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8765

client_connections = []

def handle_client(client_socket, client_address, server_socket):
    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                logging.error(f"Connessione chiusa da {client_address}")
                break

            print(f"Da {client_address}: {data}")
            log_chat(client_address, data)

            for connection in client_connections:
                if connection != client_socket:
                    connection.sendall(data.encode('utf-8'))
            
            # print(client_connections)
            
            if data == "close":
                stop_server(server_socket, client_connections)
                break
        
        except Exception as e:
            logging.error(f"Errore durante la gestione del client {client_address}: {e}")
            break
        
    client_connections.remove(client_socket)
    client_socket.close()

 
def stop_server(server_socket, client_connections):
    logging.info("Turning off the server...")
    for client_socket in client_connections:
        try:
            client_socket.close()
        except Exception as e:
            logging.error(f"Error closing client socket: {e}")
    server_socket.close()
    logging.info("Server turned off.")


def log_chat(client_address, data, file_path="../data/chat.csv"):
    try:
        with open(file_path, "a") as file:
            file.write(f"{time.time()},{client_address},{data}\n")
    except IOError as e:
        logging.error(f"Error writing to chat log: {e}")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)
    logging.info(f"Server listening on: {SERVER_IP}:{SERVER_PORT}...")
    
    def signal_handler(sig, frame):
        stop_server(server_socket, client_connections)
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        client_socket, client_address = server_socket.accept()
        logging.info(f"Connection accepted. Device {client_address}")
        client_connections.append(client_socket)
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, server_socket))
        client_thread.start()
        
        


if __name__ == "__main__":
    main()
