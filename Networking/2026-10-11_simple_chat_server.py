"""
A simple, multi-threaded chat server that allows multiple clients to connect
and exchange messages.

Clients can connect, choose a nickname, and then send messages that will be
broadcast to all other connected clients. The server handles client disconnections
gracefully.

To run:
1. Save this script as, e.g., `chat_server.py`.
2. Run from your terminal: `python chat_server.py`
3. Clients can connect using a separate client script (e.g., `chat_client.py`
   using `socket` module) or tools like `netcat` or `telnet`.
   Example for client connection using netcat (from another terminal window):
   `nc 127.0.0.1 55555`
   Upon connecting, the client will need to send its nickname. For netcat,
   you'd type "NICK:MyName" and press Enter.
"""

import socket
import threading
import sys

# Server configuration
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 55555        # Port to listen on (non-privileged ports are > 1023)

# List to keep track of connected clients and their nicknames
# Each element will be a tuple: (client_socket, nickname)
clients = []
# A lock to protect the 'clients' list from race conditions when multiple
# threads try to modify it simultaneously.
clients_lock = threading.Lock()

def broadcast(message, sender_socket=None):
    """
    Sends a message to all connected clients.
    
    Args:
        message (bytes): The message to be sent, typically encoded in utf-8.
        sender_socket (socket.socket, optional): The socket of the client
            who sent the message. If provided, the message will not be sent
            back to the sender. Defaults to None, meaning the message is
            sent to all clients including the sender.
    """
    with clients_lock:
        # Iterate over a copy of the clients list to prevent issues if a client
        # disconnects and is removed from the original list during iteration.
        for client_socket, _ in list(clients):
            if client_socket != sender_socket:
                try:
                    client_socket.sendall(message)
                except socket.error as e:
                    # If sending fails, it means the client probably disconnected.
                    # We handle removal more robustly in `remove_client`
                    # but a log here is useful.
                    print(f"Warning: Failed to send to {client_socket.getpeername()}. Error: {e}")
                    # The client will be properly removed when their `handle_client`
                    # thread detects the disconnection.

def remove_client(client_socket_to_remove):
    """
    Removes a client from the global list and closes its socket.
    Informs all other clients about the disconnection.
    """
    with clients_lock:
        disconnected_nickname = "Unknown"
        # Find the client in the list
        for i, (sock, nick) in enumerate(clients):
            if sock == client_socket_to_remove:
                disconnected_nickname = nick
                del clients[i] # Remove client from the list
                try:
                    sock.close() # Close the socket
                    print(f"Closed socket for {disconnected_nickname}.")
                except Exception as e:
                    print(f"Error closing socket for {disconnected_nickname}: {e}")
                break
        
        # If a client was actually removed
        if disconnected_nickname != "Unknown":
            print(f"Client {disconnected_nickname} disconnected. Active clients: {len(clients)}")
            # Broadcast the disconnection message to remaining clients
            disconnect_message = f"{disconnected_nickname} has left the chat.".encode('utf-8')
            broadcast(disconnect_message)
        else:
            # This case might happen if client was already removed due to an error
            # or if `remove_client` was called on a non-existent socket.
            print(f"Attempted to remove non-existent client socket.")


