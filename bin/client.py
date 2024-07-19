from http import client
import socket
import threading
import logging

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8765

nicknames = []

def receive_msg(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            
            if message == "Key: ":
                pass

            elif "close" in message:
                close_client(client_socket)
                
            elif "Welcome" in message:
                nickname = message.split(" ")[2]
                nicknames.append(nickname)
                print(message)

            else:
                print(message)
                
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


def write_msg(client_socket):
    while True:
        message = f"{nicknames[0]}: {input()}"
        client_socket.send(message.encode('utf-8'))
        
        if message == "exit" or message == "close":
            close_client(client_socket)
            break


def main():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        logging.info("Connection to the server established...")

        receive_thread = threading.Thread(target=receive_msg, args=(client_socket,))
        receive_thread.setDaemon(True)  # Set thread as daemon
        receive_thread.start()
        
        write_thread = threading.Thread(target=write_msg, args=(client_socket,))
        write_thread.setDaemon(True)  # Set thread as daemon
        write_thread.start()

    except Exception as e:
        logging.error(f"Error during the connection: {e}")  # Corrected message
        close_client(client_socket)  # Ensure socket is closed on error


if __name__ == "__main__":
    main()