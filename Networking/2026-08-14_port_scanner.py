"""
This script implements a basic port scanner.
It takes a target IP address or hostname and a range of ports,
then attempts to connect to each port to determine if it is open.

Usage:
    python port_scanner.py --target <IP_or_HOSTNAME> --ports <PORT_RANGE_or_LIST> [--timeout <SECONDS>]

Examples:
    Scan common web ports on example.com:
        python port_scanner.py --target example.com --ports 80,443

    Scan a range of ports on a local IP:
        python port_scanner.py --target 127.0.0.1 --ports 1-1024

    Scan a specific port with a longer timeout:
        python port_scanner.py --target myhost.local --ports 22 --timeout 2
"""

import socket
import argparse
import sys

def is_port_open(target_ip: str, port: int, timeout: float) -> bool:
    """
    Checks if a single port on the target IP is open.

    Args:
        target_ip (str): The IP address of the target.
        port (int): The port number to check.
        timeout (float): The maximum time in seconds to wait for a connection.

    Returns:
        bool: True if the port is open, False otherwise.
    """
    # Create a new socket. AF_INET refers to the address family IPv4.
    # SOCK_STREAM refers to the socket type TCP.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)  # Set a timeout for the connection attempt

    try:
        # connect_ex is like connect, but returns an error indicator instead of raising an exception
        # if the connection cannot be made. 0 means success.
        result = sock.connect_ex((target_ip, port))
        if result == 0:
            return True
        else:
            return False
    except socket.gaierror:
        # This error typically means the hostname could not be resolved.
        # It should ideally be caught before this function is called, but included for robustness.
        # print(f"Error: Hostname {target_ip} could not be resolved.")
        return False
    except socket.error as e:
        # Other socket-related errors (e.g., connection refused, network unreachable).
        # For a port scanner, we generally treat these as the port not being open/accessible.
        # print(f"Error checking port {port}: {e}") # Uncomment for verbose debugging
        return False
    finally:
        sock.close() # Always close the socket to free up resources


def parse_port_range(port_arg: str) -> list[int]:
    """
    Parses a string representing ports or port ranges into a list of integers.
    Handles formats like "80,443", "1-1024", or "22,80,100-200".

    Args:
        port_arg (str): The string representing port(s) to scan.

    Returns:
        list[int]: A sorted list of unique port numbers.

    Raises:
        ValueError: If the port string is invalid.
    """
    ports = set() # Use a set to automatically handle unique ports and avoid duplicates
    parts = port_arg.split(',')

    for part in parts:
        part = part.strip()
        if '-' in part:
            # Handle port range (e.g., "1-1024")
            try:
                start, end = map(int, part.split('-'))
                if not (1 <= start <= 65535 and 1 <= end <= 65535 and start <= end):
                    raise ValueError(f"Invalid port range: {part}. Ports must be between 1 and 65535, and start <= end.")
                ports.update(range(start, end + 1))
            except ValueError as e:
                raise ValueError(f"Invalid port range format '{part}': {e}. Expected 'start-end' with valid numbers.")
        else:
            # Handle single port (e.g., "80")
            try:
                port = int(part)
                if not (1 <= port <= 65535):
                    raise ValueError(f"Invalid port number: {port}. Port must be between 1 and 65535.")
                ports.add(port)
            except ValueError as e:
                raise ValueError(f"Invalid single port format '{part}': {e}. Expected a number.")
    
    return sorted(list(ports))


