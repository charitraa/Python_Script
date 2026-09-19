#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# To run this script, you need to install the 'psutil' library.
# You can install it using pip:
# pip install psutil

"""
This script monitors and displays network bandwidth usage in real-time.
It shows the current upload and download speeds, as well as the total
data uploaded and downloaded during the monitoring period.

It uses the `psutil` library to get network I/O statistics, making it
cross-platform. The output is formatted into human-readable units
(KB, MB, GB, etc.).

The monitoring can be set for a specific duration or run continuously
until the user stops it with Ctrl+C.
"""

import psutil
import time

def bytes_to_human_readable(n_bytes):
    """
    Converts a number of bytes into a human-readable string (e.g., 1.2 GB).

    Args:
        n_bytes (int): The number of bytes to convert.

    Returns:
        str: A string representing the bytes in human-readable format.
    """
    symbols = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    prefix = {}
    # Populate prefixes for powers of 1024
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i * 10) # 1 KB = 1024 B, 1 MB = 1024 KB, etc.

    # Iterate from largest unit to smallest to find the most appropriate one
    for s in reversed(symbols):
        if n_bytes >= prefix[s]:
            value = float(n_bytes) / prefix[s]
            # Format to two decimal places
            return f"{value:.2f} {s}"
    # If less than 1 KB, display in Bytes
    return f"{n_bytes} B"

def monitor_bandwidth(interval=1, duration=60):
    """
    Monitors and displays network bandwidth usage over a specified duration.

    Args:
        interval (int): The time in seconds between each data collection and display update.
                        Defaults to 1 second.
        duration (int): The total time in seconds to monitor. Set to 0 or a negative
                        value for continuous monitoring until interrupted by the user (Ctrl+C).
                        Defaults to 60 seconds.
    """
    print("--- Bandwidth Usage Monitor ---")
    print(f"Monitoring every {interval} second(s).")
    if duration > 0:
        print(f"Total monitoring duration set to: {duration} second(s).")
    else:
        print("Monitoring continuously until Ctrl+C is pressed.")
    print("-" * 30)
    print("Time | Upload Speed     | Download Speed   | Total Upload     | Total Download")
    print("-" * 79)

    # Get initial network statistics to establish a baseline.
    # psutil.net_io_counters(pernic=False) returns global statistics
    # for all network interfaces combined.
    initial_net_stats = psutil.net_io_counters(pernic=False)
    # Store initial total bytes sent and received for overall calculation later.
    bytes_sent_at_script_start = initial_net_stats.bytes_sent
    bytes_recv_at_script_start = initial_net_stats.bytes_recv

    # 'old_net_stats' will store the stats from the previous interval for delta calculation.
    old_net_stats = initial_net_stats

    # Variables to keep track of total usage *during the monitoring period*.
    total_bytes_sent_in_period = 0
    total_bytes_recv_in_period = 0

    # Record the start time of the monitoring to calculate elapsed time.
    start_time = time.time()
    # 'last_check_time' tracks when the last stats snapshot was taken for accurate interval calculation.
    last_check_time = start_time

    try:
        while True:
            current_time = time.time()
            # Calculate total elapsed time since the monitor started.
            elapsed_total = current_time - start_time

            # If a specific duration is set, check if it has been exceeded.
            if duration > 0 and elapsed_total >= duration:
                print("\nMonitoring duration completed.")
                break # Exit the loop

            # Calculate how long to sleep to maintain the desired 'interval'.
            # This adjusts for the time taken by the code execution itself.
            time_to_sleep = interval - (current_time - last_check_time)
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)
            
            # Record the actual time after sleeping (or immediately if no sleep was needed).
            new_check_time = time.time()
            # Calculate the actual time that elapsed since the last statistics check.
            actual_interval = new_check_time - last_check_time
            # Update 'last_check_time' for the next iteration.
            last_check_time = new_check_time

            # Get the current network statistics.
            new_net_stats = psutil.net_io_counters(pernic=False)

            # Calculate the difference (delta) in bytes sent and received
            # between the current snapshot and the previous one.
            bytes_sent_delta = new_net_stats.bytes_sent - old_net_stats.bytes_sent
            bytes_recv_delta = new_net_stats.bytes_recv - old_net_stats.bytes_recv

            # Accumulate total usage for the current monitoring period.
            total_bytes_sent_in_period += bytes_sent_delta
            total_bytes_recv_in_period += bytes_recv_delta

            # Calculate speeds (bytes per second).
            # Avoid division by zero if 'actual_interval' is somehow zero or very small.
            sent_speed = bytes_sent_delta / actual_interval if actual_interval > 0 else 0
            recv_speed = bytes_recv_delta / actual_interval if actual_interval > 0 else 0

            # Print current statistics, formatted for readability.
            # We use string formatting to align columns nicely.
            print(
                f"{elapsed_total:5.1f}s | "
                f"{bytes_to_human_readable(sent_speed):<15}/s | " # Left-align and pad
                f"{bytes_to_human_readable(recv_speed):<15}/s | " # Left-align and pad
                f"{bytes_to_human_readable(total_bytes_sent_in_period):<15} | " # Left-align and pad
                f"{bytes_to_human_readable(total_bytes_recv_in_period):<15}" # Left-align and pad
            )

            # Update 'old_net_stats' for the next iteration's delta calculation.
            old_net_stats = new_net_stats

    except KeyboardInterrupt:
        # Catch Ctrl+C to allow for a clean exit and final summary.
        print("\nMonitoring stopped by user (Ctrl+C).")
    except Exception as e:
        # Catch any other unexpected errors.
        print(f"\nAn unexpected error occurred: {e}")

    finally:
        # This block always executes, whether the loop finished naturally or was interrupted.
        print("-" * 79)
        # Get final network stats to calculate overall totals since the script began.
        final_net_stats = psutil.net_io_counters(pernic=False)
        overall_total_bytes_sent = final_net_stats.bytes_sent - bytes_sent_at_script_start
        overall_total_bytes_recv = final_net_stats.bytes_recv - bytes_recv_at_script_start
        
        # Print a summary of total usage.
        print(f"Overall Total Sent (since script start): {bytes_to_human_readable(overall_total_bytes_sent)}")
        print(f"Overall Total Received (since script start): {bytes_to_human_readable(overall_total_bytes_recv)}")
        print("--- End of Monitor ---")

if __name__ == "__main__":
    # Example usage: Run the monitor for 15 seconds, updating every 1 second.
    # To run continuously until Ctrl+C, set duration to 0 or a negative value:
    # monitor_bandwidth(interval=1, duration=0)
    
    print("Starting bandwidth monitor for 15 seconds. Press Ctrl+C to stop early.")
    monitor_bandwidth(interval=1, duration=15)
    
    # You can also run it continuously if you uncomment the line below
    # and comment out the previous monitor_bandwidth call.
    # print("\nStarting continuous bandwidth monitor. Press Ctrl+C to stop.")
    # monitor_bandwidth(interval=2, duration=0)
