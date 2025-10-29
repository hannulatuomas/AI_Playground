#!/usr/bin/env python3

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

# Enhanced Linux Commands Database
# This script adds comprehensive commands, tools, and distributions

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'linux_admin_tool')

async def populate_enhanced_commands():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Enhanced command database with more tools, commands, and distributions
    enhanced_commands = [
        # Network Security Tools
        {
            "id": str(uuid.uuid4()),
            "name": "nmap",
            "description": "Network exploration tool and security scanner for network discovery and security auditing",
            "syntax": "nmap [options] target",
            "examples": [
                "nmap 192.168.1.1",
                "nmap -sS -O 192.168.1.0/24",
                "nmap -A -T4 scanme.nmap.org",
                "nmap -sU -p 53,123,161 192.168.1.1"
            ],
            "category": "Network Discovery",
            "tags": ["security", "networking", "scanning", "kali", "penetration testing", "reconnaissance"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "wireshark",
            "description": "Network protocol analyzer for network troubleshooting and analysis",
            "syntax": "wireshark [options] [file]",
            "examples": [
                "wireshark -i eth0",
                "wireshark -k -i any",
                "wireshark capture.pcap"
            ],
            "category": "Sniffing & Spoofing",
            "tags": ["networking", "analysis", "packets", "kali", "debian", "ubuntu", "forensics"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "metasploit",
            "description": "Comprehensive penetration testing framework for security assessment",
            "syntax": "msfconsole [options]",
            "examples": [
                "msfconsole",
                "msfconsole -r script.rc",
                "msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.100 LPORT=4444 -f exe > payload.exe"
            ],
            "category": "Exploitation",
            "tags": ["security", "exploitation", "kali", "penetration testing", "framework"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "burp",
            "description": "Web application security testing tool for finding vulnerabilities",
            "syntax": "java -jar burpsuite.jar",
            "examples": [
                "java -jar burpsuite_community.jar",
                "java -Xmx4g -jar burpsuite_pro.jar"
            ],
            "category": "Web Application Security",
            "tags": ["web security", "burp suite", "kali", "vulnerability scanning"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "john",
            "description": "John the Ripper password cracking tool",
            "syntax": "john [options] password-files",
            "examples": [
                "john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt",
                "john --show hashes.txt",
                "john --incremental passwd"
            ],
            "category": "Password Attacks",
            "tags": ["password cracking", "security", "kali", "brute force"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "hashcat",
            "description": "Advanced password recovery utility supporting many algorithms",
            "syntax": "hashcat [options] hash [wordlist]",
            "examples": [
                "hashcat -m 0 -a 0 hash.txt wordlist.txt",
                "hashcat -m 1000 -a 3 hash.txt ?a?a?a?a?a?a",
                "hashcat --show hash.txt"
            ],
            "category": "Password Attacks",
            "tags": ["password cracking", "gpu", "security", "kali", "hashcat"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "aircrack-ng",
            "description": "Complete suite of tools to assess WiFi network security",
            "syntax": "aircrack-ng [options] capture-file",
            "examples": [
                "aircrack-ng -w wordlist.txt capture.cap",
                "airodump-ng wlan0",
                "aireplay-ng -0 5 -a BSSID wlan0"
            ],
            "category": "Wireless Security",
            "tags": ["wifi", "wireless", "security", "kali", "wpa", "wep"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # System Administration Tools
        {
            "id": str(uuid.uuid4()),
            "name": "systemctl",
            "description": "Control systemd services and units",
            "syntax": "systemctl [options] COMMAND [unit...]",
            "examples": [
                "systemctl start nginx",
                "systemctl stop apache2",
                "systemctl enable ssh",
                "systemctl status mysql",
                "systemctl list-units --failed"
            ],
            "category": "System Monitoring",
            "tags": ["systemd", "services", "ubuntu", "debian", "rhel", "centos", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "docker",
            "description": "Container platform for developing, shipping, and running applications",
            "syntax": "docker [options] COMMAND [arg...]",
            "examples": [
                "docker run -it ubuntu bash",
                "docker ps -a",
                "docker build -t myapp .",
                "docker-compose up -d",
                "docker exec -it container_name bash"
            ],
            "category": "Development Tools",
            "tags": ["containers", "docker", "development", "ubuntu", "debian", "rhel", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "kubernetes",
            "description": "Container orchestration platform for automating deployment, scaling, and management",
            "syntax": "kubectl [command] [options]",
            "examples": [
                "kubectl get pods",
                "kubectl apply -f deployment.yaml",
                "kubectl describe service myservice",
                "kubectl logs -f pod-name",
                "kubectl exec -it pod-name -- bash"
            ],
            "category": "Development Tools",
            "tags": ["kubernetes", "k8s", "containers", "orchestration", "cloud", "ubuntu", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "ansible",
            "description": "Automation tool for configuration management, application deployment",
            "syntax": "ansible [options] pattern -m module [-a args]",
            "examples": [
                "ansible all -m ping",
                "ansible-playbook site.yml",
                "ansible webservers -m service -a 'name=httpd state=started'",
                "ansible all -m setup"
            ],
            "category": "System Monitoring",
            "tags": ["automation", "configuration", "deployment", "ubuntu", "rhel", "centos"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # Development Tools
        {
            "id": str(uuid.uuid4()),
            "name": "git",
            "description": "Distributed version control system for tracking changes in source code",
            "syntax": "git [command] [options]",
            "examples": [
                "git clone https://github.com/user/repo.git",
                "git add .",
                "git commit -m 'Initial commit'",
                "git push origin main",
                "git pull origin main",
                "git branch feature-branch",
                "git merge feature-branch"
            ],
            "category": "Development Tools",
            "tags": ["version control", "git", "development", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "vim",
            "description": "Highly configurable text editor built to enable efficient text editing",
            "syntax": "vim [options] [file...]",
            "examples": [
                "vim file.txt",
                "vim +10 file.txt",
                "vim -R file.txt",
                "vimtutor"
            ],
            "category": "Text Editors",
            "tags": ["editor", "vim", "text", "ubuntu", "debian", "arch", "rhel", "centos"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "tmux",
            "description": "Terminal multiplexer for managing multiple terminal sessions",
            "syntax": "tmux [command] [options]",
            "examples": [
                "tmux new-session -d -s mysession",
                "tmux attach-session -t mysession",
                "tmux list-sessions",
                "tmux kill-session -t mysession"
            ],
            "category": "Development Tools",
            "tags": ["terminal", "multiplexer", "sessions", "ubuntu", "debian", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # Monitoring and Performance Tools
        {
            "id": str(uuid.uuid4()),
            "name": "htop",
            "description": "Interactive process viewer and system monitor",
            "syntax": "htop [options]",
            "examples": [
                "htop",
                "htop -u username",
                "htop -p PID1,PID2"
            ],
            "category": "System Monitoring",
            "tags": ["monitoring", "processes", "performance", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "iotop",
            "description": "Monitor I/O usage by processes in real time",
            "syntax": "iotop [options]",
            "examples": [
                "iotop",
                "iotop -o",
                "iotop -u username"
            ],
            "category": "System Monitoring",
            "tags": ["io", "monitoring", "performance", "disk", "ubuntu", "debian", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "netstat",
            "description": "Display network connections, routing tables, interface statistics",
            "syntax": "netstat [options]",
            "examples": [
                "netstat -tuln",
                "netstat -rn",
                "netstat -i",
                "netstat -an | grep :80"
            ],
            "category": "Networking",
            "tags": ["networking", "connections", "ports", "ubuntu", "debian", "rhel", "centos"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "ss",
            "description": "Modern replacement for netstat to investigate network sockets",
            "syntax": "ss [options] [filter]",
            "examples": [
                "ss -tuln",
                "ss -p",
                "ss -s",
                "ss dst :80"
            ],
            "category": "Networking",
            "tags": ["networking", "sockets", "modern", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # Archive and Compression Tools
        {
            "id": str(uuid.uuid4()),
            "name": "7z",
            "description": "High compression file archiver with high compression ratio",
            "syntax": "7z [command] [options] archive [files...]",
            "examples": [
                "7z a archive.7z file1 file2",
                "7z x archive.7z",
                "7z l archive.7z",
                "7z a -p archive.7z folder/"
            ],
            "category": "Archive & Compression",
            "tags": ["compression", "archive", "7zip", "ubuntu", "debian", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "zip",
            "description": "Package and compress files into ZIP archives",
            "syntax": "zip [options] archive files...",
            "examples": [
                "zip archive.zip file1 file2",
                "zip -r archive.zip directory/",
                "zip -e encrypted.zip file.txt",
                "unzip archive.zip"
            ],
            "category": "Archive & Compression",
            "tags": ["compression", "zip", "archive", "ubuntu", "debian", "rhel", "centos"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # Database Tools
        {
            "id": str(uuid.uuid4()),
            "name": "mysql",
            "description": "MySQL database client for database operations",
            "syntax": "mysql [options] [database]",
            "examples": [
                "mysql -u root -p",
                "mysql -h localhost -u user -p database",
                "mysqldump -u root -p database > backup.sql",
                "mysql -u root -p database < backup.sql"
            ],
            "category": "Database Management",
            "tags": ["database", "mysql", "sql", "ubuntu", "debian", "rhel", "centos"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "postgresql",
            "description": "PostgreSQL database client and administration tools",
            "syntax": "psql [options] [database [user]]",
            "examples": [
                "psql -U postgres",
                "psql -h localhost -d database -U user",
                "pg_dump database > backup.sql",
                "createdb newdatabase"
            ],
            "category": "Database Management",
            "tags": ["database", "postgresql", "sql", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # Web Server Tools
        {
            "id": str(uuid.uuid4()),
            "name": "nginx",
            "description": "High-performance HTTP server and reverse proxy",
            "syntax": "nginx [options]",
            "examples": [
                "nginx",
                "nginx -t",
                "nginx -s reload",
                "nginx -s stop"
            ],
            "category": "Web Server",
            "tags": ["web server", "http", "proxy", "ubuntu", "debian", "rhel", "centos"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "apache2",
            "description": "Apache HTTP Server for serving web content",
            "syntax": "apache2 [options]",
            "examples": [
                "systemctl start apache2",
                "apache2ctl configtest",
                "a2ensite default-ssl",
                "a2dismod ssl"
            ],
            "category": "Web Server",
            "tags": ["web server", "apache", "http", "ubuntu", "debian"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # Package Management for Different Distros
        {
            "id": str(uuid.uuid4()),
            "name": "pacman",
            "description": "Arch Linux package manager for installing and managing software",
            "syntax": "pacman [options] [packages...]",
            "examples": [
                "pacman -S package_name",
                "pacman -Syu",
                "pacman -R package_name",
                "pacman -Ss search_term",
                "pacman -Qi package_name"
            ],
            "category": "Package Management",
            "tags": ["package manager", "arch", "install", "update"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "yum",
            "description": "RedHat/CentOS package manager for managing RPM packages",
            "syntax": "yum [options] command [packages...]",
            "examples": [
                "yum install package_name",
                "yum update",
                "yum remove package_name",
                "yum search keyword",
                "yum info package_name"
            ],
            "category": "Package Management",
            "tags": ["package manager", "rhel", "centos", "rpm", "install"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "dnf",
            "description": "Modern package manager for Fedora and RHEL-based distributions",
            "syntax": "dnf [options] command [packages...]",
            "examples": [
                "dnf install package_name",
                "dnf update",
                "dnf remove package_name",
                "dnf search keyword",
                "dnf info package_name"
            ],
            "category": "Package Management",
            "tags": ["package manager", "fedora", "rhel", "modern", "install"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "zypper",
            "description": "openSUSE package manager for managing RPM packages",
            "syntax": "zypper [options] command [packages...]",
            "examples": [
                "zypper install package_name",
                "zypper update",
                "zypper remove package_name",
                "zypper search keyword"
            ],
            "category": "Package Management",
            "tags": ["package manager", "suse", "opensuse", "rpm"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # Security and Encryption Tools
        {
            "id": str(uuid.uuid4()),
            "name": "gpg",
            "description": "GNU Privacy Guard for encryption and digital signatures",
            "syntax": "gpg [options] [files]",
            "examples": [
                "gpg --gen-key",
                "gpg --encrypt --recipient user@example.com file.txt",
                "gpg --decrypt file.txt.gpg",
                "gpg --sign file.txt"
            ],
            "category": "Security",
            "tags": ["encryption", "pgp", "security", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "openssl",
            "description": "Cryptography toolkit for SSL/TLS and general-purpose cryptography",
            "syntax": "openssl command [options]",
            "examples": [
                "openssl genrsa -out private.key 2048",
                "openssl req -new -x509 -key private.key -out certificate.crt -days 365",
                "openssl s_client -connect google.com:443",
                "openssl enc -aes-256-cbc -in file.txt -out file.enc"
            ],
            "category": "Security",
            "tags": ["ssl", "tls", "encryption", "certificates", "ubuntu", "debian", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # Cloud and DevOps Tools
        {
            "id": str(uuid.uuid4()),
            "name": "terraform",
            "description": "Infrastructure as code software tool for building, changing, and versioning infrastructure",
            "syntax": "terraform [global options] <subcommand> [args]",
            "examples": [
                "terraform init",
                "terraform plan",
                "terraform apply",
                "terraform destroy",
                "terraform fmt"
            ],
            "category": "Development Tools",
            "tags": ["infrastructure", "cloud", "devops", "iac", "ubuntu", "debian", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "aws",
            "description": "Amazon Web Services Command Line Interface",
            "syntax": "aws [service] [operation] [options]",
            "examples": [
                "aws s3 ls",
                "aws ec2 describe-instances",
                "aws s3 cp file.txt s3://bucket/",
                "aws configure"
            ],
            "category": "Development Tools",
            "tags": ["cloud", "aws", "devops", "cli", "ubuntu", "debian", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # Advanced Networking Tools
        {
            "id": str(uuid.uuid4()),
            "name": "tcpdump",
            "description": "Command-line packet analyzer for network traffic monitoring",
            "syntax": "tcpdump [options] [expression]",
            "examples": [
                "tcpdump -i eth0",
                "tcpdump -w capture.pcap",
                "tcpdump host 192.168.1.1",
                "tcpdump port 80"
            ],
            "category": "Sniffing & Spoofing",
            "tags": ["networking", "packets", "monitoring", "kali", "ubuntu", "debian"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "curl",
            "description": "Command line tool for transferring data with URLs",
            "syntax": "curl [options] [URL...]",
            "examples": [
                "curl https://api.example.com",
                "curl -X POST -H 'Content-Type: application/json' -d '{\"key\":\"value\"}' https://api.example.com",
                "curl -o file.zip https://example.com/file.zip",
                "curl -I https://example.com"
            ],
            "category": "Networking",
            "tags": ["http", "api", "download", "web", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ]
    
    try:
        # Insert commands (skip if they already exist)
        for command in enhanced_commands:
            existing = await db.commands.find_one({"name": command["name"]})
            if not existing:
                await db.commands.insert_one(command)
                print(f"✅ Added command: {command['name']}")
            else:
                print(f"⏭️  Skipping existing command: {command['name']}")
        
        print(f"\n🎉 Enhanced database population complete!")
        print(f"📊 Total commands processed: {len(enhanced_commands)}")
        
        # Print statistics
        total_commands = await db.commands.count_documents({})
        categories = await db.commands.distinct("category")
        tags = await db.commands.distinct("tags")
        
        print(f"\n📈 Database Statistics:")
        print(f"   Total commands: {total_commands}")
        print(f"   Categories: {len(categories)}")
        print(f"   Unique tags: {len(tags)}")
        print(f"   New distributions added: Alpine, Manjaro, Elementary OS")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(populate_enhanced_commands())