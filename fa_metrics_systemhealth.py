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
import pandas as pd
from datetime import datetime, timedelta


# ------------------------------------------------------------
# Python Availability & Version | Optional
# ------------------------------------------------------------
def get_python_version():
    # Python must already be present to run this script
    return sys.version.replace("\n", " ")
   

# ------------------------------------------------------------
# OS Type, Release Version & Hostname
# ------------------------------------------------------------
def get_os_type():
    return platform.system()

def get_os_version():
    return platform.version()

def get_hostname():
    return socket.gethostname()


# ------------------------------------------------------------
# Disk Path (OS Specific)
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
# Log Directory (OS Specific) | Optional
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
# Permission Check for log_file creation to record script run activity | Optional
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
# Cleanup Activity Logs Older Than 30 Days | Optional
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
def collect_metrics(os_type):
    cpu = psutil.cpu_times_percent(interval=0.1, percpu=False)                          # Collection - CPU Usage
    cpu_usage = f"{round(100.0 - cpu.idle)}%"

    mem = psutil.virtual_memory()                                                       # Collection - Memory Usage
    used_mem =f"{mem.used / (1024 ** 3):.2f} GB"
    total_mem = f"{mem.total / (1024 ** 3):.2f} GB"
    mem_percent = f"{mem.percent}%"

    disk = psutil.disk_usage(get_disk_path(os_type))                                    # Collection - Disk Usage
    used_disk = f"{disk.used / (1024 ** 3):.2f} GB"
    total_disk = f"{disk.total / (1024 ** 3):.2f} GB"
    disk_percent = f"{disk.percent}%"

    boot_time = datetime.fromtimestamp(psutil.boot_time())                              # Collection - Uptime
    uptime_days = (datetime.now() - boot_time).days    
    uptime = f"{uptime_days} Days"

    return cpu_usage, used_mem, total_mem, mem_percent, used_disk, total_disk, disk_percent, uptime

# ------------------------------------------------------------
# Main Execution
# ------------------------------------------------------------
def main():
    error_code = "None"

    now_timestamp = datetime.now()
    timestamp_str = now_timestamp.strftime("%Y-%m-%d %H:%M:%S")
    file_timestamp = now_timestamp.strftime("%Y-%m-%d_%H-%M-%S")

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
        (
            cpu_usage,
            used_mem,
            total_mem,
            mem_percent,
            used_disk,
            total_disk,
            disk_percent,
            uptime,
        ) = collect_metrics(os_type)
    except Exception as error_found:
        error_code = str(error_found)
        cpu_usage = used_mem = total_mem = mem_percent = "N/A"
        used_disk = total_disk = disk_percent = uptime = "N/A"

    # --------------------------------------------------------
    # DataFrame Creation
    # --------------------------------------------------------
    metrics_data = {
        "Timestamp": timestamp_str,
        "Hostname": hostname,
        "CPU usage %": cpu_usage,
        "Used Memory": used_mem,
        "Total Memory": total_mem,
        "Memory usage %": mem_percent,
        "Used Disk Space": used_disk,
        "Total Disk Space": total_disk,
        "Disk usage %": disk_percent,
        "Uptime": uptime
    }

    metrics_df = pd.DataFrame([metrics_data])   
    
    # --------------------------------------------------------
    # Console Output
    # --------------------------------------------------------
    header_line = " | ".join(metrics_df.columns)
    value_line = " | ".join(metrics_df.iloc[0].astype(str).values)

    print(header_line)
    print(value_line)
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
        lf.write(header_line + "\n")
        lf.write(value_line + "\n\n")
        lf.write(f"Error Code: " + error_code + "\n")

    cleanup_old_logs(log_dir)

if __name__ == "__main__":
        main()