def handle_client(client_socket, client_address):
    """
    Handles a single client connection.
    This function runs in its own thread for each connected client.
    """
    print(f"New connection from {client_address}")
    
    nickname = "Guest" # Default nickname for new connections

    try:
        # Prompt the client for a nickname. The client is expected to send
        # a message starting with "NICK:"
        client_socket.sendall("WELCOME! Please type NICK:YourName and press Enter.\n".encode('utf-8'))
        
        # Wait for the client to send their nickname
        nick_message_raw = client_socket.recv(1024)
        if not nick_message_raw:
            # Client disconnected before sending nickname
            raise ConnectionResetError("Client disconnected during nickname setup.")

        nick_message = nick_message_raw.decode('utf-8').strip()
        if nick_message.startswith("NICK:"):
            nickname = nick_message[5:].strip()
            if not nickname: # If they just sent "NICK:"
                nickname = f"Guest_{client_address[1]}"
        else:
            nickname = f"Guest_{client_address[1]}" # Assign generic nickname if no NICK command

        # Add the new client to the global list
        with clients_lock:
            clients.append((client_socket, nickname))
        
        print(f"Client {client_address} identified as {nickname}. Total clients: {len(clients)}")
        
        # Inform all clients that a new user has joined
        join_message = f"{nickname} has joined the chat!".encode('utf-8')
        broadcast(join_message)
        client_socket.sendall(f"Welcome, {nickname}! You are now in the chat.\n".encode('utf-8'))


        # Main loop to receive messages from this client
        while True:
            try:
                message = client_socket.recv(1024) # Receive up to 1024 bytes
                if not message:
                    # If no message is received (empty bytes), client has disconnected
                    print(f"Client {nickname} ({client_address}) disconnected.")
                    break
                
                # Decode the message, prepend sender's nickname, and re-encode for broadcasting
                decoded_message = message.decode('utf-8').strip()
                full_message = f"{nickname}: {decoded_message}".encode('utf-8')
                print(f"[{nickname}] {decoded_message}")
                
                # Broadcast the message to all other clients
                broadcast(full_message, client_socket)
            
            except ConnectionResetError:
                # Client abruptly closed the connection (e.g., Ctrl+C in netcat)
                print(f"Client {nickname} ({client_address}) forcibly disconnected.")
                break
            except socket.error as e:
                # Other socket errors, indicates a problem with the connection
                print(f"Socket error with {nickname} ({client_address}): {e}")
                break
            except Exception as e:
                # Catch any other unexpected errors in the client loop
                print(f"Error in handle_client loop for {nickname} ({client_address}): {e}")
                break
    
    except socket.error as e:
        print(f"Initial connection error or client disconnected during setup for {client_address}: {e}")
    except ConnectionResetError as e:
        print(f"{e} for {client_address}.")
    except Exception as e:
        # Catch any other unexpected errors during client setup
        print(f"Unexpected error during client setup for {client_address}: {e}")
    finally:
        # Ensure client is removed and socket is closed once the thread finishes
        remove_client(client_socket)


def start_server():
    """
    Starts the main server, binds to the specified host and port,
    listens for incoming connections, and spawns a new thread for each client.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # SO_REUSEADDR allows the server to rebind to the same address immediately
    # after it has been closed, without waiting for a timeout.
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((HOST, PORT))
        server.listen() # Start listening for incoming connections
        print(f"Chat server listening on {HOST}:{PORT}")
    except socket.error as e:
        print(f"Failed to start server: {e}")
        sys.exit(1) # Exit if the server can't start

    try:
        while True:
            # Accept a new connection. This is a blocking call.
            client_socket, client_address = server.accept()
            # Start a new thread to handle this client. This allows the server
            # to continue accepting new connections while handling existing ones.
            client_handler = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address)
            )
            # Daemon threads exit automatically when the main program exits.
            client_handler.daemon = True 
            client_handler.start()
    except KeyboardInterrupt:
        print("\nServer shutting down due to KeyboardInterrupt.")
    except Exception as e:
        print(f"An unexpected error occurred in the main server loop: {e}")
    finally:
        server.close() # Close the server's listening socket
        print("Server socket closed.")
        # Attempt to close all client sockets upon server shutdown
        with clients_lock:
            for client_socket, nickname in list(clients): # Iterate over a copy
                try:
                    client_socket.close()
                    print(f"Closed client socket for {nickname} during shutdown.")
                except Exception as e:
                    print(f"Error closing client socket for {nickname} during shutdown: {e}")
            clients.clear() # Clear the list of clients


if __name__ == "__main__":
    # This block ensures that `start_server()` is called only when the script
    # is executed directly, not when imported as a module.
    start_server()
