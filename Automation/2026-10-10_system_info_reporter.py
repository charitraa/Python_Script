"""
A comprehensive System Information Reporter script.

This script gathers and displays various details about the operating system,
hardware, network, and Python environment. It provides an easy-to-understand
overview of the system it's run on.

It uses standard Python libraries like `platform`, `sys`, `os`, `socket`,
and the well-known third-party library `psutil` for more detailed hardware
statistics (CPU, memory, disk).
"""

# Import necessary modules from the standard library.
import platform
import sys
import os
import socket
import datetime

# For detailed CPU, memory, and disk usage, we use 'psutil'.
# If you don't have it, install it using pip:
# pip install psutil
import psutil

def bytes_to_human_readable(num_bytes):
    """
    Converts a number of bytes into a human-readable string (e.g., 1024 MB -> 1 GB).
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} EB" # For extremely large numbers, should be rare

def get_system_info():
    """
    Gathers various system information and returns it as a dictionary.
    """
    info = {}

    # --- General System Information ---
    info["Operating System"] = platform.system()
    info["OS Release"] = platform.release()
    info["OS Version"] = platform.version()
    info["Architecture"] = platform.machine()
    info["System Node (Hostname)"] = platform.node()
    info["Processor Type"] = platform.processor()

    # --- Network Information ---
    try:
        hostname = socket.gethostname()
        info["Local Hostname"] = hostname
        info["Local IP Address"] = socket.gethostbyname(hostname)
    except socket.error as e:
        info["Local Hostname"] = "N/A"
        info["Local IP Address"] = f"Error: {e}"

    # --- Python Environment Information ---
    info["Python Version"] = sys.version.replace('\n', ' ')
    info["Python Executable"] = sys.executable
    info["Current Working Directory"] = os.getcwd()

    # --- User Information ---
    try:
        info["Current User"] = os.getlogin()
    except OSError:
        # os.getlogin() can fail in non-interactive environments (e.g., cron jobs).
        # Fallback to environment variables.
        info["Current User"] = os.environ.get('USER') or os.environ.get('USERNAME') or 'N/A'

    # --- Hardware Information using psutil ---
    # CPU
    info["CPU Logical Cores"] = psutil.cpu_count(logical=True)
    info["CPU Physical Cores"] = psutil.cpu_count(logical=False)
    # psutil.cpu_percent with interval=1 samples CPU usage for 1 second.
    info["CPU Usage (%)"] = psutil.cpu_percent(interval=1) 

    # Memory
    mem = psutil.virtual_memory()
    info["Total Memory"] = bytes_to_human_readable(mem.total)
    info["Available Memory"] = bytes_to_human_readable(mem.available)
    info["Used Memory"] = bytes_to_human_readable(mem.used)
    info["Memory Usage (%)"] = f"{mem.percent}%"

    # Disk Usage (for the root partition or current drive)
    try:
        # Determine the root partition path based on OS for cross-platform compatibility.
        if platform.system() == "Windows":
            disk_path = "C:\\"
        else:
            disk_path = "/"
        
        disk = psutil.disk_usage(disk_path)
        info[f"Disk Total ({disk_path})"] = bytes_to_human_readable(disk.total)
        info[f"Disk Used ({disk_path})"] = bytes_to_human_readable(disk.used)
        info[f"Disk Free ({disk_path})"] = bytes_to_human_readable(disk.free)
        info[f"Disk Usage (%) ({disk_path})"] = f"{disk.percent}%"
    except Exception as e:
        # Catch any errors during disk info retrieval, e.g., if path doesn't exist.
        info["Disk Information"] = f"Could not retrieve disk info for {disk_path}: {e}"

    # Boot Time
    info["System Boot Time"] = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")

    return info

def report_system_info(info_dict):
    """
    Prints the gathered system information in a formatted, readable way.
    """
    print("=" * 40)
    print("  SYSTEM INFORMATION REPORT")
    print("=" * 40)
    print(f"Report Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Define sections and the keys that belong to each for structured output.
    sections = {
        "General System Info": ["Operating System", "OS Release", "OS Version", "Architecture", "System Node (Hostname)", "Processor Type"],
        "Network Info": ["Local Hostname", "Local IP Address"],
        "Python Environment": ["Python Version", "Python Executable", "Current Working Directory"],
        "User Info": ["Current User"],
        "CPU Info": ["CPU Logical Cores", "CPU Physical Cores", "CPU Usage (%)"],
        "Memory Info": ["Total Memory", "Available Memory", "Used Memory", "Memory Usage (%)"],
        # Dynamically find disk keys because the key name changes based on the disk path.
        "Disk Info": [key for key in info_dict if key.startswith("Disk")], 
        "System Uptime": ["System Boot Time"]
    }

    for section_title, keys in sections.items():
        print(f"\n--- {section_title} ---")
        for key in keys:
            if key in info_dict:
                # Align values for better readability using string formatting.
                print(f"{key.ljust(30)}: {info_dict[key]}")

if __name__ == "__main__":
    # This block ensures the code runs only when the script is executed directly,
    # not when it's imported as a module into another script.
    # It demonstrates how to use the functions defined above.

    print("Gathering system information... Please wait.")
    
    # 1. Call the function to gather all the system details into a dictionary.
    system_details = get_system_info()
    
    # 2. Call the function to print the gathered information in a user-friendly format.
    report_system_info(system_details)
    
    print("\nInformation gathering complete.")
