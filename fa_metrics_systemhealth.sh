!/usr/bin/env bash
#
# File Name  : fa_metrics_systemhealth.sh
# Purpose    : Collect system health metrics (CPU, Memory, Disk, Uptime)
# Platforms  : Linux, macOS, Windows (Git Bash / WSL)
#

# ------------------------------------------------------------
# Step-1: Detect OS Type
# ------------------------------------------------------------
OS_TYPE="$(uname)"
HOSTNAME="$(hostname)"
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"
FILE_TIMESTAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
ERROR_CODE="None"

# ------------------------------------------------------------
# Step-2: Set Log Directory (OS Specific)
# ------------------------------------------------------------
if [[ "$OS_TYPE" == "Linux" ]]; then
    LOG_DIR="/var/log/Content_Logs"
    DISK_PATH="/opt/FA"
elif [[ "$OS_TYPE" == "Darwin" ]]; then
    LOG_DIR="$HOME/Documents/Content_Logs"
    DISK_PATH="/Library/FA"
else
    # Windows (Git Bash / WSL)
    LOG_DIR="/c/temp/Content_Logs"
    DISK_PATH="/c/ProgramData/FA"
fi

# ------------------------------------------------------------
# Step-3: Permission Check
# ------------------------------------------------------------
mkdir -p "$LOG_DIR" 2>/dev/null
if [[ $? -ne 0 ]]; then
    echo "ERROR: Insufficient permissions to create $LOG_DIR"
    exit 1
fi

LOG_FILE="$LOG_DIR/${FILE_TIMESTAMP}_${HOSTNAME}_SensorHealth_Log.txt"

# ------------------------------------------------------------
# Step-4: CPU Usage
# ------------------------------------------------------------
if [[ "$OS_TYPE" == "Linux" ]]; then
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print 100 - $8}')
elif [[ "$OS_TYPE" == "Darwin" ]]; then
    CPU_IDLE=$(top -l 1 | grep "CPU usage" | awk '{print $7}' | sed 's/%//')
    CPU_USAGE=$(echo "100 - $CPU_IDLE" | bc)
else
    CPU_USAGE=$(wmic cpu get loadpercentage | awk 'NR==2 {print $1}')
fi
CPU_USAGE=$(printf "%.0f" "$CPU_USAGE")

# ------------------------------------------------------------
# Step-5: Memory Usage
# ------------------------------------------------------------
if [[ "$OS_TYPE" == "Linux" ]]; then
    read MEM_TOTAL MEM_USED <<<$(free -g | awk '/Mem:/ {print $2, $3}')
elif [[ "$OS_TYPE" == "Darwin" ]]; then
    PAGE_SIZE=$(vm_stat | awk '/page size/ {print $8}')
    PAGES_FREE=$(vm_stat | awk '/Pages free/ {print $3}' | tr -d '.')
    PAGES_ACTIVE=$(vm_stat | awk '/Pages active/ {print $3}' | tr -d '.')
    MEM_USED=$(echo "($PAGES_ACTIVE*$PAGE_SIZE)/1024/1024/1024" | bc)
    MEM_TOTAL=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)}')
else
    MEM_TOTAL=$(wmic computersystem get TotalPhysicalMemory | awk 'NR==2 {print int($1/1024/1024/1024)}')
    MEM_USED=$(wmic OS get FreePhysicalMemory | awk 'NR==2 {print int(($1*-1)/1024/1024)}')
fi

MEM_PERCENT=$(echo "scale=1; ($MEM_USED/$MEM_TOTAL)*100" | bc)

# ------------------------------------------------------------
# Step-6: Disk Usage
# ------------------------------------------------------------
read DISK_TOTAL DISK_USED <<<$(df -BG "$DISK_PATH" 2>/dev/null | awk 'NR==2 {gsub("G",""); print $2, $3}')
DISK_PERCENT=$(echo "scale=1; ($DISK_USED/$DISK_TOTAL)*100" | bc)

# ------------------------------------------------------------
# Step-7: Uptime
# ------------------------------------------------------------
UPTIME_DAYS=$(uptime | awk -F'(up |,)' '{print $2}' | awk '{print $1}')
[[ -z "$UPTIME_DAYS" ]] && UPTIME_DAYS=0

# ------------------------------------------------------------
# Output (Console)
# ------------------------------------------------------------
HEADER="Timestamp | Hostname | CPU usage % | Used Memory | Total Memory | Memory usage % | Used Disk Space | Total Disk Space | Disk usage % | Uptime"
VALUES="$TIMESTAMP | $HOSTNAME | ${CPU_USAGE}% | ${MEM_USED} GB | ${MEM_TOTAL} GB | ${MEM_PERCENT}% | ${DISK_USED} GB | ${DISK_TOTAL} GB | ${DISK_PERCENT}% | ${UPTIME_DAYS} Days"

echo "$HEADER"
echo "$VALUES"

# ------------------------------------------------------------
# Write Log File
# ------------------------------------------------------------
{
    echo "FA Sensor Health Log"
    echo "=============================================================="
    echo "Script Run Time : $TIMESTAMP"
    echo "Hostname        : $HOSTNAME"
    echo "OS Type         : $OS_TYPE"
    echo "Shell Version   : $BASH_VERSION"
    echo
    echo "$HEADER"
    echo "$VALUES"
    echo
    echo "Error Code      : $ERROR_CODE"
} > "$LOG_FILE"

# ------------------------------------------------------------
# Step-8: Delete Logs Older Than 30 Days
# ------------------------------------------------------------
find "$LOG_DIR" -type f -mtime +30 -name "*_SensorHealth_Log.txt" -delete