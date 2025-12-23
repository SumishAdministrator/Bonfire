#!/usr/bin/env python3
"""
File Name  : fa_metrics_systemhealth.py
Purpose    : Collect system health metrics (CPU, Memory, Disk, Uptime)
Platforms  : Windows, Linux, macOS
Dependency : psutil
"""


import psutil
import platform
import socket
import os
import sys
from datetime import datetime, timedelta


# ------------------------------------------------------------
# Step-1: Python Availability & Version | Optional
# ------------------------------------------------------------
def get_python_version():
    # Python must already be present to run this script
    return sys.version.replace("\n", " ")
   

# ------------------------------------------------------------
# Step-2.1: OS Type, Release Version & Hostname
# ------------------------------------------------------------
def get_os_type():
    return platform.system()

def get_os_version():
    return platform.version()

def get_hostname():
    return socket.gethostname()


# ------------------------------------------------------------
#Step-2.2: Disk Path (OS Specific)
# ------------------------------------------------------------
def get_disk_path(os_type):
    if os_type == "Windows":
        return r"C:\ProgramData\FA"             # Windows: Absolute path where FA metadata is available
    elif os_type == "Linux":
        return "/opt/FA"                        # Linux: Absolute path where FA binaries are available
    elif os_type == "Darwin":
        return "/Library/FA"                    # Mac: Absolute path where FA binaries are available
    else:
        raise RuntimeError("Unsupported OS")


# ------------------------------------------------------------
# Step-3: Log Directory (OS Specific) | Optional
# ------------------------------------------------------------
def get_log_directory(os_type):
    if os_type == "Windows":
        return r"C:\temp\Content_Logs"
    elif os_type == "Linux":
        return "/var/log/Content_Logs"
    elif os_type == "Darwin":  # macOS
        return os.path.expanduser("~/Documents/Content_Logs")
    else:
        raise RuntimeError("Unsupported OS")


# -------------------------------------------------------------------------------------------------
# Step-4: Permission Check for log_file creation to record script run activity | Optional
# -------------------------------------------------------------------------------------------------
def check_permissions(log_dir):
    try:
        os.makedirs(log_dir, exist_ok=True)
        test_file = os.path.join(log_dir, "permission_test.tmp")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        return True
    except PermissionError:
        print("ERROR: Insufficient permissions to execute script or create log files.")
        print("Please run the script with appropriate permissions.")
        return False


# ------------------------------------------------------------
# Step-5: Cleanup Activity Logs Older Than 30 Days | Optional
# ------------------------------------------------------------
def cleanup_old_logs(log_dir, retention_days=30):
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    for file_name in os.listdir(log_dir):
        file_path = os.path.join(log_dir, file_name)
        if os.path.isfile(file_path):
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_time < cutoff_date:
                os.remove(file_path)


# ------------------------------------------------------------
# Metrics Collection
# ------------------------------------------------------------
def get_cpu_usage():
    cpu = psutil.cpu_times_percent(interval=0.1, percpu=False)                          # Collection - CPU Usage
    return round(100.0 - cpu.idle)


def get_memory_usage():
    mem = psutil.virtual_memory()                                                       # Collection - Memory Usage
    used_gb = mem.used / (1024 ** 3)
    total_gb = mem.total / (1024 ** 3)
    return round(used_gb, 1), round(total_gb, 1), round(mem.percent, 1)


def get_disk_usage(path):
    disk = psutil.disk_usage(path)                                                      # Collection - Disk Usage
    used_gb = disk.used / (1024 ** 3)
    total_gb = disk.total / (1024 ** 3)
    return round(used_gb, 1), round(total_gb, 1), round(disk.percent, 1)


def get_uptime_days():          
    boot_time = datetime.fromtimestamp(psutil.boot_time())                              # Collection - Uptime
    return (datetime.now() - boot_time).days


# ------------------------------------------------------------
# Main Execution
# ------------------------------------------------------------
def main():
    error_code = "None"

    now = datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
    file_timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

    os_type = get_os_type()
    os_version = get_os_version()
    hostname = get_hostname()
    python_version = get_python_version()

    log_dir = get_log_directory(os_type)

    if not check_permissions(log_dir):
        sys.exit(1)

    log_file = os.path.join(
        log_dir,
        f"{file_timestamp}_{hostname}_SystemHealth_Log.txt"                                 # Activity LogFile Name
    )

    try:
        cpu_usage = get_cpu_usage()
        mem_used, mem_total, mem_percent = get_memory_usage()
        disk_path = get_disk_path(os_type)
        disk_used, disk_total, disk_percent = get_disk_usage(disk_path)
        uptime_days = get_uptime_days()
    except Exception as error_received:
        error_code = str(error_received)
        cpu_usage = mem_used = mem_total = mem_percent = "N/A"
        disk_used = disk_total = disk_percent = "N/A"
        uptime_days = "N/A"

    # --------------------------------------------------------
    # Console Output
    # --------------------------------------------------------
    header = (
        "Timestamp | Hostname | CPU usage % | Used Memory | Total Memory | "
        "Memory usage % | Used Disk Space | Total Disk Space | Disk usage % | Uptime"
    )

    values = (
        f"{timestamp_str} | {hostname} | {cpu_usage}% | "
        f"{mem_used} GB | {mem_total} GB | {mem_percent}% | "
        f"{disk_used} GB | {disk_total} GB | {disk_percent}% | "
        f"{uptime_days} Days"
    )

    print(header)
    print(values)

    # --------------------------------------------------------
    # Write Log File
    # --------------------------------------------------------
    with open(log_file, "w") as lf:
        lf.write("=" * 90 + "\n")
        lf.write("\nFA Sensor Health Log\n")
        lf.write("=" * 90 + "\n")
        lf.write(f"Script Run Time : {timestamp_str}\n")
        lf.write(f"Hostname        : {hostname}\n")
        lf.write(f"OS Type         : {os_type}\n")
        lf.write(f"OS Version      : {os_version}\n")
        lf.write(f"Python Version  : {python_version}\n\n")
        lf.write(header + "\n")
        lf.write(values + "\n\n")
        lf.write(f"Error Code      : {error_code}\n")

    cleanup_old_logs(log_dir)


if __name__ == "__main__":
    main()

