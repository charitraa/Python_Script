"""
A simple, beginner-friendly Python script to perform a network ping sweep.

This script identifies active hosts within a given IP network range by sending
ICMP echo requests (pings) to each IP address and checking for responses.
It utilizes the system's native 'ping' command via subprocess and concurrent
execution for speed.

Usage:
    Run the script directly. It can accept a network range as a command-line
    argument (e.g., "192.168.1.0/24"). If no argument is provided, it uses
    a small default range for demonstration.
"""

import subprocess
import ipaddress
import platform
import concurrent.futures
import sys

def is_host_up(ip_address: str, timeout: int = 1) -> bool:
    """
    Checks if a single host is reachable (responds to a ping).

    Args:
        ip_address (str): The IP address of the host to ping.
        timeout (int): The timeout in seconds for the ping command.

    Returns:
        bool: True if the host is reachable, False otherwise.
    """
    # Determine the ping command based on the operating system
    current_os = platform.system()
    ping_command = []

    if current_os == "Windows":
        # Windows uses '-n' for count and '-w' for timeout in milliseconds
        ping_command = ["ping", "-n", "1", "-w", str(timeout * 1000), ip_address]
    else:
        # Linux/macOS use '-c' for count and '-W' for timeout in seconds
        ping_command = ["ping", "-c", "1", "-W", str(timeout), ip_address]

    try:
        # Execute the ping command
        # subprocess.run returns a CompletedProcess object
        # `capture_output=True` captures stdout and stderr
        # `text=True` decodes stdout/stderr as text
        # `check=False` prevents an exception for non-zero exit codes (e.g., host unreachable)
        # `timeout` here is for the subprocess itself, slightly longer than ping's internal timeout.
        process = subprocess.run(
            ping_command,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout + 1 # Give a little extra time for the subprocess to complete
        )

        # A return code of 0 usually indicates success, but we also check output for robustness.
        if process.returncode == 0:
            # Additional check: Look for specific success strings in the output
            if current_os == "Windows":
                # On Windows, "Reply from" indicates a successful ping
                return "Reply from" in process.stdout
            else: # Linux/macOS
                # On Linux/macOS, "1 received" indicates a successful ping
                return "1 received" in process.stdout
        return False # If return code is not 0, or success string not found
    except subprocess.TimeoutExpired:
        # This occurs if the subprocess itself times out before ping finishes
        return False
    except FileNotFoundError:
        print(f"Error: 'ping' command not found. Please ensure ping is installed and in your system's PATH.", file=sys.stderr)
        return False
    except Exception as e:
        # Catch other potential errors during subprocess execution
        print(f"Error pinging {ip_address}: {e}", file=sys.stderr)
        return False

def ping_sweep(network_range: str, max_workers: int = 50) -> list[str]:
    """
    Performs a ping sweep on a given network range to find active hosts.

    Args:
        network_range (str): The IP network range to sweep (e.g., "192.168.1.0/24").
                             Only IPv4 is directly supported by the current ping command structure.
        max_workers (int): The maximum number of threads to use for concurrent pings.
                           Adjust this value based on your system's resources and network conditions.

    Returns:
        list[str]: A sorted list of IP addresses of active hosts found in the range.
    """
    active_hosts = []
    print(f"Starting ping sweep on network: {network_range}")

    try:
        # Parse the network range using ipaddress module
        # strict=False allows for network addresses like "192.168.1.1/24" which it
        # then normalizes to "192.168.1.0/24".
        network = ipaddress.ip_network(network_range, strict=False)
    except ValueError as e:
        print(f"Error: Invalid network range '{network_range}'. {e}", file=sys.stderr)
        return []

    # Prepare a list of all *host* IP addresses in the network.
    # The `hosts()` method automatically excludes network and broadcast addresses
    # for conventional subnets (e.g., /24), but includes all for /31 or /32.
    ip_addresses = [str(ip) for ip in network.hosts()]

    if not ip_addresses:
        print(f"No host IPs found in the range {network_range} for scanning.", file=sys.stderr)
        return []

    # Use ThreadPoolExecutor for concurrent execution
    # This significantly speeds up the sweep by pinging multiple hosts simultaneously.
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Map the is_host_up function to each IP address, creating a future for each.
        future_to_ip = {executor.submit(is_host_up, ip): ip for ip in ip_addresses}

        for i, future in enumerate(concurrent.futures.as_completed(future_to_ip)):
            ip = future_to_ip[future]
            try:
                if future.result():
                    active_hosts.append(ip)
                    # Provide immediate feedback for active hosts and update progress
                    sys.stdout.write(f"\r{ip} is UP! ({len(active_hosts)} active hosts found so far)           ")
                    sys.stdout.flush()
                # Optionally, for a cleaner output, only print active hosts
                # else:
                #     sys.stdout.write(f"\r{ip} is DOWN.                               ")
                #     sys.stdout.flush()

            except Exception as exc:
                print(f"\nError processing {ip}: {exc}", file=sys.stderr)

            # Update general progress on the same line
            # Ensure the line is long enough to clear previous messages
            sys.stdout.write(f"\rScanning... {i+1}/{len(ip_addresses)} IPs checked. {len(active_hosts)} active.   ")
            sys.stdout.flush()

        print("\nScan complete.") # New line after the final progress update

    # Sort the found active hosts numerically for cleaner output
    return sorted(active_hosts, key=lambda ip: ipaddress.ip_address(ip))


if __name__ == "__main__":
    # Example Usage:
    # You can provide a network range as a command-line argument,
    # or use a default one.
    #
    # To find your local network range, you can often infer it from your IP address
    # (e.g., if your IP is 192.168.1.10, your network might be "192.168.1.0/24").
    # For demonstration, a small, safe range (like localhost or your gateway)
    # is often best to avoid long scan times or scanning unintended networks.
    #
    # Example for a small test:
    # network_to_sweep = "127.0.0.1/30" # This covers 127.0.0.0, 127.0.0.1, 127.0.0.2, 127.0.0.3
    #
    # Example for a typical local network (replace with your actual network if you know it):
    # network_to_sweep = "192.168.1.0/24" # Common home network
    # network_to_sweep = "10.0.0.0/24"   # Another common home/office network

    # Default network range if no argument is provided
    # Using a small, safe range for the default example, typically includes localhost.
    default_network = "127.0.0.0/29" # Covers 127.0.0.0 to 127.0.0.7 - good for testing!

    if len(sys.argv) > 1:
        network_to_sweep = sys.argv[1]
    else:
        network_to_sweep = default_network
        print(f"No network range provided. Using default: {network_to_sweep}")
        print("Usage: python ping_sweep_tool.py <network_range>")
        print("Example: python ping_sweep_tool.py 192.168.1.0/24")
        print("-" * 30)

    print(f"Initiating ping sweep for: {network_to_sweep}")
    active_hosts = ping_sweep(network_to_sweep)

    if active_hosts:
        print("\n\n--- Active Hosts Found ---")
        for host in active_hosts:
            print(f"  - {host}")
    else:
        print("\n\nNo active hosts found in the specified range.")
    print("\nScript finished.")
