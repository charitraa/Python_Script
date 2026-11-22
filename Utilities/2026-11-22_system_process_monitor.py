# pip install psutil

import psutil
import time
import os

"""
This script provides a real-time system process monitor, displaying key information
about active processes such as their Process ID (PID), Name, CPU usage percentage,
and Memory usage percentage. It refreshes the display periodically, sorting processes
by CPU usage to highlight resource-intensive tasks.

It requires the 'psutil' library, which can be installed via pip:
pip install psutil
"""

def get_process_info(p):
    """
    Attempts to retrieve a process's PID, name, CPU%, and Memory%.
    Handles various psutil exceptions that can occur for transient processes
    or access denied situations.
    """
    try:
        # Using p.oneshot() context manager to fetch multiple process attributes
        # efficiently and avoid race conditions if the process terminates
        # between individual attribute calls.
        with p.oneshot():
            pid = p.pid
            name = p.name()
            # cpu_percent() calculates usage since the last call or process creation.
            # The very first call will typically return 0.0.
            cpu_percent = p.cpu_percent(interval=None) 
            memory_percent = p.memory_percent()
        
        return {
            'pid': pid,
            'name': name,
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        # These exceptions occur when a process no longer exists,
        # access is denied (e.g., for system processes), or it's a zombie.
        # In such cases, we return None to skip this process.
        return None
    except Exception:
        # Catch any other unexpected errors during information retrieval.
        return None

def monitor_processes(interval=2, top_n=20):
    """
    Monitors system processes, displaying PID, Name, CPU usage, and Memory usage.
    Refreshes the display periodically.

    Args:
        interval (int): The time in seconds to wait between refreshing the display.
        top_n (int): The number of top processes (by CPU usage) to display.
                     Set to 0 or a very large number to display all.
    """
    # Prime the psutil library for CPU percentage calculation.
    # The first call to psutil.cpu_percent() (either global or per-process)
    # returns 0.0, as there's no previous baseline to compare against.
    # By calling it once here, subsequent calls within the loop will provide
    # meaningful values reflecting usage over the given 'interval'.
    psutil.cpu_percent(interval=0.1) 

    print("Starting System Process Monitor. Press Ctrl+C to stop.")

    try:
        while True:
            # Clear the console for a clean, refreshed display.
            # 'cls' for Windows, 'clear' for Linux/macOS.
            os.system('cls' if os.name == 'nt' else 'clear')

            print(f"--- System Process Monitor (Refresh every {interval}s) ---")
            print(f"{'PID':<7} {'Name':<30} {'CPU%':<8} {'Memory%':<10}")
            print("-" * 60)

            processes_data = []
            # Iterate over all running processes
            for p in psutil.process_iter():
                info = get_process_info(p)
                if info:
                    processes_data.append(info)

            # Sort processes by CPU usage in descending order
            processes_data.sort(key=lambda x: x['cpu_percent'], reverse=True)

            # Display the top N processes (or all if top_n is 0 or too large)
            for p_info in processes_data[:top_n if top_n > 0 else len(processes_data)]:
                # Print formatted process information
                print(f"{p_info['pid']:<7} {p_info['name']:<30} {p_info['cpu_percent']:<8.2f} {p_info['memory_percent']:<10.2f}")

            # Wait for the specified interval before the next refresh
            time.sleep(interval)

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nMonitoring stopped by user.")
    except Exception as e:
        # Catch any other unexpected errors during the monitoring loop
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    # Example usage:
    # Monitor processes, refreshing every 2 seconds and showing the top 15 processes.
    monitor_processes(interval=2, top_n=15)
