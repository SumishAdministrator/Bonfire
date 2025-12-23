# Bonfire
External


Pre-Requisites:
===============
1. Python1 (any latest version) to be installed on the endpoint (Win, Lim, Mac)
2. Check for script file executable permission. If not, modify it as:  <chmod +x fa_metrics_systemhealth.py>
3. The script file can be run from any absolute path
4. Ensure you have a Content_Logs directory created as mentioned under "Log Directory" section. For Mac, its: "~/Documents/Content_Logs"

Scripts Run
============
1. ./fa_metrics_systemhealth.py

Output
======
1. Terminal Console
    Example: From Test Run
    Timestamp | Hostname | CPU usage % | Used Memory | Total Memory | Memory usage % | Used Disk Space | Total Disk Space | Disk usage % | Uptime
    2025-12-23 20:05:07 | Sunils-MacBook-Air.local | 30% | 3.27 GB | 8.00 GB | 78.1% | 119.93 GB | 228.27 GB | 58.8% | 11 Days
2. cat ~/Documents/Content_Logs/<SystemHealth_Log.txt>
    
    Example-1: From Test Run (OK)
FA Sensor Health Log
==========================================================================================
Script Run Time : 2025-12-23 20:03:25
Hostname        : Sunils-MacBook-Air.local
OS Type         : Darwin
OS Version      : Darwin Kernel Version 24.6.0: Mon Jul 14 11:30:51 PDT 2025; root:xnu-11417.140.69~1/RELEASE_ARM64_T8112
Python Version  : 3.11.5 (v3.11.5:cce6ba91b3, Aug 24 2023, 10:50:31) [Clang 13.0.0 (clang-1300.0.29.30)]

Timestamp | Hostname | CPU usage % | Used Memory | Total Memory | Memory usage % | Used Disk Space | Total Disk Space | Disk usage % | Uptime
2025-12-23 20:03:25 | Sunils-MacBook-Air.local | 28% | 3.27 GB | 8.00 GB | 78.2% | 119.93 GB | 228.27 GB | 58.8% | 11 Days

Error Code: None
    
    Example-2: From Test Run (NOK)
FA Sensor Health Log
==========================================================================================
Script Run Time : 2025-12-23 19:43:49
Hostname        : Sunils-MacBook-Air.local
OS Type         : Darwin
OS Version      : Darwin Kernel Version 24.6.0: Mon Jul 14 11:30:51 PDT 2025; root:xnu-11417.140.69~1/RELEASE_ARM64_T8112
Python Version  : 3.11.5 (v3.11.5:cce6ba91b3, Aug 24 2023, 10:50:31) [Clang 13.0.0 (clang-1300.0.29.30)]

Timestamp | Hostname | CPU usage % | Used Memory | Total Memory | Memory usage % | Used Disk Space | Total Disk Space | Disk usage % | Uptime
2025-12-23 19:43:49 | Sunils-MacBook-Air.local | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A

Error Code: 'datetime.datetime' object has no attribute 'days'
