"""
This script implements a simple HTTP server using Python's standard library.
It serves files from the directory where it is run, making it ideal for quickly
sharing local files or testing web content locally.

To use:
1. Save this script as, e.g., `simple_server.py`.
2. Open a terminal or command prompt.
3. Navigate to the directory containing the files you want to serve.
4. Run the script: `python simple_server.py` (or `python simple_server.py 8080` to specify a port)
5. Open your web browser and go to `http://localhost:8000` (or the address printed).
6. To stop the server, press `Ctrl+C` in the terminal.
"""

import http.server
import socketserver
import sys

# Define the default port the server will listen on.
# Port 8000 is a common default for local development servers.
# You can change this to any available port number (e.g., 8080, 5000).
DEFAULT_PORT = 8000

# Define the host address.
# "0.0.0.0" makes the server accessible from any IP address on the network.
# Use "127.0.0.1" or "localhost" if you only want it accessible from your own machine.
DEFAULT_HOST = "0.0.0.0"

def start_server(host=DEFAULT_HOST, port=DEFAULT_PORT):
    """
    Starts a simple HTTP server that serves files from the current directory.
    """
    # Set the handler for the HTTP requests.
    # SimpleHTTPRequestHandler serves files relative to the current working directory
    # where the script is executed. It automatically handles GET requests for files
    # and directory listings.
    Handler = http.server.SimpleHTTPRequestHandler

    # Create a TCPServer instance.
    # socketserver.TCPServer handles the low-level network communication (TCP sockets).
    # It binds to the specified (host, port) and uses our Handler to process requests.
    try:
        with socketserver.TCPServer((host, port), Handler) as httpd:
            print(f"Serving HTTP on {host} port {port} (http://localhost:{port}/)")
            print("Press Ctrl+C to stop the server.")
            
            # Start the server and keep it running indefinitely.
            # It will handle incoming requests until a KeyboardInterrupt (Ctrl+C) occurs.
            httpd.serve_forever()
    except OSError as e:
        # Handle cases where the port might already be in use or permissions are insufficient.
        print(f"Error: Could not start server on port {port}. {e}", file=sys.stderr)
        print("Perhaps another program is using the port, or you lack permissions (e.g., trying to use a privileged port like 80).", file=sys.stderr)
        print("Try a different port (e.g., `python simple_server.py 8080`) or check if a process is already running.", file=sys.stderr)
        sys.exit(1) # Exit with an error code to indicate failure
    except KeyboardInterrupt:
        # Gracefully handle server shutdown when Ctrl+C is pressed.
        print("\nServer stopped.")
        sys.exit(0) # Exit cleanly

if __name__ == "__main__":
    # Example usage:
    # Run the server with default host and port, or with a specified port
    # from command-line arguments.

    port_to_use = DEFAULT_PORT

    # Check if a port number was provided as a command-line argument.
    # sys.argv[0] is the script name itself. sys.argv[1] would be the first argument.
    if len(sys.argv) > 1:
        try:
            # Attempt to convert the first argument to an integer.
            arg_port = int(sys.argv[1])
            # Validate the port number to be within a reasonable range (non-privileged ports).
            if 1024 <= arg_port <= 65535:
                port_to_use = arg_port
            else:
                print(f"Warning: Port {arg_port} is outside the common user range (1024-65535). Using default port {DEFAULT_PORT}.", file=sys.stderr)
        except ValueError:
            # If the argument is not a valid integer, print a warning.
            print(f"Warning: Invalid port number '{sys.argv[1]}'. Using default port {DEFAULT_PORT}.", file=sys.stderr)
    
    # Start the server with the determined host and port.
    start_server(host=DEFAULT_HOST, port=port_to_use)
