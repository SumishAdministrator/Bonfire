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
import time
from datetime import datetime, timedelta


# ------------------------------------------------------------
# Python Availability & Version | label as tag_<> | Optional
# ------------------------------------------------------------
def get_python_version():
    # Python must already be present to run this script
    return sys.version.replace("\n", " ")
   

# ------------------------------------------------------------
# OS Type, Release Version & Hostname | label as tag_<>
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
        return r"C:\\ProgramData\\FA"           # Windows: Absolute path where FA metadata is available. 
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
        return r"C:\\temp\\Content_Logs"          # Note, if we can have a root partition as validation point
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
# Metrics Collection | m_<metric-name>
# ------------------------------------------------------------
def collect_metrics(os_type):
    cpu = psutil.cpu_times_percent(interval=0.1, percpu=False)                          # Collection - CPU Usage
    m_cpu_usage = f"{round(100.0 - cpu.idle)}%"

    mem = psutil.virtual_memory()                                                       # Collection - Memory Usage
    m_used_memory =f"{mem.used / (1024 ** 3):.2f} GB"
    m_total_memory = f"{mem.total / (1024 ** 3):.2f} GB"
    m_memory_percent = f"{mem.percent}%"

    disk = psutil.disk_usage(get_disk_path(os_type))                                    # Collection - Disk Usage
    m_used_disk = f"{disk.used / (1024 ** 3):.2f} GB"
    m_total_disk = f"{disk.total / (1024 ** 3):.2f} GB"
    m_disk_percent = f"{disk.percent}%"

    boot_time = datetime.fromtimestamp(psutil.boot_time())                              # Collection - Uptime
    uptime_days = (datetime.now() - boot_time).days    
    m_uptime = f"{uptime_days} Days"

    return m_cpu_usage, m_used_memory, m_total_memory, m_memory_percent, m_used_disk, m_total_disk, m_disk_percent, m_uptime


# -------------------------------------------------------------------------------------------------
# User Input - Metric Collection Interval (mc_interval_min) and Script Total Runtime (st_runtime_hr)
# -------------------------------------------------------------------------------------------------
def get_user_inputs_mci_sr():
    try:
        mc_interval_min = int(input("Enter input on the metric collection interval (in min): ").strip())
        if mc_interval_min <= 0:
            raise ValueError
    except ValueError:
        print("ERROR: Value must be a positive integer. ")
        sys.exit(1)

    try:
        st_runtime_hr = float(input("Enter input on the script total runtime (in hour)? ").strip())
        if st_runtime_hr <= 0:
            raise ValueError
    except ValueError:
        print("ERROR: Runtime should be a positive integer. ")
        sys.exit(1)
    
    return mc_interval_min, st_runtime_hr


# ------------------------------------------------------------
# Main Execution
# ------------------------------------------------------------
def main():
    mc_interval_min, st_runtime_hr = get_user_inputs_mci_sr()

    tag_os_type = get_os_type()
    tag_os_version = get_os_version()
    tag_hostname = get_hostname()
    tag_python_version = get_python_version()

    log_dir = get_log_directory(tag_os_type)

    if not check_permissions(log_dir):
        sys.exit(1)

    metrics_history_csv = os.path.join(log_dir, f"Metric_History_csv_{tag_hostname}.csv")                                              
    

# Capturing existing CSV row count (excluding header)
    if os.path.exists(metrics_history_csv):
        csv_start_row_count = len(pd.read_csv(metrics_history_csv))
    else:
        csv_start_row_count = 0

# Script duration and Interval calculation
    start_time_script = time.time()
    end_time_script = start_time_script + (st_runtime_hr * 3600 )

    while time.time() < end_time_script:
        error_code = "None"
        now_timestamp = datetime.now()
        display_timestamp = now_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        file_timestamp = now_timestamp.strftime("%Y-%m-%d_%H-%M-%S")
        
        log_file = os.path.join(
            log_dir,
            f"{file_timestamp}_{tag_hostname}_SystemHealth_Log.txt"                                 # Activity LogFile Name
        )
        try:
            (
                m_cpu_usage,
                m_used_memory,
                m_total_memory,
                m_memory_percent,
                m_used_disk,
                m_total_disk,
                m_disk_percent,
                m_uptime,
            ) = collect_metrics(tag_os_type)
        except Exception as error_found:
            error_code = str(error_found)
            m_cpu_usage = m_used_memory = m_total_memory = m_memory_percent = "N/A"
            m_used_disk = m_total_disk = m_disk_percent = m_uptime = "N/A"

    # --------------------------------------------------------
    # DataFrame Creation
    # --------------------------------------------------------
        metrics_data = {
            "Timestamp": display_timestamp,
            "Hostname": tag_hostname,
            "CPU usage %": m_cpu_usage,
            "Used Memory": m_used_memory,
            "Total Memory": m_total_memory,
            "Memory usage %": m_memory_percent,
            "Used Disk Space": m_used_disk,
            "Total Disk Space": m_total_disk,
            "Disk usage %": m_disk_percent,
            "uptime": m_uptime
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
            lf.write(f"Script Run Time : {display_timestamp}\n")
            lf.write(f"Hostname        : {tag_hostname}\n")
            lf.write(f"OS Type         : {tag_os_type}\n")
            lf.write(f"OS Version      : {tag_os_version}\n")
            lf.write(f"Python Version  : {tag_python_version}\n\n")
            lf.write(header_line + "\n")
            lf.write(value_line + "\n\n")
            lf.write(f"Error Code: " + error_code + "\n")

    # --------------------------------------------------------
    # Write CSV File (with Header if ONLY file do not exists)
    # --------------------------------------------------------
        write_header = not os.path.exists(metrics_history_csv)
        metrics_df.to_csv(metrics_history_csv, mode="a", header=write_header, index=False)
    
        cleanup_old_logs(log_dir)
    
        if time.time() + (mc_interval_min * 60) >= end_time_script:
            print("\nExiting Metric collection")
            break
        else:
            print("\nScript Run is in Progress ..." )
    
        time.sleep(mc_interval_min * 60)
    # --------------------------------------------------------
    # FINAL OUTPUT
    # --------------------------------------------------------
    print(f"\nThe Script has completed collecting metrics\n")
    
    
    final_updated_df = pd.read_csv(metrics_history_csv)
    delta_row_added_df = final_updated_df.iloc[csv_start_row_count:]
    
    print(f" *** Metrics collected *** ")
    print(delta_row_added_df.to_string(index=False))
    #print(pd.read_csv(metrics_history_csv).to_string(index=False))

if __name__ == "__main__":
        main()
