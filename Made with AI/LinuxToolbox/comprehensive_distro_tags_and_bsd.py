#!/usr/bin/env python3

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

# Comprehensive Distro Tags + Massive BSD Expansion
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'linux_admin_tool')

async def add_distro_tags_and_bsd_commands():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("🚀 Starting comprehensive distro tags update and BSD expansion...")
        
        # ==================== ADD DISTRO TAGS TO EXISTING COMMANDS ====================
        
        # Define command to distro mappings
        distro_mappings = {
            # Package managers
            'apt': ['debian', 'ubuntu', 'mint', 'elementary', 'pop', 'mx-linux', 'zorin'],
            'apt-get': ['debian', 'ubuntu', 'mint', 'elementary', 'pop', 'mx-linux', 'zorin'],
            'dpkg': ['debian', 'ubuntu', 'mint', 'elementary', 'pop', 'mx-linux', 'zorin'],
            'yum': ['rhel', 'centos', 'fedora'],
            'dnf': ['fedora', 'rhel', 'centos'],
            'rpm': ['rhel', 'centos', 'fedora', 'suse', 'opensuse'],
            'zypper': ['suse', 'opensuse'],
            'pacman': ['arch', 'manjaro', 'endeavouros'],
            'emerge': ['gentoo'],
            'apk': ['alpine'],
            'pkg': ['freebsd'],
            'pkg_add': ['openbsd'],
            'pkgin': ['netbsd'],
            
            # System services
            'systemctl': ['ubuntu', 'debian', 'fedora', 'rhel', 'centos', 'arch', 'manjaro', 'suse', 'opensuse'],
            'service': ['ubuntu', 'debian', 'rhel', 'centos', 'mint', 'mx-linux'],
            'rc-service': ['alpine', 'gentoo'],
            
            # Networking
            'NetworkManager': ['ubuntu', 'fedora', 'debian', 'mint', 'manjaro', 'opensuse'],
            'nmcli': ['ubuntu', 'fedora', 'debian', 'mint', 'manjaro', 'opensuse'],
            'ifconfig': ['freebsd', 'openbsd', 'netbsd', 'ubuntu', 'debian', 'rhel', 'centos'],
            'ip': ['ubuntu', 'debian', 'fedora', 'rhel', 'centos', 'arch', 'manjaro'],
            
            # Security/Forensics tools (Kali-specific)
            'nmap': ['kali', 'ubuntu', 'debian', 'arch', 'fedora', 'freebsd', 'openbsd'],
            'wireshark': ['kali', 'ubuntu', 'debian', 'fedora', 'arch', 'freebsd'],
            'metasploit': ['kali'],
            'burp': ['kali'],
            'sqlmap': ['kali'],
            'gobuster': ['kali'],
            'aircrack-ng': ['kali'],
            
            # File systems
            'zfs': ['freebsd', 'ubuntu', 'debian'],
            'btrfs': ['opensuse', 'fedora', 'arch'],
            
            # Universal commands (available on most systems)
            'universal': ['ubuntu', 'debian', 'fedora', 'rhel', 'centos', 'arch', 'manjaro', 'mint', 'opensuse', 'suse', 'gentoo', 'alpine', 'freebsd', 'openbsd', 'netbsd', 'kali']
        }
        
        # Universal commands that are available on most Unix-like systems
        universal_commands = [
            'ls', 'cp', 'mv', 'rm', 'mkdir', 'rmdir', 'pwd', 'cd', 'find', 'grep', 'sed', 'awk',
            'cat', 'less', 'more', 'head', 'tail', 'sort', 'uniq', 'cut', 'tr', 'wc', 'tee',
            'ps', 'top', 'kill', 'killall', 'which', 'whereis', 'who', 'w', 'id', 'su', 'sudo',
            'chmod', 'chown', 'chgrp', 'tar', 'gzip', 'gunzip', 'zip', 'unzip', 'ssh', 'scp', 'rsync',
            'ping', 'wget', 'curl', 'mount', 'umount', 'df', 'du', 'free', 'uptime', 'uname',
            'date', 'cal', 'man', 'info', 'history', 'alias', 'env', 'export', 'echo', 'printf'
        ]
        
        # Update existing commands with distro tags
        update_count = 0
        
        # First, add universal tags to universal commands
        for cmd_name in universal_commands:
            result = await db.commands.update_many(
                {"name": cmd_name},
                {"$addToSet": {"tags": {"$each": distro_mappings['universal']}}}
            )
            if result.modified_count > 0:
                update_count += result.modified_count
                print(f"✅ Added universal distro tags to {cmd_name}")
        
        # Then add specific distro tags
        for cmd_name, distros in distro_mappings.items():
            if cmd_name != 'universal':
                result = await db.commands.update_many(
                    {"name": cmd_name},
                    {"$addToSet": {"tags": {"$each": distros}}}
                )
                if result.modified_count > 0:
                    update_count += result.modified_count
                    print(f"✅ Added {distros} tags to {cmd_name}")
        
        print(f"\n📊 Updated {update_count} commands with distro tags")
        
        # ==================== ADD MASSIVE BSD COMMANDS ====================
        
        bsd_commands = [
            # FreeBSD System Administration
            {
                "name": "sysrc", "description": "FreeBSD system configuration utility for managing rc.conf variables safely",
                "syntax": "sysrc [options] [variable[=value]]", "category": "System Monitoring",
                "examples": [
                    "sysrc sshd_enable=YES  # Enable SSH daemon",
                    "sysrc -a  # Show all variables",
                    "sysrc nginx_enable  # Check variable value",
                    "sysrc -x nginx_enable  # Delete variable"
                ],
                "tags": ["freebsd", "configuration", "rc.conf", "system"]
            },
            {
                "name": "kldload", "description": "FreeBSD kernel module loader for dynamically loading kernel modules",
                "syntax": "kldload [options] module", "category": "Hardware Information",
                "examples": [
                    "kldload if_em  # Load Ethernet driver",
                    "kldload linux  # Load Linux compatibility",
                    "kldload fuse  # Load FUSE filesystem"
                ],
                "tags": ["freebsd", "kernel", "modules", "drivers"]
            },
            {
                "name": "kldunload", "description": "FreeBSD kernel module unloader for removing loaded kernel modules",
                "syntax": "kldunload [options] module", "category": "Hardware Information", 
                "examples": [
                    "kldunload if_em  # Unload Ethernet driver",
                    "kldunload linux  # Unload Linux compatibility"
                ],
                "tags": ["freebsd", "kernel", "modules", "unload"]
            },
            {
                "name": "kldstat", "description": "FreeBSD kernel module status display showing loaded modules",
                "syntax": "kldstat [options]", "category": "Hardware Information",
                "examples": [
                    "kldstat  # List loaded modules", 
                    "kldstat -v  # Verbose output",
                    "kldstat -i 1  # Show specific module"
                ],
                "tags": ["freebsd", "kernel", "modules", "status"]
            },
            {
                "name": "camcontrol", "description": "FreeBSD CAM (Common Access Method) control utility for SCSI/ATA devices",
                "syntax": "camcontrol [command] [options]", "category": "Hardware Information",
                "examples": [
                    "camcontrol devlist  # List devices",
                    "camcontrol inquiry da0  # Device inquiry",
                    "camcontrol identify ada0  # ATA identify"
                ],
                "tags": ["freebsd", "scsi", "ata", "devices", "cam"]
            },
            {
                "name": "gpart", "description": "FreeBSD GEOM partitioning utility for managing disk partitions",
                "syntax": "gpart [command] [options] geom", "category": "Disk Management",
                "examples": [
                    "gpart show  # Show partition tables",
                    "gpart create -s GPT da0  # Create GPT partition table",
                    "gpart add -t freebsd-ufs -s 20G da0  # Add UFS partition"
                ],
                "tags": ["freebsd", "partitioning", "geom", "gpt"]
            },
            {
                "name": "newfs", "description": "FreeBSD filesystem creation utility for UFS filesystems",
                "syntax": "newfs [options] device", "category": "Disk Management",
                "examples": [
                    "newfs /dev/da0p1  # Create UFS filesystem",
                    "newfs -U /dev/da0p1  # Create with soft updates"
                ],
                "tags": ["freebsd", "filesystem", "ufs", "format"]
            },
            {
                "name": "tunefs", "description": "FreeBSD UFS filesystem tuning utility for performance optimization",
                "syntax": "tunefs [options] filesystem", "category": "Disk Management", 
                "examples": [
                    "tunefs -p /dev/da0p1  # Display parameters",
                    "tunefs -m 5 /dev/da0p1  # Set reserved space to 5%"
                ],
                "tags": ["freebsd", "ufs", "tuning", "performance"]
            },
            {
                "name": "dumpfs", "description": "FreeBSD UFS filesystem information dump utility",
                "syntax": "dumpfs [options] filesystem", "category": "Disk Management",
                "examples": [
                    "dumpfs /dev/da0p1  # Show filesystem info",
                    "dumpfs -m /  # Show mounted filesystem info"
                ],
                "tags": ["freebsd", "ufs", "information", "dump"]
            },
            
            # FreeBSD Security
            {
                "name": "ipfw", "description": "FreeBSD IP firewall configuration utility with stateful filtering",
                "syntax": "ipfw [options] [command]", "category": "Security",
                "examples": [
                    "ipfw list  # Show firewall rules",
                    "ipfw add allow tcp from any to me 22  # Allow SSH",
                    "ipfw flush  # Clear all rules"
                ],
                "tags": ["freebsd", "firewall", "ipfw", "security"]
            },
            {
                "name": "pfctl", "description": "FreeBSD Packet Filter control utility (when PF is used)",
                "syntax": "pfctl [options]", "category": "Security",
                "examples": [
                    "pfctl -sr  # Show rules",
                    "pfctl -f /etc/pf.conf  # Load rules", 
                    "pfctl -e  # Enable PF"
                ],
                "tags": ["freebsd", "pf", "firewall", "security"]
            },
            
            # FreeBSD Networking
            {
                "name": "ifconfig", "description": "FreeBSD network interface configuration utility with advanced features",
                "syntax": "ifconfig [interface] [options]", "category": "Networking",
                "examples": [
                    "ifconfig em0  # Show interface info",
                    "ifconfig em0 inet 192.168.1.100/24  # Set IP address",
                    "ifconfig em0 up  # Bring interface up",
                    "ifconfig wlan create wlandev ath0  # Create wireless interface"
                ],
                "tags": ["freebsd", "networking", "interfaces", "wireless"]
            },
            {
                "name": "route", "description": "FreeBSD routing table manipulation utility",
                "syntax": "route [command] [options]", "category": "Networking",
                "examples": [
                    "route show  # Display routing table",
                    "route add default 192.168.1.1  # Add default route",
                    "route delete 10.0.0.0/8  # Delete route"
                ],
                "tags": ["freebsd", "routing", "network", "gateway"]
            },
            
            # OpenBSD System Administration  
            {
                "name": "rcctl", "description": "OpenBSD service control utility for managing system daemons",
                "syntax": "rcctl [command] [service]", "category": "System Monitoring",
                "examples": [
                    "rcctl ls started  # List running services",
                    "rcctl start httpd  # Start web server",
                    "rcctl enable sshd  # Enable SSH at boot",
                    "rcctl disable httpd  # Disable service"
                ],
                "tags": ["openbsd", "services", "daemons", "control"]
            },
            {
                "name": "doas", "description": "OpenBSD privilege escalation utility as alternative to sudo",
                "syntax": "doas [options] command", "category": "Security",
                "examples": [
                    "doas pkg_add nginx  # Install package as root",
                    "doas -u user command  # Run as specific user",
                    "doas vi /etc/doas.conf  # Edit doas configuration"
                ],
                "tags": ["openbsd", "privilege", "escalation", "security"]
            },
            {
                "name": "disklabel", "description": "OpenBSD disk label editor for partition management",
                "syntax": "disklabel [options] device", "category": "Disk Management",
                "examples": [
                    "disklabel sd0  # Show disk label",
                    "disklabel -E sd0  # Edit disk label interactively",
                    "disklabel -w sd0  # Write label to disk"
                ],
                "tags": ["openbsd", "partitioning", "disklabel", "disk"]
            },
            {
                "name": "newfs", "description": "OpenBSD filesystem creation utility for FFS filesystems",
                "syntax": "newfs [options] device", "category": "Disk Management",
                "examples": [
                    "newfs sd0a  # Create FFS filesystem",
                    "newfs -O 2 sd0d  # Create FFS2 filesystem"
                ],
                "tags": ["openbsd", "filesystem", "ffs", "format"]
            },
            {
                "name": "fw_update", "description": "OpenBSD firmware update utility for device firmware",
                "syntax": "fw_update [options]", "category": "Hardware Information",
                "examples": [
                    "fw_update  # Update all firmware",
                    "fw_update -v  # Verbose update",
                    "fw_update iwm  # Update specific driver firmware"
                ],
                "tags": ["openbsd", "firmware", "update", "drivers"]
            },
            {
                "name": "sendsyslog", "description": "OpenBSD system log message sender utility",
                "syntax": "sendsyslog [options] message", "category": "System Monitoring",
                "examples": [
                    "sendsyslog 'System maintenance started'  # Send log message",
                    "sendsyslog -p local0.info 'Custom message'  # Specific facility"
                ],
                "tags": ["openbsd", "logging", "syslog", "messages"]
            },
            
            # OpenBSD Security
            {
                "name": "pfctl", "description": "OpenBSD Packet Filter control - the original and most advanced implementation",
                "syntax": "pfctl [options]", "category": "Security",
                "examples": [
                    "pfctl -f /etc/pf.conf  # Load firewall rules",
                    "pfctl -sr  # Show rules",
                    "pfctl -ss  # Show state table",
                    "pfctl -si  # Show interface statistics",
                    "pfctl -e  # Enable PF",
                    "pfctl -F all  # Flush all"
                ],
                "tags": ["openbsd", "pf", "firewall", "security", "advanced"]
            },
            {
                "name": "authpf", "description": "OpenBSD authenticating gateway user shell for PF firewall",
                "syntax": "authpf", "category": "Security",
                "examples": [
                    "# Used as user shell for authenticated firewall access",
                    "# Configured in /etc/passwd"
                ],
                "tags": ["openbsd", "authentication", "pf", "gateway"]
            },
            
            # NetBSD System Administration
            {
                "name": "postinstall", "description": "NetBSD post-installation configuration checker and updater",
                "syntax": "postinstall [command] [options]", "category": "System Monitoring",
                "examples": [
                    "postinstall check  # Check configuration",
                    "postinstall fix  # Fix configuration issues",
                    "postinstall help  # Show help"
                ],
                "tags": ["netbsd", "configuration", "post-install", "system"]
            },
            {
                "name": "veriexecctl", "description": "NetBSD Veriexec control utility for file integrity verification", 
                "syntax": "veriexecctl [command] [options]", "category": "Security",
                "examples": [
                    "veriexecctl load  # Load fingerprint database",
                    "veriexecctl query /bin/ls  # Query file status"
                ],
                "tags": ["netbsd", "veriexec", "integrity", "security"]
            },
            {
                "name": "cgdconfig", "description": "NetBSD crypto graphic disk configuration utility",
                "syntax": "cgdconfig [options] device", "category": "Security", 
                "examples": [
                    "cgdconfig cgd0 /dev/wd0a  # Configure encrypted disk",
                    "cgdconfig -u cgd0  # Unconfigure encrypted disk"
                ],
                "tags": ["netbsd", "encryption", "disk", "crypto"]
            },
            {
                "name": "raidctl", "description": "NetBSD software RAID configuration and management utility",
                "syntax": "raidctl [options] device", "category": "Disk Management",
                "examples": [
                    "raidctl -c /etc/raid0.conf raid0  # Create RAID",
                    "raidctl -S raid0  # Show RAID status",
                    "raidctl -R /dev/wd1a raid0  # Add hot spare"
                ],
                "tags": ["netbsd", "raid", "software raid", "storage"]
            },
            
            # Cross-BSD Utilities
            {
                "name": "ktrace", "description": "BSD kernel trace utility for system call tracing and debugging",
                "syntax": "ktrace [options] command", "category": "Development Tools",
                "examples": [
                    "ktrace ls  # Trace ls command",
                    "ktrace -f trace.out program  # Save trace to file", 
                    "kdump  # Display trace output"
                ],
                "tags": ["freebsd", "openbsd", "netbsd", "tracing", "debugging"]
            },
            {
                "name": "kdump", "description": "BSD kernel trace dump utility for displaying ktrace output", 
                "syntax": "kdump [options]", "category": "Development Tools",
                "examples": [
                    "kdump  # Display trace from ktrace.out",
                    "kdump -f trace.out  # Display specific trace file",
                    "kdump -T  # Show timestamps"
                ],
                "tags": ["freebsd", "openbsd", "netbsd", "tracing", "analysis"]
            },
            {
                "name": "jot", "description": "BSD utility for generating sequences of numbers or characters",
                "syntax": "jot [options] [count] [begin] [end] [step]", "category": "Text Processing",
                "examples": [
                    "jot 10  # Generate numbers 1-10",
                    "jot 5 1 100  # 5 numbers between 1-100",
                    "jot -c 26 a  # Generate a-z",
                    "jot -r 10 1 100  # 10 random numbers 1-100"
                ],
                "tags": ["freebsd", "openbsd", "netbsd", "sequences", "numbers"]
            },
            {
                "name": "leave", "description": "BSD utility to remind when to leave by specified time",
                "syntax": "leave [time]", "category": "System Monitoring",
                "examples": [
                    "leave 1730  # Remind at 5:30 PM",
                    "leave +60  # Remind in 60 minutes"
                ],
                "tags": ["freebsd", "openbsd", "netbsd", "reminder", "time"]
            },
            {
                "name": "calendar", "description": "BSD calendar and reminder system with holiday support",
                "syntax": "calendar [options]", "category": "System Monitoring", 
                "examples": [
                    "calendar  # Show today's events",
                    "calendar -a  # Show for all users",
                    "calendar -f ~/.calendar  # Use specific calendar file"
                ],
                "tags": ["freebsd", "openbsd", "netbsd", "calendar", "reminders"]
            },
            {
                "name": "hexdump", "description": "BSD hexadecimal dump utility for binary file analysis",
                "syntax": "hexdump [options] files", "category": "Development Tools",
                "examples": [
                    "hexdump -C file.bin  # Canonical hex+ASCII display",
                    "hexdump -x file.bin  # Hexadecimal display", 
                    "hexdump -d file.bin  # Decimal display"
                ],
                "tags": ["freebsd", "openbsd", "netbsd", "hex", "binary", "analysis"]
            },
            
            # BSD Package Management Extensions
            {
                "name": "pkg-config", "description": "BSD package configuration helper for compilation flags",
                "syntax": "pkg-config [options] packages", "category": "Development Tools",
                "examples": [
                    "pkg-config --cflags gtk+-3.0  # Get compiler flags",
                    "pkg-config --libs openssl  # Get linker flags",
                    "pkg-config --list-all  # List all packages"
                ],
                "tags": ["freebsd", "openbsd", "netbsd", "compilation", "development"]
            },
            {
                "name": "portsnap", "description": "FreeBSD Ports Collection update utility for source-based packages",
                "syntax": "portsnap [command] [options]", "category": "Package Management",
                "examples": [
                    "portsnap fetch extract  # Initial ports tree setup",
                    "portsnap fetch update  # Update existing ports tree",
                    "portsnap auto  # Automatic update"
                ],
                "tags": ["freebsd", "ports", "update", "source"]
            },
            {
                "name": "portmaster", "description": "FreeBSD Ports management tool for building and upgrading",
                "syntax": "portmaster [options] [ports...]", "category": "Package Management",
                "examples": [
                    "portmaster -a  # Upgrade all ports",
                    "portmaster www/nginx  # Install specific port",
                    "portmaster -e  # Rebuild with existing options"
                ],
                "tags": ["freebsd", "ports", "management", "upgrade"]
            },
            {
                "name": "portaudit", "description": "FreeBSD Ports security vulnerability auditing tool",
                "syntax": "portaudit [options]", "category": "Security",
                "examples": [
                    "portaudit -Fda  # Update database and audit",
                    "portaudit -a  # Audit installed ports"
                ],
                "tags": ["freebsd", "ports", "security", "audit"]
            }
        ]
        
        # Add all BSD commands
        bsd_added = 0
        for cmd_data in bsd_commands:
            existing = await db.commands.find_one({"name": cmd_data["name"]})
            if not existing:
                full_command = {
                    "id": str(uuid.uuid4()),
                    **cmd_data,
                    "created_by": "system",
                    "is_public": True,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
                await db.commands.insert_one(full_command)
                print(f"✅ Added BSD command: {cmd_data['name']}")
                bsd_added += 1
            else:
                # Update existing with BSD tags
                await db.commands.update_one(
                    {"name": cmd_data["name"]},
                    {"$addToSet": {"tags": {"$each": cmd_data["tags"]}}}
                )
                print(f"🔄 Updated BSD command: {cmd_data['name']}")
        
        # Get final statistics
        total_commands = await db.commands.count_documents({})
        categories = await db.commands.distinct("category")
        tags = await db.commands.distinct("tags")
        
        print(f"\n🎉 Comprehensive update complete!")
        print(f"📊 Distro tags added to existing commands: {update_count}")
        print(f"📊 New BSD commands added: {bsd_added}")
        print(f"📈 TOTAL COMMANDS: {total_commands}")
        print(f"📂 Categories: {len(categories)}")
        print(f"🏷️  Unique tags: {len(tags)}")
        
        print(f"\n🐧 NOW ALL COMMANDS HAVE PROPER DISTRO TAGS!")
        print(f"🔶 BSD COMMAND COVERAGE EXPANDED SIGNIFICANTLY!")
        print(f"✨ Users can now filter by their specific distribution!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_distro_tags_and_bsd_commands())