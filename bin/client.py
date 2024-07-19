'''
This is a simple chat client that connects to a chat server and sends and receives messages.

Neetre 2024
'''

import socket
import threading
import logging
import sys

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8765

should_continue = True

def receive_msg(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')

            if "close" in message:
                close_client(client_socket)

            elif message == "":
                logging.info("Connection closed by the server...")
                close_client(client_socket)
    
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
    global should_continue  # Use a global flag to control the loop in write_msg
    should_continue = False  # Set it to False to break the loop and close the client
    client_socket.close()


def write_msg(client_socket, nickname):
    global should_continue
    should_continue = True  # Initialize the flag to True when starting to write messages
    while should_continue:  # Use the flag to control the loop
        try:
            message = f"{nickname}: {input()}"
            if message.endswith(": exit") or message.endswith(": close"):
                close_client(client_socket)
                break
            client_socket.send(message.encode('utf-8'))
        except Exception as e:
            print(f"An error occurred while sending the message: {e}")
            close_client(client_socket)
            break


def main():
    nickname = input("Enter your nickname: ")
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        logging.info("Connection to the server established...")

        receive_thread = threading.Thread(target=receive_msg, args=(client_socket,))
        receive_thread.setDaemon(True)  # Set thread as daemon
        receive_thread.start()
        
        # write_thread = threading.Thread(target=write_msg, args=(client_socket,nickname))
        # write_thread.setDaemon(True)  # Set thread as daemon
        # write_thread.start()
        
        write_msg(client_socket, nickname)

    except Exception as e:
        logging.error(f"Error during the connection: {e}")  # Corrected message
        close_client(client_socket)  # Ensure socket is closed on error\
        sys.exit()


if __name__ == "__main__":
    main()