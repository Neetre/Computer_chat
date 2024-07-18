import socket
import threading

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8765

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((SERVER_IP, SERVER_PORT))

client_connections = []

def handle_client(client_socket, client_address):
    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                print(f"Connessione chiusa da {client_address}")
                break

            print(f"Da {client_address}: {data}")
            with open("../flussi/chat.csv", "a", encoding="utf-8") as file:
                file.write(f"{client_address},{data}\n")

            for connection in client_connections:
                if connection != client_socket:
                    connection.sendall(data.encode('utf-8'))
            
            print(client_connections)
            
            if data == "close":
                stop_server()
                break
        
        except Exception as e:
            print(f"Errore durante la gestione del client {client_address}: {e}")
            break
        
    client_connections.remove(client_socket)
    client_socket.close()
            
def stop_server():
    pass
