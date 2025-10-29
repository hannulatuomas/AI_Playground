#!/usr/bin/env python3
"""
Script to populate the Linux Admin Toolbox with essential Linux commands
"""

import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from datetime import datetime, timezone

# MongoDB connection
mongo_url = "mongodb://localhost:27017"
db_name = "linux_admin_tool"

# Sample commands data
COMMANDS_DATA = [
    # File Management
    {
        "name": "ls",
        "description": "List directory contents with detailed information about files and directories",
        "syntax": "ls [options] [directory]",
        "examples": [
            "ls -la",
            "ls -lh /home/user",
            "ls -lt | head -10",
            "ls -la --color=auto"
        ],
        "category": "File Management",
        "tags": ["basic", "files", "directory", "listing"]
    },
    {
        "name": "cp",
        "description": "Copy files and directories from source to destination",
        "syntax": "cp [options] source destination",
        "examples": [
            "cp file1.txt file2.txt",
            "cp -r /source/dir /dest/dir",
            "cp -p file.txt backup/",
            "cp *.txt /backup/"
        ],
        "category": "File Management",
        "tags": ["basic", "files", "copy", "backup"]
    },
    {
        "name": "mv",
        "description": "Move or rename files and directories",
        "syntax": "mv [options] source destination",
        "examples": [
            "mv oldname.txt newname.txt",
            "mv file.txt /new/location/",
            "mv *.log /logs/",
            "mv -i file.txt dest/"
        ],
        "category": "File Management",
        "tags": ["basic", "files", "move", "rename"]
    },
    {
        "name": "find",
        "description": "Search for files and directories based on various criteria",
        "syntax": "find [path] [expression]",
        "examples": [
            "find /home -name '*.txt'",
            "find . -type f -size +100M",
            "find /var/log -mtime +7",
            "find . -name '*.py' -exec grep -l 'import os' {} \\;"
        ],
        "category": "File Management",
        "tags": ["advanced", "files", "search", "locate"]
    },
    
    # Text Processing
    {
        "name": "grep",
        "description": "Search text patterns in files using regular expressions",
        "syntax": "grep [options] pattern [file...]",
        "examples": [
            "grep 'error' /var/log/syslog",
            "grep -r 'TODO' /project/src/",
            "grep -i 'warning' *.log",
            "ps aux | grep apache"
        ],
        "category": "Text Processing",
        "tags": ["basic", "text", "search", "regex", "logs"]
    },
    {
        "name": "sed",
        "description": "Stream editor for filtering and transforming text",
        "syntax": "sed [options] 'command' [file...]",
        "examples": [
            "sed 's/old/new/g' file.txt",
            "sed -i 's/localhost/server/g' config.txt",
            "sed -n '5,10p' file.txt",
            "sed '/pattern/d' file.txt"
        ],
        "category": "Text Processing",
        "tags": ["advanced", "text", "replace", "edit", "regex"]
    },
    {
        "name": "awk",
        "description": "Pattern scanning and processing language for text manipulation",
        "syntax": "awk 'pattern { action }' [file...]",
        "examples": [
            "awk '{print $1}' file.txt",
            "awk -F':' '{print $1,$3}' /etc/passwd",
            "awk '$3 > 100' data.txt",
            "ps aux | awk '{sum+=$6} END {print sum}'"
        ],
        "category": "Text Processing",
        "tags": ["advanced", "text", "processing", "columns"]
    },
    
    # Networking
    {
        "name": "ping",
        "description": "Send ICMP echo request packets to test network connectivity",
        "syntax": "ping [options] destination",
        "examples": [
            "ping google.com",
            "ping -c 4 192.168.1.1",
            "ping -i 2 server.com",
            "ping6 ipv6.google.com"
        ],
        "category": "Networking",
        "tags": ["basic", "networking", "connectivity", "icmp"]
    },
    {
        "name": "wget",
        "description": "Download files from web servers using HTTP, HTTPS, and FTP",
        "syntax": "wget [options] [URL...]",
        "examples": [
            "wget https://example.com/file.zip",
            "wget -r -np https://site.com/folder/",
            "wget -c https://large-file.com/download",
            "wget --mirror --convert-links https://site.com/"
        ],
        "category": "Networking",
        "tags": ["basic", "networking", "download", "http", "ftp"]
    },
    {
        "name": "ssh",
        "description": "Secure Shell for remote login and command execution",
        "syntax": "ssh [options] [user@]hostname [command]",
        "examples": [
            "ssh user@server.com",
            "ssh -p 2222 admin@192.168.1.100",
            "ssh -X user@server 'gedit file.txt'",
            "ssh -L 8080:localhost:80 user@server"
        ],
        "category": "Networking",
        "tags": ["basic", "networking", "security", "remote", "ssh"]
    },
    
    # System Monitoring
    {
        "name": "top",
        "description": "Display running processes and system resource usage in real-time",
        "syntax": "top [options]",
        "examples": [
            "top",
            "top -u username",
            "top -p 1234,5678",
            "top -n 1 -b"
        ],
        "category": "System Monitoring",
        "tags": ["basic", "system", "monitoring", "processes", "cpu", "memory"]
    },
    {
        "name": "ps",
        "description": "Display information about currently running processes",
        "syntax": "ps [options]",
        "examples": [
            "ps aux",
            "ps -ef | grep apache",
            "ps -u username",
            "ps --forest"
        ],
        "category": "System Monitoring",
        "tags": ["basic", "system", "processes", "monitoring"]
    },
    {
        "name": "df",
        "description": "Display filesystem disk space usage information",
        "syntax": "df [options] [filesystem...]",
        "examples": [
            "df -h",
            "df -i",
            "df -T",
            "df /home"
        ],
        "category": "System Monitoring",
        "tags": ["basic", "system", "disk", "space", "filesystem"]
    },
    
    # User Management
    {
        "name": "sudo",
        "description": "Execute commands as another user with elevated privileges",
        "syntax": "sudo [options] command",
        "examples": [
            "sudo apt update",
            "sudo -u www-data ls /var/www",
            "sudo -i",
            "sudo systemctl restart apache2"
        ],
        "category": "User Management",
        "tags": ["basic", "security", "permissions", "admin", "user"]
    },
    {
        "name": "useradd",
        "description": "Add a new user account to the system",
        "syntax": "useradd [options] username",
        "examples": [
            "sudo useradd newuser",
            "sudo useradd -m -s /bin/bash john",
            "sudo useradd -g users -G sudo,www-data alice",
            "sudo useradd -d /custom/home -c 'Full Name' user"
        ],
        "category": "User Management",
        "tags": ["advanced", "user", "admin", "account"]
    },
    
    # Security
    {
        "name": "chmod",
        "description": "Change file and directory permissions",
        "syntax": "chmod [options] mode file...",
        "examples": [
            "chmod 755 script.sh",
            "chmod u+x file.txt",
            "chmod -R 644 /var/www/html",
            "chmod a-w sensitive.txt"
        ],
        "category": "Security",
        "tags": ["basic", "security", "permissions", "files"]
    },
    {
        "name": "chown",
        "description": "Change file and directory ownership",
        "syntax": "chown [options] owner[:group] file...",
        "examples": [
            "sudo chown user:group file.txt",
            "sudo chown -R www-data:www-data /var/www",
            "sudo chown :admin file.txt",
            "sudo chown user file1 file2"
        ],
        "category": "Security",
        "tags": ["basic", "security", "ownership", "files", "permissions"]
    },
    
    # Package Management
    {
        "name": "apt",
        "description": "Advanced Package Tool for Debian/Ubuntu package management",
        "syntax": "apt [options] command [package...]",
        "examples": [
            "sudo apt update",
            "sudo apt install nginx",
            "sudo apt upgrade",
            "sudo apt search python"
        ],
        "category": "Package Management",
        "tags": ["basic", "package", "install", "update", "debian", "ubuntu"]
    },
    {
        "name": "systemctl",
        "description": "Control systemd services and units",
        "syntax": "systemctl [options] command [unit...]",
        "examples": [
            "sudo systemctl start nginx",
            "sudo systemctl enable apache2",
            "systemctl status ssh",
            "sudo systemctl reload NetworkManager"
        ],
        "category": "Process Control",
        "tags": ["basic", "system", "service", "systemd", "control"]
    },
    
    # Process Control
    {
        "name": "kill",
        "description": "Terminate processes by sending signals",
        "syntax": "kill [options] pid...",
        "examples": [
            "kill 1234",
            "kill -9 5678",
            "kill -TERM $(pidof process_name)",
            "kill -USR1 1234"
        ],
        "category": "Process Control",
        "tags": ["basic", "processes", "signals", "terminate"]
    },
    
    # Disk Management
    {
        "name": "mount",
        "description": "Mount filesystems and storage devices",
        "syntax": "mount [options] device mountpoint",
        "examples": [
            "sudo mount /dev/sdb1 /mnt/usb",
            "sudo mount -t ntfs /dev/sdc1 /mnt/windows",
            "mount -o remount,rw /",
            "sudo mount -a"
        ],
        "category": "Disk Management",
        "tags": ["basic", "disk", "filesystem", "storage", "mount"]
    },
    {
        "name": "du",
        "description": "Display directory space usage recursively",
        "syntax": "du [options] [directory...]",
        "examples": [
            "du -h",
            "du -sh /var/log/*",
            "du -a /home/user | sort -nr | head -10",
            "du --max-depth=1 -h"
        ],
        "category": "Disk Management",
        "tags": ["basic", "disk", "space", "usage", "directory"]
    },
    
    # Additional Essential Commands
    {
        "name": "htop",
        "description": "Interactive process viewer with improved interface over top",
        "syntax": "htop [options]",
        "examples": [
            "htop",
            "htop -u username",
            "htop -p 1234,5678",
            "htop --sort-key PERCENT_CPU"
        ],
        "category": "System Monitoring",
        "tags": ["advanced", "system", "monitoring", "processes", "interactive"]
    },
    {
        "name": "rsync",
        "description": "Synchronize files and directories locally or over a network",
        "syntax": "rsync [options] source destination",
        "examples": [
            "rsync -avz /local/dir/ user@server:/remote/dir/",
            "rsync -av --delete /source/ /backup/",
            "rsync -azP file.txt user@server:~/",
            "rsync -av --exclude='*.tmp' /src/ /dst/"
        ],
        "category": "File Management",
        "tags": ["advanced", "sync", "backup", "network", "files"]
    },
    {
        "name": "tar",
        "description": "Archive files and directories into compressed packages",
        "syntax": "tar [options] archive-name files",
        "examples": [
            "tar -czvf backup.tar.gz /home/user/",
            "tar -xzvf archive.tar.gz",
            "tar -tf archive.tar.gz",
            "tar -czf - /dir | ssh user@server 'cat > backup.tar.gz'"
        ],
        "category": "File Management",
        "tags": ["basic", "compression", "archive", "backup"]
    },
    {
        "name": "netstat",
        "description": "Display network connections, routing tables, and network statistics",
        "syntax": "netstat [options]",
        "examples": [
            "netstat -tuln",
            "netstat -anp | grep :80",
            "netstat -i",
            "netstat -rn"
        ],
        "category": "Networking",
        "tags": ["basic", "networking", "connections", "ports", "monitoring"]
    },
    {
        "name": "iptables",
        "description": "Configure Linux firewall rules and packet filtering",
        "syntax": "iptables [options] -j target",
        "examples": [
            "sudo iptables -L",
            "sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT",
            "sudo iptables -A INPUT -s 192.168.1.0/24 -j ACCEPT",
            "sudo iptables -D INPUT -p tcp --dport 80 -j DROP"
        ],
        "category": "Security",
        "tags": ["advanced", "security", "firewall", "network", "admin"]
    },
    {
        "name": "crontab",
        "description": "Schedule tasks to run automatically at specified times",
        "syntax": "crontab [options]",
        "examples": [
            "crontab -e",
            "crontab -l",
            "crontab -r",
            "0 2 * * * /usr/bin/backup.sh"
        ],
        "category": "Process Control",
        "tags": ["basic", "scheduling", "automation", "cron", "service"]
    },
    {
        "name": "curl",
        "description": "Transfer data to or from servers using various protocols",
        "syntax": "curl [options] [URL...]",
        "examples": [
            "curl -O https://example.com/file.zip",
            "curl -X POST -H 'Content-Type: application/json' -d '{\"key\":\"value\"}' https://api.example.com/",
            "curl -u username:password https://secure.example.com/",
            "curl -I https://example.com/"
        ],
        "category": "Networking",
        "tags": ["basic", "networking", "http", "api", "download"]
    },
    {
        "name": "sort",
        "description": "Sort lines of text files in alphabetical or numerical order",
        "syntax": "sort [options] [file...]",
        "examples": [
            "sort file.txt",
            "sort -n numbers.txt",
            "sort -r file.txt",
            "ps aux | sort -k 3 -nr"
        ],
        "category": "Text Processing",
        "tags": ["basic", "text", "sorting", "processing"]
    },
    {
        "name": "uniq",
        "description": "Report or omit repeated lines in sorted files",
        "syntax": "uniq [options] [input [output]]",
        "examples": [
            "sort file.txt | uniq",
            "sort file.txt | uniq -c",
            "sort file.txt | uniq -d",
            "history | cut -d' ' -f2- | sort | uniq -c | sort -nr"
        ],
        "category": "Text Processing",
        "tags": ["basic", "text", "duplicates", "processing"]
    },
    {
        "name": "wc",
        "description": "Count lines, words, and characters in text files",
        "syntax": "wc [options] [file...]",
        "examples": [
            "wc file.txt",
            "wc -l *.txt",
            "wc -w document.txt",
            "find . -name '*.py' | xargs wc -l"
        ],
        "category": "Text Processing",
        "tags": ["basic", "text", "counting", "statistics"]
    },
    {
        "name": "tail",
        "description": "Display the last part of files, useful for monitoring logs",
        "syntax": "tail [options] [file...]",
        "examples": [
            "tail /var/log/syslog",
            "tail -f /var/log/apache2/access.log",
            "tail -n 50 logfile.txt",
            "tail -f /var/log/*.log"
        ],
        "category": "Text Processing",
        "tags": ["basic", "text", "logs", "monitoring", "files"]
    },
    {
        "name": "head",
        "description": "Display the first part of files",
        "syntax": "head [options] [file...]",
        "examples": [
            "head file.txt",
            "head -n 20 /var/log/syslog",
            "head -c 1024 binary.dat",
            "ls -la | head -10"
        ],
        "category": "Text Processing",
        "tags": ["basic", "text", "files", "display"]
    },
    {
        "name": "less",
        "description": "View file contents page by page with navigation",
        "syntax": "less [options] [file...]",
        "examples": [
            "less /var/log/syslog",
            "less +G largefile.txt",
            "ps aux | less",
            "less -S wide-output.txt"
        ],
        "category": "Text Processing",
        "tags": ["basic", "text", "pager", "navigation", "files"]
    },
    {
        "name": "fdisk",
        "description": "Manipulate disk partition tables",
        "syntax": "fdisk [options] device",
        "examples": [
            "sudo fdisk -l",
            "sudo fdisk /dev/sdb",
            "sudo fdisk -l /dev/sda",
            "sudo fdisk /dev/sdc"
        ],
        "category": "Disk Management",
        "tags": ["advanced", "disk", "partitions", "admin", "storage"]
    },
    {
        "name": "lsblk",
        "description": "List block devices in a tree format",
        "syntax": "lsblk [options] [device...]",
        "examples": [
            "lsblk",
            "lsblk -f",
            "lsblk -o NAME,SIZE,TYPE,MOUNTPOINT",
            "lsblk /dev/sda"
        ],
        "category": "Disk Management",
        "tags": ["basic", "disk", "block devices", "storage", "info"]
    },
    {
        "name": "free",
        "description": "Display amount of free and used memory in the system",
        "syntax": "free [options]",
        "examples": [
            "free -h",
            "free -m",
            "free -g",
            "watch -n 1 free -h"
        ],
        "category": "System Monitoring",
        "tags": ["basic", "memory", "system", "monitoring", "ram"]
    },
    {
        "name": "uptime",
        "description": "Show how long the system has been running",
        "syntax": "uptime [options]",
        "examples": [
            "uptime",
            "uptime -p",
            "uptime -s",
            "w"
        ],
        "category": "System Monitoring",
        "tags": ["basic", "system", "uptime", "load", "monitoring"]
    },
    {
        "name": "whoami",
        "description": "Display the current username",
        "syntax": "whoami",
        "examples": [
            "whoami",
            "sudo whoami",
            "echo \"Current user: $(whoami)\"",
            "id $(whoami)"
        ],
        "category": "User Management",
        "tags": ["basic", "user", "identity", "current"]
    },
    {
        "name": "id",
        "description": "Display user and group IDs",
        "syntax": "id [options] [username]",
        "examples": [
            "id",
            "id username",
            "id -u",
            "id -g username"
        ],
        "category": "User Management",
        "tags": ["basic", "user", "groups", "permissions", "identity"]
    },
    {
        "name": "which",
        "description": "Locate the executable file associated with a command",
        "syntax": "which [options] command",
        "examples": [
            "which python",
            "which -a python",
            "which ls",
            "which java"
        ],
        "category": "System Monitoring",
        "tags": ["basic", "system", "path", "executables", "location"]
    }
]

