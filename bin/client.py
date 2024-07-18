from http import client
import socket
import threading
import logging

SERVER_IP = "127.0.0.1"
SERVER_PORT = "8765"


def receive_msg(client_socket):
    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            
            if data:
                print(data)
            
            elif "exit" in data:
                close_client(client_socket)
            elif "close" in data:
                close_client(client_socket)
                
        except ConnectionResetError as e:
            logging.error(f"MSG: {e}")
            logging.info(f"Connection closed by the server...")
            close_client(client_socket)
            break
        
        except OSError as e:
            if e.errno == 10038:
                logging.error("Socket closed. Closing the connection...")
                close_client(client_socket)
                break
            else:
                logging.error(f"Error during the connection: {e}")
                

def close_client(client_socket):
    client_socket.close()
    return

def main():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        logging.info("Connection to the server established...")
        receive_thread = threading.Thread(target=receive_msg, args=(client_socket,))
        receive_thread.setDaemon(True)  # Set thread as daemon
        receive_thread.start()
        
        while True:
            message = input()
            client_socket.sendall(message.encode('utf-8'))
            
            if message == "exit" or message == "close":  # Combined condition
                close_client(client_socket)  # Corrected function call
                break

    except Exception as e:
        logging.error(f"Error during the connection: {e}")  # Corrected message
        close_client(client_socket)  # Ensure socket is closed on error


if __name__ == "__main__":
    main()