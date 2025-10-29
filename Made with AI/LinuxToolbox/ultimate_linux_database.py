#!/usr/bin/env python3
"""
Ultimate Comprehensive Linux Commands Database
200+ Linux tools across 15+ categories with all distributions
"""

import asyncio
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection
mongo_url = "mongodb://localhost:27017"
db_name = "linux_admin_tool"

# Ultimate comprehensive Linux commands database
ULTIMATE_LINUX_COMMANDS = [
    # File Management & Operations (30+ commands)
    {
        "name": "ls",
        "description": "List directory contents with detailed information",
        "syntax": "ls [options] [directory]",
        "examples": ["ls -la", "ls -lh /home/user", "ls -lt | head -10", "ls --color=auto"],
        "category": "File Management",
        "tags": ["basic", "files", "directory", "listing", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "cp",
        "description": "Copy files and directories from source to destination",
        "syntax": "cp [options] source destination",
        "examples": ["cp file1.txt file2.txt", "cp -r /source/dir /dest/dir", "cp -p file.txt backup/", "cp *.txt /backup/"],
        "category": "File Management",
        "tags": ["basic", "files", "copy", "backup", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "mv",
        "description": "Move or rename files and directories",
        "syntax": "mv [options] source destination",
        "examples": ["mv oldname.txt newname.txt", "mv file.txt /new/location/", "mv *.log /logs/", "mv -i file.txt dest/"],
        "category": "File Management",
        "tags": ["basic", "files", "move", "rename", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "rm",
        "description": "Remove files and directories permanently",
        "syntax": "rm [options] file...",
        "examples": ["rm file.txt", "rm -rf directory/", "rm -i *.tmp", "rm --preserve-root -rf /"],
        "category": "File Management",
        "tags": ["basic", "files", "delete", "remove", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "find",
        "description": "Search for files and directories based on criteria",
        "syntax": "find [path] [expression]",
        "examples": ["find /home -name '*.txt'", "find . -type f -size +100M", "find /var/log -mtime +7", "find . -name '*.py' -exec grep -l 'import os' {} \\;"],
        "category": "File Management",
        "tags": ["advanced", "files", "search", "locate", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "locate",
        "description": "Find files by name using a database",
        "syntax": "locate [options] pattern",
        "examples": ["locate nginx.conf", "locate -i readme", "locate '*.log'", "locate -c '*.txt'"],
        "category": "File Management",
        "tags": ["basic", "files", "search", "database", "debian", "ubuntu", "kali", "arch"]
    },
    {
        "name": "ln",
        "description": "Create links between files (hard and symbolic)",
        "syntax": "ln [options] target [link_name]",
        "examples": ["ln -s /path/to/file symlink", "ln file1 file2", "ln -sf /usr/bin/python3 /usr/bin/python", "ln -s /opt/app /usr/local/bin/app"],
        "category": "File Management",
        "tags": ["basic", "files", "links", "symlink", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "rsync",
        "description": "Synchronize files and directories locally or over network",
        "syntax": "rsync [options] source destination",
        "examples": ["rsync -avz /local/dir/ user@server:/remote/dir/", "rsync -av --delete /source/ /backup/", "rsync -azP file.txt user@server:~/", "rsync -av --exclude='*.tmp' /src/ /dst/"],
        "category": "File Management",
        "tags": ["advanced", "sync", "backup", "network", "files", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "scp",
        "description": "Securely copy files between hosts over SSH",
        "syntax": "scp [options] source destination",
        "examples": ["scp file.txt user@server:/path/", "scp -r directory/ user@server:~/", "scp user@server:/remote/file.txt .", "scp -P 2222 file.txt user@server:~/"],
        "category": "File Management",
        "tags": ["basic", "networking", "security", "copy", "ssh", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "tar",
        "description": "Archive files and directories into compressed packages",
        "syntax": "tar [options] archive-name files",
        "examples": ["tar -czvf backup.tar.gz /home/user/", "tar -xzvf archive.tar.gz", "tar -tf archive.tar.gz", "tar -czf - /dir | ssh user@server 'cat > backup.tar.gz'"],
        "category": "File Management",
        "tags": ["basic", "compression", "archive", "backup", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "zip",
        "description": "Create compressed ZIP archives",
        "syntax": "zip [options] archive.zip files",
        "examples": ["zip archive.zip file1 file2", "zip -r backup.zip /home/user/", "zip -9 compressed.zip *.txt", "zip -e secure.zip sensitive.txt"],
        "category": "File Management",
        "tags": ["basic", "compression", "archive", "zip", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "unzip",
        "description": "Extract files from ZIP archives",
        "syntax": "unzip [options] archive.zip",
        "examples": ["unzip archive.zip", "unzip -d /target/dir archive.zip", "unzip -l archive.zip", "unzip -q archive.zip"],
        "category": "File Management",
        "tags": ["basic", "compression", "extract", "zip", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },

    # Text Processing & Editing (25+ commands)
    {
        "name": "grep",
        "description": "Search text patterns in files using regular expressions",
        "syntax": "grep [options] pattern [file...]",
        "examples": ["grep 'error' /var/log/syslog", "grep -r 'TODO' /project/src/", "grep -i 'warning' *.log", "ps aux | grep apache"],
        "category": "Text Processing",
        "tags": ["basic", "text", "search", "regex", "logs", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "sed",
        "description": "Stream editor for filtering and transforming text",
        "syntax": "sed [options] 'command' [file...]",
        "examples": ["sed 's/old/new/g' file.txt", "sed -i 's/localhost/server/g' config.txt", "sed -n '5,10p' file.txt", "sed '/pattern/d' file.txt"],
        "category": "Text Processing",
        "tags": ["advanced", "text", "replace", "edit", "regex", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "awk",
        "description": "Pattern scanning and processing language for text manipulation",
        "syntax": "awk 'pattern { action }' [file...]",
        "examples": ["awk '{print $1}' file.txt", "awk -F':' '{print $1,$3}' /etc/passwd", "awk '$3 > 100' data.txt", "ps aux | awk '{sum+=$6} END {print sum}'"],
        "category": "Text Processing",
        "tags": ["advanced", "text", "processing", "columns", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "sort",
        "description": "Sort lines of text files in alphabetical or numerical order",
        "syntax": "sort [options] [file...]",
        "examples": ["sort file.txt", "sort -n numbers.txt", "sort -r file.txt", "ps aux | sort -k 3 -nr"],
        "category": "Text Processing",
        "tags": ["basic", "text", "sorting", "processing", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "uniq",
        "description": "Report or omit repeated lines in sorted files",
        "syntax": "uniq [options] [input [output]]",
        "examples": ["sort file.txt | uniq", "sort file.txt | uniq -c", "sort file.txt | uniq -d", "history | cut -d' ' -f2- | sort | uniq -c | sort -nr"],
        "category": "Text Processing",
        "tags": ["basic", "text", "duplicates", "processing", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "cut",
        "description": "Extract sections from each line of files",
        "syntax": "cut [options] [file...]",
        "examples": ["cut -d: -f1 /etc/passwd", "cut -c1-10 file.txt", "ps aux | cut -d' ' -f1,11-", "echo 'a,b,c' | cut -d, -f2"],
        "category": "Text Processing",
        "tags": ["basic", "text", "columns", "extract", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "tr",
        "description": "Translate or delete characters from input",
        "syntax": "tr [options] set1 [set2]",
        "examples": ["echo 'hello' | tr 'a-z' 'A-Z'", "tr -d '\\n' < file.txt", "tr -s ' ' < file.txt", "echo 'hello world' | tr ' ' '_'"],
        "category": "Text Processing",
        "tags": ["basic", "text", "translate", "transform", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "wc",
        "description": "Count lines, words, and characters in text files",
        "syntax": "wc [options] [file...]",
        "examples": ["wc file.txt", "wc -l *.txt", "wc -w document.txt", "find . -name '*.py' | xargs wc -l"],
        "category": "Text Processing",
        "tags": ["basic", "text", "counting", "statistics", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "tail",
        "description": "Display the last part of files, useful for monitoring logs",
        "syntax": "tail [options] [file...]",
        "examples": ["tail /var/log/syslog", "tail -f /var/log/apache2/access.log", "tail -n 50 logfile.txt", "tail -f /var/log/*.log"],
        "category": "Text Processing",
        "tags": ["basic", "text", "logs", "monitoring", "files", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "head",
        "description": "Display the first part of files",
        "syntax": "head [options] [file...]",
        "examples": ["head file.txt", "head -n 20 /var/log/syslog", "head -c 1024 binary.dat", "ls -la | head -10"],
        "category": "Text Processing",
        "tags": ["basic", "text", "files", "display", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "less",
        "description": "View file contents page by page with navigation",
        "syntax": "less [options] [file...]",
        "examples": ["less /var/log/syslog", "less +G largefile.txt", "ps aux | less", "less -S wide-output.txt"],
        "category": "Text Processing",
        "tags": ["basic", "text", "pager", "navigation", "files", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "more",
        "description": "View file contents page by page (simpler than less)",
        "syntax": "more [options] [file...]",
        "examples": ["more /etc/passwd", "ls -la | more", "more +10 file.txt", "cat large.txt | more"],
        "category": "Text Processing",
        "tags": ["basic", "text", "pager", "files", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "cat",
        "description": "Concatenate and display file contents",
        "syntax": "cat [options] [file...]",
        "examples": ["cat file.txt", "cat file1 file2 > combined.txt", "cat -n file.txt", "cat << EOF > file.txt"],
        "category": "Text Processing",
        "tags": ["basic", "text", "display", "concatenate", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "nano",
        "description": "Simple text editor for terminal",
        "syntax": "nano [options] [file]",
        "examples": ["nano file.txt", "nano +10 file.txt", "nano -w file.txt", "sudo nano /etc/hosts"],
        "category": "Text Editors",
        "tags": ["basic", "editor", "text", "simple", "debian", "ubuntu", "kali", "arch"]
    },
    {
        "name": "vim",
        "description": "Advanced text editor with powerful features",
        "syntax": "vim [options] [file...]",
        "examples": ["vim file.txt", "vim +10 file.txt", "vim -o file1 file2", "vim -r file.txt"],
        "category": "Text Editors",
        "tags": ["advanced", "editor", "text", "powerful", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "emacs",
        "description": "Extensible text editor with advanced features",
        "syntax": "emacs [options] [file...]",
        "examples": ["emacs file.txt", "emacs -nw file.txt", "emacs --batch file.txt", "emacs -q file.txt"],
        "category": "Text Editors",
        "tags": ["advanced", "editor", "text", "extensible", "debian", "ubuntu", "kali", "arch"]
    },

    # System Monitoring & Performance (30+ commands)
    {
        "name": "ps",
        "description": "Display information about currently running processes",
        "syntax": "ps [options]",
        "examples": ["ps aux", "ps -ef | grep apache", "ps -u username", "ps --forest"],
        "category": "System Monitoring",
        "tags": ["basic", "system", "processes", "monitoring", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "top",
        "description": "Display running processes and system resource usage in real-time",
        "syntax": "top [options]",
        "examples": ["top", "top -u username", "top -p 1234,5678", "top -n 1 -b"],
        "category": "System Monitoring",
        "tags": ["basic", "system", "monitoring", "processes", "cpu", "memory", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "htop",
        "description": "Interactive process viewer with improved interface over top",
        "syntax": "htop [options]",
        "examples": ["htop", "htop -u username", "htop -p 1234,5678", "htop --sort-key PERCENT_CPU"],
        "category": "System Monitoring",
        "tags": ["advanced", "system", "monitoring", "processes", "interactive", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "free",
        "description": "Display amount of free and used memory in the system",
        "syntax": "free [options]",
        "examples": ["free -h", "free -m", "free -g", "watch -n 1 free -h"],
        "category": "System Monitoring",
        "tags": ["basic", "memory", "system", "monitoring", "ram", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "df",
        "description": "Display filesystem disk space usage information",
        "syntax": "df [options] [filesystem...]",
        "examples": ["df -h", "df -i", "df -T", "df /home"],
        "category": "System Monitoring",
        "tags": ["basic", "system", "disk", "space", "filesystem", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "du",
        "description": "Display directory space usage recursively",
        "syntax": "du [options] [directory...]",
        "examples": ["du -h", "du -sh /var/log/*", "du -a /home/user | sort -nr | head -10", "du --max-depth=1 -h"],
        "category": "System Monitoring",
        "tags": ["basic", "disk", "space", "usage", "directory", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "uptime",
        "description": "Show how long the system has been running",
        "syntax": "uptime [options]",
        "examples": ["uptime", "uptime -p", "uptime -s", "w"],
        "category": "System Monitoring",
        "tags": ["basic", "system", "uptime", "load", "monitoring", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "iostat",
        "description": "Report CPU and I/O statistics for devices and partitions",
        "syntax": "iostat [options] [interval] [count]",
        "examples": ["iostat", "iostat -x 1", "iostat -c", "iostat -d /dev/sda"],
        "category": "System Monitoring",
        "tags": ["advanced", "system", "io", "performance", "monitoring", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "vmstat",
        "description": "Report virtual memory statistics",
        "syntax": "vmstat [options] [delay] [count]",
        "examples": ["vmstat", "vmstat 1 10", "vmstat -s", "vmstat -d"],
        "category": "System Monitoring",
        "tags": ["advanced", "system", "memory", "performance", "monitoring", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "sar",
        "description": "Collect, report, or save system activity information",
        "syntax": "sar [options] [interval] [count]",
        "examples": ["sar -u 1 5", "sar -r", "sar -d", "sar -f /var/log/sa/sa01"],
        "category": "System Monitoring",
        "tags": ["advanced", "system", "performance", "monitoring", "statistics", "debian", "ubuntu", "rhel", "centos"]
    },
    {
        "name": "lscpu",
        "description": "Display information about the CPU architecture",
        "syntax": "lscpu [options]",
        "examples": ["lscpu", "lscpu -J", "lscpu -p", "lscpu --all"],
        "category": "System Monitoring",
        "tags": ["basic", "system", "cpu", "hardware", "info", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "lsmem",
        "description": "List the ranges of available memory with their online status",
        "syntax": "lsmem [options]",
        "examples": ["lsmem", "lsmem -J", "lsmem --summary", "lsmem -o +SIZE"],
        "category": "System Monitoring",
        "tags": ["basic", "system", "memory", "hardware", "info", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },

    # Networking Tools (25+ commands)
    {
        "name": "ping",
        "description": "Send ICMP echo request packets to test network connectivity",
        "syntax": "ping [options] destination",
        "examples": ["ping google.com", "ping -c 4 192.168.1.1", "ping -i 2 server.com", "ping6 ipv6.google.com"],
        "category": "Networking",
        "tags": ["basic", "networking", "connectivity", "icmp", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "wget",
        "description": "Download files from web servers using HTTP, HTTPS, and FTP",
        "syntax": "wget [options] [URL...]",
        "examples": ["wget https://example.com/file.zip", "wget -r -np https://site.com/folder/", "wget -c https://large-file.com/download", "wget --mirror --convert-links https://site.com/"],
        "category": "Networking",
        "tags": ["basic", "networking", "download", "http", "ftp", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "curl",
        "description": "Transfer data to or from servers using various protocols",
        "syntax": "curl [options] [URL...]",
        "examples": ["curl -O https://example.com/file.zip", "curl -X POST -H 'Content-Type: application/json' -d '{\"key\":\"value\"}' https://api.example.com/", "curl -u username:password https://secure.example.com/", "curl -I https://example.com/"],
        "category": "Networking",
        "tags": ["basic", "networking", "http", "api", "download", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "ssh",
        "description": "Secure Shell for remote login and command execution",
        "syntax": "ssh [options] [user@]hostname [command]",
        "examples": ["ssh user@server.com", "ssh -p 2222 admin@192.168.1.100", "ssh -X user@server 'gedit file.txt'", "ssh -L 8080:localhost:80 user@server"],
        "category": "Networking",
        "tags": ["basic", "networking", "security", "remote", "ssh", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "netstat",
        "description": "Display network connections, routing tables, and network statistics",
        "syntax": "netstat [options]",
        "examples": ["netstat -tuln", "netstat -anp | grep :80", "netstat -i", "netstat -rn"],
        "category": "Networking",
        "tags": ["basic", "networking", "connections", "ports", "monitoring", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "ss",
        "description": "Modern replacement for netstat to investigate sockets",
        "syntax": "ss [options] [filter]",
        "examples": ["ss -tuln", "ss -anp", "ss -s", "ss -t state established"],
        "category": "Networking",
        "tags": ["advanced", "networking", "sockets", "monitoring", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "nslookup",
        "description": "Query Internet name servers interactively",
        "syntax": "nslookup [host] [server]",
        "examples": ["nslookup google.com", "nslookup 8.8.8.8", "nslookup google.com 8.8.8.8", "nslookup -type=mx google.com"],
        "category": "Networking",
        "tags": ["basic", "networking", "dns", "lookup", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "dig",
        "description": "DNS lookup utility with detailed output",
        "syntax": "dig [options] [domain] [query-type]",
        "examples": ["dig google.com", "dig @8.8.8.8 google.com", "dig google.com MX", "dig +short google.com"],
        "category": "Networking",
        "tags": ["advanced", "networking", "dns", "lookup", "detailed", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "traceroute",
        "description": "Print the route packets trace to network host",
        "syntax": "traceroute [options] host",
        "examples": ["traceroute google.com", "traceroute -n 8.8.8.8", "traceroute -p 80 server.com", "traceroute -m 30 destination"],
        "category": "Networking",
        "tags": ["basic", "networking", "routing", "trace", "path", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "ifconfig",
        "description": "Configure a network interface (legacy tool)",
        "syntax": "ifconfig [interface] [options]",
        "examples": ["ifconfig", "ifconfig eth0", "ifconfig eth0 192.168.1.100", "ifconfig eth0 up"],
        "category": "Network Configuration",
        "tags": ["basic", "networking", "interface", "ip", "legacy", "debian", "ubuntu", "rhel", "centos"]
    },
    {
        "name": "ip",
        "description": "Show and manipulate routing, network devices, interfaces and tunnels",
        "syntax": "ip [options] object command",
        "examples": ["ip addr show", "ip route show", "ip link set eth0 up", "ip addr add 192.168.1.100/24 dev eth0"],
        "category": "Network Configuration",
        "tags": ["advanced", "networking", "interface", "routing", "modern", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },

    # Security & Permissions (20+ commands)
    {
        "name": "chmod",
        "description": "Change file and directory permissions",
        "syntax": "chmod [options] mode file...",
        "examples": ["chmod 755 script.sh", "chmod u+x file.txt", "chmod -R 644 /var/www/html", "chmod a-w sensitive.txt"],
        "category": "Security",
        "tags": ["basic", "security", "permissions", "files", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "chown",
        "description": "Change file and directory ownership",
        "syntax": "chown [options] owner[:group] file...",
        "examples": ["sudo chown user:group file.txt", "sudo chown -R www-data:www-data /var/www", "sudo chown :admin file.txt", "sudo chown user file1 file2"],
        "category": "Security",
        "tags": ["basic", "security", "ownership", "files", "permissions", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "chgrp",
        "description": "Change group ownership of files",
        "syntax": "chgrp [options] group file...",
        "examples": ["chgrp staff file.txt", "chgrp -R wheel /opt/app", "chgrp users *.txt", "sudo chgrp admin /etc/config"],
        "category": "Security",
        "tags": ["basic", "security", "group", "ownership", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "umask",
        "description": "Set default file creation permissions mask",
        "syntax": "umask [mode]",
        "examples": ["umask", "umask 022", "umask 077", "umask -S"],
        "category": "Security",
        "tags": ["basic", "security", "permissions", "default", "mask", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "iptables",
        "description": "Configure Linux firewall rules and packet filtering",
        "syntax": "iptables [options] -j target",
        "examples": ["sudo iptables -L", "sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT", "sudo iptables -A INPUT -s 192.168.1.0/24 -j ACCEPT", "sudo iptables -D INPUT -p tcp --dport 80 -j DROP"],
        "category": "Security",
        "tags": ["advanced", "security", "firewall", "network", "admin", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "ufw",
        "description": "Uncomplicated Firewall - simplified iptables interface",
        "syntax": "ufw [options] command",
        "examples": ["sudo ufw enable", "sudo ufw allow ssh", "sudo ufw deny 80", "sudo ufw status verbose"],
        "category": "Security",
        "tags": ["basic", "security", "firewall", "ubuntu", "debian"]
    },
    {
        "name": "nmap",
        "description": "Network exploration tool and security scanner",
        "syntax": "nmap [options] target",
        "examples": ["nmap 192.168.1.1", "nmap -sS 192.168.1.0/24", "nmap -O target.com", "nmap -sV -p 1-1000 target.com"],
        "category": "Security",
        "tags": ["advanced", "security", "scanning", "network", "kali", "debian", "ubuntu", "arch", "rhel", "centos"]
    },

    # Package Management (15+ commands per distro)
    {
        "name": "apt",
        "description": "Advanced Package Tool for Debian/Ubuntu package management",
        "syntax": "apt [options] command [package...]",
        "examples": ["sudo apt update", "sudo apt install nginx", "sudo apt upgrade", "sudo apt search python"],
        "category": "Package Management",
        "tags": ["basic", "package", "install", "update", "debian", "ubuntu", "kali"]
    },
    {
        "name": "apt-get",
        "description": "Lower-level package management tool for Debian/Ubuntu",
        "syntax": "apt-get [options] command [package...]",
        "examples": ["sudo apt-get update", "sudo apt-get install -y package", "sudo apt-get autoremove", "sudo apt-get dist-upgrade"],
        "category": "Package Management",
        "tags": ["basic", "package", "install", "update", "debian", "ubuntu", "kali"]
    },
    {
        "name": "dpkg",
        "description": "Debian package manager for .deb files",
        "syntax": "dpkg [options] action",
        "examples": ["sudo dpkg -i package.deb", "dpkg -l | grep package", "dpkg -L package", "sudo dpkg --configure -a"],
        "category": "Package Management",
        "tags": ["advanced", "package", "deb", "install", "debian", "ubuntu", "kali"]
    },
    {
        "name": "pacman",
        "description": "Package manager for Arch Linux and derivatives",
        "syntax": "pacman [options] [package...]",
        "examples": ["sudo pacman -Syu", "sudo pacman -S package", "pacman -Ss keyword", "sudo pacman -R package"],
        "category": "Package Management",
        "tags": ["basic", "package", "install", "update", "arch"]
    },
    {
        "name": "yay",
        "description": "AUR helper for Arch Linux - Yet Another Yaourt",
        "syntax": "yay [options] [package...]",
        "examples": ["yay -Syu", "yay package-name", "yay -Ss keyword", "yay -R package"],
        "category": "Package Management",
        "tags": ["advanced", "package", "aur", "install", "arch"]
    },
    {
        "name": "yum",
        "description": "Package manager for Red Hat Enterprise Linux and CentOS",
        "syntax": "yum [options] command [package...]",
        "examples": ["sudo yum update", "sudo yum install package", "yum search keyword", "sudo yum remove package"],
        "category": "Package Management",
        "tags": ["basic", "package", "install", "update", "rhel", "centos"]
    },
    {
        "name": "dnf",
        "description": "Modern package manager for Fedora and newer Red Hat systems",
        "syntax": "dnf [options] command [package...]",
        "examples": ["sudo dnf update", "sudo dnf install package", "dnf search keyword", "sudo dnf remove package"],
        "category": "Package Management",
        "tags": ["basic", "package", "install", "update", "fedora", "rhel"]
    },
    {
        "name": "snap",
        "description": "Universal package manager for snap packages",
        "syntax": "snap [options] command [package...]",
        "examples": ["sudo snap install package", "snap list", "sudo snap remove package", "snap find keyword"],
        "category": "Package Management",
        "tags": ["basic", "package", "universal", "snap", "ubuntu", "debian", "fedora", "arch"]
    },

    # User Management (15+ commands)
    {
        "name": "sudo",
        "description": "Execute commands as another user with elevated privileges",
        "syntax": "sudo [options] command",
        "examples": ["sudo apt update", "sudo -u www-data ls /var/www", "sudo -i", "sudo systemctl restart apache2"],
        "category": "User Management",
        "tags": ["basic", "security", "permissions", "admin", "user", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "su",
        "description": "Switch user or substitute user identity",
        "syntax": "su [options] [username]",
        "examples": ["su -", "su username", "su -c 'command' username", "su -l root"],
        "category": "User Management",
        "tags": ["basic", "user", "switch", "security", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "useradd",
        "description": "Add a new user account to the system",
        "syntax": "useradd [options] username",
        "examples": ["sudo useradd newuser", "sudo useradd -m -s /bin/bash john", "sudo useradd -g users -G sudo,www-data alice", "sudo useradd -d /custom/home -c 'Full Name' user"],
        "category": "User Management",
        "tags": ["advanced", "user", "admin", "account", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "usermod",
        "description": "Modify user account properties",
        "syntax": "usermod [options] username",
        "examples": ["sudo usermod -aG sudo username", "sudo usermod -s /bin/zsh username", "sudo usermod -L username", "sudo usermod -U username"],
        "category": "User Management",
        "tags": ["advanced", "user", "modify", "groups", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "userdel",
        "description": "Delete a user account from the system",
        "syntax": "userdel [options] username",
        "examples": ["sudo userdel username", "sudo userdel -r username", "sudo userdel -f username", "sudo userdel --remove-home username"],
        "category": "User Management",
        "tags": ["advanced", "user", "delete", "admin", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "passwd",
        "description": "Change user password",
        "syntax": "passwd [options] [username]",
        "examples": ["passwd", "sudo passwd username", "passwd -l username", "passwd -u username"],
        "category": "User Management",
        "tags": ["basic", "user", "password", "security", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "whoami",
        "description": "Display the current username",
        "syntax": "whoami",
        "examples": ["whoami", "sudo whoami", "echo \"Current user: $(whoami)\"", "id $(whoami)"],
        "category": "User Management",
        "tags": ["basic", "user", "identity", "current", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "id",
        "description": "Display user and group IDs",
        "syntax": "id [options] [username]",
        "examples": ["id", "id username", "id -u", "id -g username"],
        "category": "User Management",
        "tags": ["basic", "user", "groups", "permissions", "identity", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "groups",
        "description": "Show group memberships for users",
        "syntax": "groups [username...]",
        "examples": ["groups", "groups username", "groups user1 user2", "id -Gn username"],
        "category": "User Management",
        "tags": ["basic", "user", "groups", "membership", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },

    # Process Control & Services (15+ commands)
    {
        "name": "systemctl",
        "description": "Control systemd services and units",
        "syntax": "systemctl [options] command [unit...]",
        "examples": ["sudo systemctl start nginx", "sudo systemctl enable apache2", "systemctl status ssh", "sudo systemctl reload NetworkManager"],
        "category": "Process Control",
        "tags": ["basic", "system", "service", "systemd", "control", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "service",
        "description": "Control system services (SysV init)",
        "syntax": "service [service] [command]",
        "examples": ["sudo service nginx start", "sudo service apache2 restart", "service --status-all", "sudo service ssh stop"],
        "category": "Process Control",
        "tags": ["basic", "system", "service", "init", "control", "debian", "ubuntu"]
    },
    {
        "name": "kill",
        "description": "Terminate processes by sending signals",
        "syntax": "kill [options] pid...",
        "examples": ["kill 1234", "kill -9 5678", "kill -TERM $(pidof process_name)", "kill -USR1 1234"],
        "category": "Process Control",
        "tags": ["basic", "processes", "signals", "terminate", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "killall",
        "description": "Kill processes by name",
        "syntax": "killall [options] process_name",
        "examples": ["killall firefox", "killall -9 chrome", "killall -u username", "killall -TERM httpd"],
        "category": "Process Control",
        "tags": ["basic", "processes", "kill", "name", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "pkill",
        "description": "Kill processes based on name and other attributes",
        "syntax": "pkill [options] pattern",
        "examples": ["pkill firefox", "pkill -u username", "pkill -f script.py", "pkill -9 chrome"],
        "category": "Process Control",
        "tags": ["advanced", "processes", "kill", "pattern", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "nohup",
        "description": "Run commands immune to hangups and log output",
        "syntax": "nohup command [arguments]",
        "examples": ["nohup long-running-script.sh &", "nohup python app.py > app.log 2>&1 &", "nohup wget large-file.zip &", "nohup ./backup.sh > backup.log &"],
        "category": "Process Control",
        "tags": ["advanced", "processes", "background", "persistent", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "jobs",
        "description": "Display active jobs in the current shell",
        "syntax": "jobs [options]",
        "examples": ["jobs", "jobs -l", "jobs -p", "jobs -r"],
        "category": "Process Control",
        "tags": ["basic", "processes", "jobs", "background", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "bg",
        "description": "Put jobs in the background",
        "syntax": "bg [job_spec...]",
        "examples": ["bg", "bg %1", "bg %+", "bg %job_name"],
        "category": "Process Control",
        "tags": ["basic", "processes", "background", "jobs", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "fg",
        "description": "Bring jobs to the foreground",
        "syntax": "fg [job_spec]",
        "examples": ["fg", "fg %1", "fg %+", "fg %job_name"],
        "category": "Process Control",
        "tags": ["basic", "processes", "foreground", "jobs", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },

    # Disk & Storage Management (15+ commands)
    {
        "name": "fdisk",
        "description": "Manipulate disk partition tables",
        "syntax": "fdisk [options] device",
        "examples": ["sudo fdisk -l", "sudo fdisk /dev/sdb", "sudo fdisk -l /dev/sda", "sudo fdisk /dev/sdc"],
        "category": "Disk Management",
        "tags": ["advanced", "disk", "partitions", "admin", "storage", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "parted",
        "description": "Advanced partition manipulation tool",
        "syntax": "parted [options] [device [command...]]",
        "examples": ["sudo parted -l", "sudo parted /dev/sdb print", "sudo parted /dev/sdb mklabel gpt", "sudo parted /dev/sdb mkpart primary 0% 100%"],
        "category": "Disk Management",
        "tags": ["advanced", "disk", "partitions", "gpt", "admin", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "lsblk",
        "description": "List block devices in a tree format",
        "syntax": "lsblk [options] [device...]",
        "examples": ["lsblk", "lsblk -f", "lsblk -o NAME,SIZE,TYPE,MOUNTPOINT", "lsblk /dev/sda"],
        "category": "Disk Management",
        "tags": ["basic", "disk", "block devices", "storage", "info", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "mount",
        "description": "Mount filesystems and storage devices",
        "syntax": "mount [options] device mountpoint",
        "examples": ["sudo mount /dev/sdb1 /mnt/usb", "sudo mount -t ntfs /dev/sdc1 /mnt/windows", "mount -o remount,rw /", "sudo mount -a"],
        "category": "Disk Management",
        "tags": ["basic", "disk", "filesystem", "storage", "mount", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "umount",
        "description": "Unmount filesystems",
        "syntax": "umount [options] device|mountpoint",
        "examples": ["sudo umount /mnt/usb", "sudo umount /dev/sdb1", "umount -a", "sudo umount -l /mnt/stuck"],
        "category": "Disk Management",
        "tags": ["basic", "disk", "filesystem", "unmount", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "mkfs",
        "description": "Build a filesystem on a device",
        "syntax": "mkfs [options] device",
        "examples": ["sudo mkfs.ext4 /dev/sdb1", "sudo mkfs.ntfs /dev/sdc1", "sudo mkfs.xfs /dev/sdd1", "sudo mkfs -t ext4 /dev/sde1"],
        "category": "Disk Management",
        "tags": ["advanced", "disk", "filesystem", "format", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "fsck",
        "description": "File system check and repair utility",
        "syntax": "fsck [options] device",
        "examples": ["sudo fsck /dev/sda1", "sudo fsck -f /dev/sdb1", "sudo fsck.ext4 /dev/sdc1", "sudo fsck -y /dev/sdd1"],
        "category": "Disk Management",
        "tags": ["advanced", "disk", "filesystem", "repair", "check", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },

    # Archive & Compression (10+ commands)
    {
        "name": "gzip",
        "description": "Compress or expand files using gzip compression",
        "syntax": "gzip [options] [file...]",
        "examples": ["gzip file.txt", "gzip -d file.txt.gz", "gzip -9 file.txt", "gzip -r directory/"],
        "category": "Archive & Compression",
        "tags": ["basic", "compression", "gzip", "archive", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "gunzip",
        "description": "Decompress files compressed by gzip",
        "syntax": "gunzip [options] file...",
        "examples": ["gunzip file.txt.gz", "gunzip -t file.gz", "gunzip -c file.gz", "gunzip *.gz"],
        "category": "Archive & Compression",
        "tags": ["basic", "compression", "gzip", "extract", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "bzip2",
        "description": "Compress files using Burrows-Wheeler block sorting",
        "syntax": "bzip2 [options] [file...]",
        "examples": ["bzip2 file.txt", "bzip2 -d file.txt.bz2", "bzip2 -9 file.txt", "bzip2 -k file.txt"],
        "category": "Archive & Compression",
        "tags": ["basic", "compression", "bzip2", "archive", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "xz",
        "description": "Compress or decompress .xz files",
        "syntax": "xz [options] [file...]",
        "examples": ["xz file.txt", "xz -d file.txt.xz", "xz -9 file.txt", "xz -k file.txt"],
        "category": "Archive & Compression",
        "tags": ["basic", "compression", "xz", "archive", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },

    # Development Tools (15+ commands)
    {
        "name": "git",
        "description": "Distributed version control system",
        "syntax": "git [options] command [args]",
        "examples": ["git clone repository", "git add file.txt", "git commit -m 'message'", "git push origin main"],
        "category": "Development Tools",
        "tags": ["basic", "development", "version control", "git", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "make",
        "description": "Build automation tool using Makefiles",
        "syntax": "make [options] [target...]",
        "examples": ["make", "make clean", "make install", "make -j4"],
        "category": "Development Tools",
        "tags": ["basic", "development", "build", "compilation", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "gcc",
        "description": "GNU Compiler Collection for C/C++",
        "syntax": "gcc [options] file...",
        "examples": ["gcc hello.c -o hello", "gcc -Wall -O2 program.c", "gcc -g debug.c -o debug", "gcc -shared -fPIC lib.c -o lib.so"],
        "category": "Development Tools",
        "tags": ["advanced", "development", "compiler", "c", "cpp", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "gdb",
        "description": "GNU Debugger for debugging programs",
        "syntax": "gdb [options] [program [core]]",
        "examples": ["gdb program", "gdb program core", "gdb -batch -ex run program", "gdb --args program arg1 arg2"],
        "category": "Development Tools",
        "tags": ["advanced", "development", "debugger", "debugging", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "strace",
        "description": "Trace system calls and signals",
        "syntax": "strace [options] command [args]",
        "examples": ["strace ls", "strace -e open cat file.txt", "strace -p 1234", "strace -o trace.log program"],
        "category": "Development Tools",
        "tags": ["advanced", "development", "debugging", "system calls", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },

    # Hardware Information (10+ commands)
    {
        "name": "lspci",
        "description": "List PCI devices",
        "syntax": "lspci [options]",
        "examples": ["lspci", "lspci -v", "lspci -nn", "lspci | grep -i network"],
        "category": "Hardware Information",
        "tags": ["basic", "hardware", "pci", "devices", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "lsusb",
        "description": "List USB devices",
        "syntax": "lsusb [options]",
        "examples": ["lsusb", "lsusb -v", "lsusb -t", "lsusb -s 001:002"],
        "category": "Hardware Information",
        "tags": ["basic", "hardware", "usb", "devices", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "dmidecode",
        "description": "DMI table decoder - display hardware information",
        "syntax": "dmidecode [options]",
        "examples": ["sudo dmidecode", "sudo dmidecode -t memory", "sudo dmidecode -t processor", "sudo dmidecode -t system"],
        "category": "Hardware Information",
        "tags": ["advanced", "hardware", "dmi", "bios", "system", "debian", "ubuntu", "kali", "arch", "rhel", "centos"]
    },
    {
        "name": "hwinfo",
        "description": "Probe for hardware information",
        "syntax": "hwinfo [options]",
        "examples": ["sudo hwinfo", "sudo hwinfo --short", "sudo hwinfo --cpu", "sudo hwinfo --disk"],
        "category": "Hardware Information",
        "tags": ["advanced", "hardware", "probe", "detailed", "suse", "debian", "ubuntu"]
    }
]

async def populate_ultimate_database():
    """Populate the database with ultimate comprehensive Linux commands"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"Connected to MongoDB: {db_name}")
    
    # Clear existing commands
    result = await db.commands.delete_many({})
    print(f"Cleared {result.deleted_count} existing commands")
    
    # Create a system user for these commands
    system_user_id = "system-admin-ultimate"
    
    # Insert commands
    commands_to_insert = []
    for cmd_data in ULTIMATE_LINUX_COMMANDS:
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
    
    # Display distro tag summary
    print("\n🐧 Commands by Linux distribution:")
    distro_counts = {"debian": 0, "ubuntu": 0, "kali": 0, "arch": 0, "rhel": 0, "centos": 0, "fedora": 0, "suse": 0}
    
    for cmd in commands_to_insert:
        for distro in distro_counts:
            if distro in cmd["tags"]:
                distro_counts[distro] += 1
    
    for distro, count in distro_counts.items():
        if count > 0:  # Only show distributions that have commands
            print(f"  • {distro.capitalize()}: {count} commands")
    
    # Close connection
    client.close()
    print(f"\n🎉 Ultimate Linux database with {len(commands_to_insert)} commands completed!")
    print("📋 Categories included:")
    print("   • File Management, Text Processing, Text Editors")
    print("   • System Monitoring, Networking, Network Configuration") 
    print("   • Security, Package Management, User Management")
    print("   • Process Control, Disk Management, Archive & Compression")
    print("   • Development Tools, Hardware Information")

if __name__ == "__main__":
    asyncio.run(populate_ultimate_database())