async def populate_database():
    """Populate the database with sample Linux commands"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"Connected to MongoDB: {db_name}")
    
    # Clear existing commands (optional)
    existing_count = await db.commands.count_documents({})
    print(f"Found {existing_count} existing commands")
    
    if existing_count > 0:
        print("Database already has commands. Skipping population.")
        return
    
    # Create a system user for these commands
    system_user_id = "system-admin-001"
    
    # Insert commands
    commands_to_insert = []
    for cmd_data in COMMANDS_DATA:
        command = {
            "id": str(uuid.uuid4()),
            "name": cmd_data["name"],
            "description": cmd_data["description"],
            "syntax": cmd_data["syntax"],
            "examples": cmd_data["examples"],
            "category": cmd_data["category"],
            "tags": cmd_data["tags"],
            "created_by": system_user_id,
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        commands_to_insert.append(command)
    
    # Insert all commands
    result = await db.commands.insert_many(commands_to_insert)
    print(f"✅ Successfully inserted {len(result.inserted_ids)} commands!")
    
    # Display summary by category
    print("\n📊 Commands added by category:")
    categories = {}
    for cmd in commands_to_insert:
        cat = cmd["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    for category, count in sorted(categories.items()):
        print(f"  • {category}: {count} commands")
    
    # Close connection
    client.close()
    print("\n🎉 Database population completed!")

if __name__ == "__main__":
    asyncio.run(populate_database())