def main():
    """
    Main function to parse arguments and initiate the port scan.
    """
    parser = argparse.ArgumentParser(
        description="A simple Python port scanner.",
        formatter_class=argparse.RawTextHelpFormatter # Preserve docstring formatting for help message
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Target IP address or hostname (e.g., 'example.com', '192.168.1.1')"
    )
    parser.add_argument(
        "--ports",
        required=True,
        help="Ports to scan (e.g., '80,443,22', '1-1024', '1,50-100,443')"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=1.0, # Default timeout of 1 second per port
        help="Connection timeout in seconds for each port (default: 1.0)"
    )

    args = parser.parse_args()

    target_host = args.target
    scan_timeout = args.timeout

    print(f"[*] Scanning target: {target_host}")
    print(f"[*] Timeout per port: {scan_timeout} seconds")

    try:
        # Resolve hostname to IP address if a hostname is provided.
        # This is crucial because socket operations generally require an IP address.
        target_ip = socket.gethostbyname(target_host)
        print(f"[*] Resolved {target_host} to IP: {target_ip}")
    except socket.gaierror:
        print(f"[-] Error: Could not resolve hostname '{target_host}'. Please check the hostname or IP address.")
        sys.exit(1) # Exit if hostname cannot be resolved

    try:
        ports_to_scan = parse_port_range(args.ports)
        # Display the parsed ports in a readable format, handling potentially large lists
        display_ports = ', '.join(map(str, ports_to_scan[:10]))
        if len(ports_to_scan) > 10:
            display_ports += f", ... (total {len(ports_to_scan)} ports)"
        print(f"[*] Ports to scan: {display_ports}")
    except ValueError as e:
        print(f"[-] Error: {e}")
        sys.exit(1) # Exit if port range is invalid

    open_ports = []
    total_ports = len(ports_to_scan)
    print(f"\n[+] Starting scan for {total_ports} ports on {target_ip}...")

    # Iterate through each port and check if it's open
    for i, port in enumerate(ports_to_scan):
        # Print progress update on the same line using carriage return '\r'
        # sys.stdout.write ensures immediate output without buffering.
        sys.stdout.write(f"\r[*] Progress: {i+1}/{total_ports} ports checked ({((i+1)/total_ports)*100:.1f}%)")
        sys.stdout.flush()

        if is_port_open(target_ip, port, scan_timeout):
            # When a port is found open, print it on a new line.
            # We clear the current progress line using '\r' and then print.
            # Then we can resume the progress indicator after the message.
            sys.stdout.write(f"\r[+] Port {port:<5} is OPEN{' ' * 40}\n") # Clear rest of the line with spaces
            sys.stdout.flush()
            open_ports.append(port)
        # else:
            # For a basic scanner, we often only report open ports to keep output clean.
            # Uncomment the line below for verbose output showing closed/filtered ports.
            # sys.stdout.write(f"\r[-] Port {port:<5} is CLOSED/FILTERED{' ' * 20}\n")
            # sys.stdout.flush()

    # Ensure a newline character is printed after the loop finishes,
    # so the next output starts on a new line after the final progress update.
    sys.stdout.write("\n") 

    print("\n[=== Scan Results ===]")
    if open_ports:
        print(f"[+] Found {len(open_ports)} open port(s) on {target_ip}:")
        for port in open_ports:
            try:
                # Attempt to guess common service based on port number for better output.
                # getservbyport can raise OSError if service is unknown.
                service_name = socket.getservbyport(port, "tcp")
            except OSError:
                service_name = "Unknown Service"
            print(f"    - Port {port} ({service_name})")
    else:
        print(f"[-] No open ports found on {target_ip} in the specified range.")
    print("[====================]")


if __name__ == "__main__":
    # To run this script, save it as (e.g.) `port_scanner.py`
    # and execute it from your terminal using one of the following commands:

    # Example 1: Scan common web ports (80 for HTTP, 443 for HTTPS, 22 for SSH)
    # on a publicly accessible domain (scanme.nmap.org is provided by Nmap for testing purposes).
    # python port_scanner.py --target scanme.nmap.org --ports 80,443,22

    # Example 2: Scan a range of ports (from 1 to 100) on your local machine (localhost).
    # This might show some ports open if you have services running locally (e.g., web server, database).
    # python port_scanner.py --target 127.0.0.1 --ports 1-100

    # Example 3: Scan a specific port (e.g., 3306 for MySQL) with a longer timeout of 2.5 seconds.
    # python port_scanner.py --target localhost --ports 3306 --timeout 2.5
    
    # Note: Scanning many ports on a remote host can take a significant amount of time
    # due to the sequential nature of this script and the timeout applied to each port.
    # For speed, professional port scanners often use multi-threading or asynchronous operations.
    
    main()
