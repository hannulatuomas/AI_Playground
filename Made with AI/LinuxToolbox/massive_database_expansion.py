#!/usr/bin/env python3

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

# Massive Linux Commands Database - Goal: 500+ commands
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'linux_admin_tool')

async def create_comprehensive_database():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Comprehensive Linux Commands Database
    massive_commands = [
        # ==================== SYSTEM ADMINISTRATION ====================
        {
            "id": str(uuid.uuid4()),
            "name": "ps",
            "description": "Display information about running processes with detailed process information including PID, CPU usage, memory usage, and command details",
            "syntax": "ps [options]",
            "examples": [
                "ps aux | head -20  # Show all processes with user info",
                "ps -ef | grep nginx  # Find nginx processes",
                "ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%cpu | head  # Sort by CPU usage",
                "ps -u username  # Show processes for specific user",
                "ps -p 1234  # Show specific process by PID",
                "ps --forest  # Show process tree",
                "ps -L  # Show threads",
                "ps -o pid,comm,etime  # Custom output format"
            ],
            "category": "Process Control",
            "tags": ["processes", "monitoring", "system", "ubuntu", "debian", "rhel", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "top",
            "description": "Real-time process monitor showing CPU and memory usage, load average, and system statistics with interactive controls for process management",
            "syntax": "top [options]",
            "examples": [
                "top  # Interactive process viewer",
                "top -u username  # Show processes for specific user",
                "top -p 1234,5678  # Monitor specific PIDs",
                "top -n 1  # Run once and exit",
                "top -d 5  # Update every 5 seconds",
                "top -c  # Show full command lines",
                "top -H  # Show threads",
                "top -b -n1 | head -20  # Batch mode for scripting"
            ],
            "category": "System Monitoring",
            "tags": ["monitoring", "processes", "cpu", "memory", "interactive", "ubuntu", "debian", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "kill",
            "description": "Terminate processes by sending signals, with various signal types for graceful shutdown or forced termination",
            "syntax": "kill [options] PID...",
            "examples": [
                "kill 1234  # Send SIGTERM (graceful shutdown)",
                "kill -9 1234  # Send SIGKILL (force kill)",
                "kill -HUP 1234  # Send SIGHUP (reload config)",
                "kill -USR1 1234  # Send SIGUSR1 (user-defined signal)",
                "kill -STOP 1234  # Pause process",
                "kill -CONT 1234  # Resume paused process",
                "killall nginx  # Kill all nginx processes",
                "pkill -f 'python.*script.py'  # Kill by pattern"
            ],
            "category": "Process Control",
            "tags": ["processes", "signals", "terminate", "system", "ubuntu", "debian", "rhel", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "cron",
            "description": "Time-based job scheduler for automating tasks, system maintenance, backups, and periodic script execution with flexible scheduling syntax",
            "syntax": "crontab [options]",
            "examples": [
                "crontab -e  # Edit user's crontab",
                "crontab -l  # List current crontab entries",
                "crontab -r  # Remove all crontab entries",
                "0 2 * * * /path/to/backup.sh  # Daily at 2 AM",
                "*/5 * * * * /usr/bin/monitor.py  # Every 5 minutes",
                "0 0 1 * * /usr/local/bin/monthly.sh  # Monthly on 1st",
                "30 9-17 * * 1-5 /usr/bin/workday.sh  # Weekdays 9:30-17:30",
                "@reboot /path/to/startup.sh  # Run at system boot"
            ],
            "category": "System Monitoring",
            "tags": ["scheduling", "automation", "jobs", "cron", "ubuntu", "debian", "rhel", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "uptime",
            "description": "Display system uptime, load averages, and current time showing how long the system has been running and current system load",
            "syntax": "uptime [options]",
            "examples": [
                "uptime  # Show uptime and load average",
                "uptime -p  # Show uptime in pretty format",
                "uptime -s  # Show system start time",
                "w  # Show who is logged on and what they are doing",
                "cat /proc/uptime  # Raw uptime data",
                "cat /proc/loadavg  # Raw load average data"
            ],
            "category": "System Monitoring",
            "tags": ["uptime", "load average", "system info", "monitoring", "ubuntu", "debian", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # ==================== NETWORKING TOOLS ====================
        {
            "id": str(uuid.uuid4()),
            "name": "ping",
            "description": "Test network connectivity and measure round-trip time to hosts with detailed packet loss statistics and timing information",
            "syntax": "ping [options] destination",
            "examples": [
                "ping google.com  # Basic connectivity test",
                "ping -c 4 8.8.8.8  # Send only 4 packets",
                "ping -i 2 192.168.1.1  # 2 second intervals",
                "ping -s 1000 host.com  # Large packet size",
                "ping -f localhost  # Flood ping (root only)",
                "ping6 ipv6.google.com  # IPv6 ping",
                "ping -W 5000 slow-host.com  # 5 second timeout",
                "ping -q -c 10 host.com  # Quiet mode with summary"
            ],
            "category": "Networking",
            "tags": ["networking", "connectivity", "icmp", "diagnostics", "ubuntu", "debian", "rhel", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "wget",
            "description": "Download files from web servers with support for HTTP, HTTPS, FTP protocols, resume capability, and recursive downloading",
            "syntax": "wget [options] URL...",
            "examples": [
                "wget https://example.com/file.zip  # Download file",
                "wget -c https://large-file.com/download  # Resume download",
                "wget -r -np -k https://example.com/  # Mirror website",
                "wget --spider https://example.com  # Check if URL exists",
                "wget -q -O - https://api.example.com/data  # Download to stdout",
                "wget --limit-rate=200k https://file.com/big.iso  # Rate limiting",
                "wget -t 3 --retry-connrefused https://unreliable.com/file  # Retry options",
                "wget --header='Authorization: Bearer token' https://api.com/data"
            ],
            "category": "Networking",
            "tags": ["download", "http", "ftp", "web", "files", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "iptables",
            "description": "Configure Linux kernel firewall with packet filtering, NAT, and port forwarding for network security and traffic control",
            "syntax": "iptables [options] [chain] [matches] [target]",
            "examples": [
                "iptables -L  # List all rules",
                "iptables -A INPUT -p tcp --dport 22 -j ACCEPT  # Allow SSH",
                "iptables -A INPUT -s 192.168.1.0/24 -j ACCEPT  # Allow subnet",
                "iptables -D INPUT 3  # Delete rule number 3",
                "iptables -P INPUT DROP  # Default policy DROP",
                "iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE  # NAT",
                "iptables -A FORWARD -p tcp --dport 80 -j ACCEPT  # Forward HTTP",
                "iptables-save > /etc/iptables/rules.v4  # Save rules"
            ],
            "category": "Security",
            "tags": ["firewall", "security", "networking", "iptables", "ubuntu", "debian", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # ==================== FILE OPERATIONS ====================
        {
            "id": str(uuid.uuid4()),
            "name": "find",
            "description": "Search for files and directories with powerful filtering options including name patterns, size, date, permissions, and execute actions on results",
            "syntax": "find [path] [expression]",
            "examples": [
                "find /home -name '*.txt'  # Find all .txt files",
                "find . -type f -size +100M  # Files larger than 100MB",
                "find /var/log -mtime +7 -delete  # Delete files older than 7 days",
                "find . -perm 777  # Find files with 777 permissions",
                "find /usr -name 'python*' -executable  # Find python executables",
                "find . -user root -type f  # Files owned by root",
                "find /tmp -empty -type d -delete  # Remove empty directories",
                "find . -name '*.log' -exec gzip {} \\;  # Compress log files"
            ],
            "category": "File Management",
            "tags": ["search", "files", "directories", "permissions", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "chmod",
            "description": "Change file and directory permissions using numeric or symbolic notation for user, group, and other access control",
            "syntax": "chmod [options] mode file...",
            "examples": [
                "chmod 755 script.sh  # rwxr-xr-x permissions",
                "chmod u+x file.txt  # Add execute for owner",
                "chmod g-w,o-r file.txt  # Remove group write, other read",
                "chmod -R 644 /var/www/html/  # Recursive permission change",
                "chmod a+r file.txt  # Add read for all",
                "chmod u=rwx,g=rx,o=r file  # Explicit permissions",
                "chmod --reference=file1 file2  # Copy permissions from file1",
                "chmod 4755 /usr/bin/sudo  # Set SUID bit"
            ],
            "category": "File Management",
            "tags": ["permissions", "security", "files", "access control", "ubuntu", "debian", "rhel", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "chown",
            "description": "Change file and directory ownership, including user and group ownership for access control and security management",
            "syntax": "chown [options] owner[:group] file...",
            "examples": [
                "chown user:group file.txt  # Change owner and group",
                "chown -R www-data:www-data /var/www/  # Recursive ownership",
                "chown :group file.txt  # Change only group",
                "chown user file.txt  # Change only owner",
                "chown --reference=file1 file2  # Copy ownership from file1",
                "chown -h user symlink  # Don't follow symbolic links",
                "chown 1000:1000 file.txt  # Use numeric UID/GID"
            ],
            "category": "File Management",
            "tags": ["ownership", "security", "files", "users", "groups", "ubuntu", "debian", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "rsync",
            "description": "Efficiently synchronize files and directories locally or over network with compression, incremental transfer, and preservation of attributes",
            "syntax": "rsync [options] source destination",
            "examples": [
                "rsync -av /source/ /destination/  # Archive mode with verbose",
                "rsync -avz user@server:/remote/ /local/  # Sync from remote with compression",
                "rsync --delete -av /source/ /backup/  # Delete files not in source",
                "rsync -av --exclude='*.tmp' /src/ /dst/  # Exclude patterns",
                "rsync -av --progress large-file.iso /backup/  # Show progress",
                "rsync -av --dry-run /src/ /dst/  # Test run without changes",
                "rsync -av --partial --append /src/ /dst/  # Resume interrupted transfers",
                "rsync -av --bwlimit=1000 /src/ user@host:/dst/  # Bandwidth limiting"
            ],
            "category": "File Management",
            "tags": ["sync", "backup", "transfer", "remote", "incremental", "ubuntu", "debian", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # ==================== TEXT PROCESSING ====================
        {
            "id": str(uuid.uuid4()),
            "name": "grep",
            "description": "Search text patterns in files using regular expressions with context options, line numbers, and recursive directory searching",
            "syntax": "grep [options] pattern [files...]",
            "examples": [
                "grep 'error' /var/log/messages  # Search for 'error' in log",
                "grep -r 'TODO' /home/user/code/  # Recursive search",
                "grep -n 'pattern' file.txt  # Show line numbers",
                "grep -i 'Error' *.log  # Case insensitive search",
                "grep -v 'debug' log.txt  # Invert match (exclude)",
                "grep -A 3 -B 2 'error' log.txt  # Show 3 lines after, 2 before",
                "grep -c 'pattern' file.txt  # Count matches",
                "grep -E '(error|warning|critical)' log.txt  # Extended regex"
            ],
            "category": "Text Processing",
            "tags": ["search", "text", "regex", "patterns", "logs", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "sed",
            "description": "Stream editor for filtering and transforming text with pattern replacement, line deletion, and text manipulation capabilities",
            "syntax": "sed [options] 'command' [files...]",
            "examples": [
                "sed 's/old/new/g' file.txt  # Replace all occurrences",
                "sed -i 's/foo/bar/g' file.txt  # In-place editing",
                "sed '1,5d' file.txt  # Delete lines 1-5",
                "sed '/pattern/d' file.txt  # Delete lines matching pattern",
                "sed -n '10,20p' file.txt  # Print lines 10-20",
                "sed 's/^/> /' file.txt  # Add prefix to each line",
                "sed '/^$/d' file.txt  # Remove empty lines",
                "sed 's/\\([0-9]\\+\\)/[\\1]/g' file.txt  # Capture groups"
            ],
            "category": "Text Processing",
            "tags": ["text editing", "regex", "replacement", "stream", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "awk",
            "description": "Powerful pattern scanning and processing language for text processing, data extraction, and report generation",
            "syntax": "awk [options] 'program' [files...]",
            "examples": [
                "awk '{print $1}' file.txt  # Print first column",
                "awk '/pattern/ {print $2}' file.txt  # Print second column of matching lines",
                "awk -F: '{print $1,$3}' /etc/passwd  # Use colon as field separator",
                "awk 'length($0) > 80' file.txt  # Print lines longer than 80 chars",
                "awk '{sum+=$1} END {print sum}' numbers.txt  # Sum first column",
                "awk 'NR==5' file.txt  # Print line number 5",
                "awk '{print NF, $0}' file.txt  # Print number of fields and line",
                "ps aux | awk '$3 > 10.0 {print $2, $11}'  # High CPU processes"
            ],
            "category": "Text Processing",
            "tags": ["text processing", "scripting", "data extraction", "patterns", "ubuntu", "debian", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # ==================== SYSTEM INFORMATION ====================
        {
            "id": str(uuid.uuid4()),
            "name": "df",
            "description": "Display filesystem disk space usage with available space, used space, and mount points for storage monitoring",
            "syntax": "df [options] [filesystem...]",
            "examples": [
                "df -h  # Human readable format",
                "df -T  # Show filesystem type",
                "df -i  # Show inode usage",
                "df /home  # Show usage for specific mount",
                "df -x tmpfs  # Exclude filesystem type",
                "df --total  # Show grand total",
                "df -h | grep -v tmpfs  # Exclude temporary filesystems"
            ],
            "category": "Hardware Information",
            "tags": ["disk usage", "filesystem", "storage", "monitoring", "ubuntu", "debian", "rhel", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "du",
            "description": "Display directory space usage with recursive size calculation, sorting options, and threshold filtering for storage analysis",
            "syntax": "du [options] [directories...]",
            "examples": [
                "du -h  # Human readable sizes",
                "du -sh /home/*  # Summary of home directories",
                "du -ah /var/log | sort -hr | head -10  # Top 10 largest files",
                "du --max-depth=2 /usr  # Limit depth",
                "du -x /  # Don't cross filesystem boundaries",
                "du --threshold=1G /home  # Show only directories > 1GB",
                "du -c /home/user/*  # Show totals",
                "du --apparent-size -sh folder/  # Show apparent size"
            ],
            "category": "Hardware Information",
            "tags": ["disk usage", "directories", "size", "storage", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "free",
            "description": "Display system memory usage including RAM, swap, buffers, and cache with real-time monitoring capabilities",
            "syntax": "free [options]",
            "examples": [
                "free -h  # Human readable format",
                "free -m  # Show in megabytes",
                "free -s 2  # Update every 2 seconds",
                "free -t  # Show totals",
                "free -w  # Wide mode (separate buffers/cache)",
                "cat /proc/meminfo  # Detailed memory information",
                "vmstat 1 5  # Memory statistics every second for 5 times"
            ],
            "category": "System Monitoring",
            "tags": ["memory", "ram", "swap", "system info", "monitoring", "ubuntu", "debian", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # ==================== ARCHIVE & COMPRESSION ====================
        {
            "id": str(uuid.uuid4()),
            "name": "tar",
            "description": "Archive files and directories with compression support, extraction capabilities, and preservation of file attributes and permissions",
            "syntax": "tar [options] archive [files...]",
            "examples": [
                "tar -czf backup.tar.gz /home/user/  # Create compressed archive",
                "tar -xzf archive.tar.gz  # Extract compressed archive",
                "tar -tzf archive.tar.gz  # List archive contents",
                "tar --exclude='*.tmp' -czf backup.tar.gz /data/  # Exclude patterns",
                "tar -xzf archive.tar.gz -C /destination/  # Extract to specific directory",
                "tar -czf - /source/ | ssh user@host 'cat > remote.tar.gz'  # Remote backup",
                "tar -cjf archive.tar.bz2 /data/  # Use bzip2 compression",
                "tar --incremental -czf backup.tar.gz /home/  # Incremental backup"
            ],
            "category": "Archive & Compression",
            "tags": ["archive", "compression", "backup", "tar", "gzip", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "gzip",
            "description": "Compress and decompress files using gzip compression algorithm with space-saving capabilities and fast processing",
            "syntax": "gzip [options] [files...]",
            "examples": [
                "gzip file.txt  # Compress file (creates file.txt.gz)",
                "gzip -d file.txt.gz  # Decompress file",
                "gzip -r /directory/  # Recursively compress directory",
                "gzip -k file.txt  # Keep original file",
                "gzip -9 file.txt  # Maximum compression",
                "gzip -1 file.txt  # Fast compression",
                "gzip -c file.txt > file.gz  # Compress to stdout",
                "zcat file.gz | grep pattern  # Search compressed file"
            ],
            "category": "Archive & Compression",
            "tags": ["compression", "gzip", "space saving", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # ==================== SECURITY TOOLS ====================
        {
            "id": str(uuid.uuid4()),
            "name": "ssh",
            "description": "Secure Shell for encrypted remote access, file transfers, and tunnel creation with key-based authentication and port forwarding",
            "syntax": "ssh [options] [user@]hostname [command]",
            "examples": [
                "ssh user@server.com  # Connect to remote server",
                "ssh -p 2222 user@server.com  # Connect on custom port",
                "ssh -i ~/.ssh/id_rsa user@server  # Use specific private key",
                "ssh -L 8080:localhost:80 user@server  # Local port forwarding",
                "ssh -R 9090:localhost:3000 user@server  # Remote port forwarding",
                "ssh -X user@server  # Enable X11 forwarding",
                "ssh -N -f -L 8080:db.internal:5432 bastion  # Background tunnel",
                "ssh user@server 'ls -la'  # Execute remote command"
            ],
            "category": "Security",
            "tags": ["ssh", "remote access", "encryption", "tunneling", "ubuntu", "debian", "rhel", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "sudo",
            "description": "Execute commands as another user with privilege escalation, logging, and fine-grained access control for system administration",
            "syntax": "sudo [options] command",
            "examples": [
                "sudo apt update  # Run command as root",
                "sudo -u postgres psql  # Run as specific user",
                "sudo -i  # Interactive root shell",
                "sudo visudo  # Edit sudoers file safely",
                "sudo !!  # Repeat last command with sudo",
                "sudo -l  # List allowed commands",
                "sudo -k  # Invalidate cached credentials",
                "sudo -s  # Run shell as root"
            ],
            "category": "Security",
            "tags": ["privilege escalation", "root", "security", "administration", "ubuntu", "debian", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # ==================== DATABASE TOOLS ====================
        {
            "id": str(uuid.uuid4()),
            "name": "sqlite3",
            "description": "Command-line interface for SQLite database with SQL queries, database administration, and data import/export capabilities",
            "syntax": "sqlite3 [options] database [SQL]",
            "examples": [
                "sqlite3 database.db  # Open database interactively",
                "sqlite3 db.sqlite '.tables'  # List all tables",
                "sqlite3 db.sqlite '.schema users'  # Show table schema",
                "sqlite3 -header -csv db.sqlite 'SELECT * FROM users;'  # CSV output",
                "sqlite3 db.sqlite '.dump' > backup.sql  # Export database",
                "sqlite3 new.db < backup.sql  # Import database",
                "sqlite3 db.sqlite '.backup backup.db'  # Binary backup",
                "sqlite3 -separator ',' db.sqlite '.import data.csv table'"
            ],
            "category": "Database Management",
            "tags": ["database", "sqlite", "sql", "data", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # ==================== MONITORING TOOLS ====================
        {
            "id": str(uuid.uuid4()),
            "name": "iostat",
            "description": "Monitor system input/output device loading and CPU utilization with detailed disk performance statistics and I/O patterns",
            "syntax": "iostat [options] [interval] [count]",
            "examples": [
                "iostat  # One-time I/O statistics",
                "iostat 2  # Update every 2 seconds",
                "iostat -x 1 10  # Extended stats, 1 sec interval, 10 times",
                "iostat -d  # Disk statistics only",
                "iostat -c  # CPU statistics only",
                "iostat -p sda  # Specific disk partition",
                "iostat -m  # Display in MB/s",
                "iostat -h  # Human readable format"
            ],
            "category": "System Monitoring",
            "tags": ["io", "disk", "performance", "monitoring", "statistics", "ubuntu", "debian", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "vmstat",
            "description": "Report virtual memory statistics including processes, memory, paging, block IO, traps, and CPU activity for performance analysis",
            "syntax": "vmstat [options] [delay] [count]",
            "examples": [
                "vmstat  # One-time memory statistics",
                "vmstat 2 5  # Update every 2 seconds, 5 times",
                "vmstat -a  # Active/inactive memory",
                "vmstat -d  # Disk statistics",
                "vmstat -s  # Summary of memory statistics",
                "vmstat -f  # Fork statistics",
                "vmstat -m  # Slab cache information",
                "vmstat -S M  # Display in megabytes"
            ],
            "category": "System Monitoring",
            "tags": ["memory", "virtual memory", "statistics", "performance", "ubuntu", "debian", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # ==================== DEVELOPMENT TOOLS ====================
        {
            "id": str(uuid.uuid4()),
            "name": "make",
            "description": "Build automation tool for compiling programs, managing dependencies, and executing build tasks with Makefile rules",
            "syntax": "make [options] [target...]",
            "examples": [
                "make  # Build default target",
                "make install  # Build and install",
                "make clean  # Clean build artifacts",
                "make -j4  # Parallel build with 4 jobs",
                "make -f custom.mk  # Use custom Makefile",
                "make -n  # Dry run (show commands without executing)",
                "make CFLAGS='-O2 -g'  # Override variables",
                "make -C /path/to/project  # Change to directory first"
            ],
            "category": "Development Tools",
            "tags": ["build", "compilation", "make", "development", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "gcc",
            "description": "GNU Compiler Collection for compiling C, C++, and other languages with optimization options and debugging support",
            "syntax": "gcc [options] files...",
            "examples": [
                "gcc -o program program.c  # Compile C program",
                "gcc -Wall -Wextra -g program.c  # Enable warnings and debug info",
                "gcc -O2 -o optimized program.c  # Optimize compilation",
                "gcc -shared -fPIC -o library.so library.c  # Create shared library",
                "gcc -static -o static_program program.c  # Static linking",
                "gcc -std=c99 program.c  # Specify C standard",
                "gcc -I/usr/include/custom program.c  # Include directory",
                "gcc -L/usr/lib/custom -lcustomlib program.c  # Link library"
            ],
            "category": "Development Tools",
            "tags": ["compiler", "gcc", "c", "cpp", "development", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # ==================== WEB SERVERS & SERVICES ====================
        {
            "id": str(uuid.uuid4()),
            "name": "apache2ctl",
            "description": "Apache HTTP Server control interface for starting, stopping, reloading configuration, and managing Apache web server operations",
            "syntax": "apache2ctl [command]",
            "examples": [
                "apache2ctl start  # Start Apache server",
                "apache2ctl stop  # Stop Apache server",
                "apache2ctl restart  # Restart Apache server",
                "apache2ctl reload  # Reload configuration",
                "apache2ctl configtest  # Test configuration syntax",
                "apache2ctl status  # Show server status",
                "apache2ctl fullstatus  # Detailed server status",
                "apache2ctl graceful  # Graceful restart"
            ],
            "category": "Web Server",
            "tags": ["apache", "web server", "http", "control", "ubuntu", "debian"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ]
    
    # Continue adding more commands in next part...
    return massive_commands

async def add_massive_commands():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        commands = await create_comprehensive_database()
        added_count = 0
        
        print("🚀 Starting massive database expansion...")
        
        for i, command in enumerate(commands, 1):
            existing = await db.commands.find_one({"name": command["name"]})
            if not existing:
                await db.commands.insert_one(command)
                print(f"✅ [{i:3d}] Added: {command['name']}")
                added_count += 1
            else:
                print(f"⏭️  [{i:3d}] Skipped: {command['name']}")
        
        # Get final statistics
        total_commands = await db.commands.count_documents({})
        categories = await db.commands.distinct("category")
        tags = await db.commands.distinct("tags")
        
        print(f"\n🎉 Massive expansion complete!")
        print(f"📊 Commands processed: {len(commands)}")
        print(f"📊 New commands added: {added_count}")
        print(f"📈 Total commands in database: {total_commands}")
        print(f"📂 Categories: {len(categories)}")
        print(f"🏷️  Unique tags: {len(tags)}")
        
        # Check if we need more to reach 500
        if total_commands < 500:
            remaining = 500 - total_commands
            print(f"\n📌 Need {remaining} more commands to reach 500 target")
        else:
            print(f"\n🎯 Target achieved! Database has {total_commands} commands")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_massive_commands())