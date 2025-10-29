#!/usr/bin/env python3

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

# Complete Distributions Expansion - BSD + All Major Linux Distros + Commands
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'linux_admin_tool')

async def create_complete_distros_expansion():
    
    # BSD and Linux Distribution-specific commands
    distro_commands = [
        # ==================== BSD DISTRIBUTIONS ====================
        
        # FreeBSD Commands
        {
            "name": "pkg", "description": "FreeBSD package manager for installing, upgrading, and managing binary packages with dependency resolution",
            "syntax": "pkg [command] [options] [packages...]", "category": "Package Management",
            "examples": [
                "pkg install nginx  # Install package",
                "pkg update  # Update package database", 
                "pkg upgrade  # Upgrade all packages",
                "pkg search keyword  # Search for packages",
                "pkg info package  # Show package info",
                "pkg delete package  # Remove package",
                "pkg autoremove  # Remove orphaned packages",
                "pkg clean  # Clean package cache"
            ],
            "tags": ["package manager", "freebsd", "binary", "packages"]
        },
        {
            "name": "ports", "description": "FreeBSD Ports Collection for building software from source code with customizable options",
            "syntax": "cd /usr/ports/category/port && make [target]", "category": "Package Management",
            "examples": [
                "cd /usr/ports/www/nginx && make install clean  # Install from ports",
                "make config  # Configure build options",
                "make deinstall  # Remove installed port",
                "make search name=nginx  # Search ports",
                "portsnap fetch update  # Update ports tree",
                "portmaster -a  # Upgrade all ports",
                "portaudit -Fda  # Security audit"
            ],
            "tags": ["ports", "freebsd", "source", "compilation"]
        },
        {
            "name": "freebsd-update", "description": "FreeBSD binary update utility for system security updates and version upgrades",
            "syntax": "freebsd-update [command] [options]", "category": "System Monitoring",
            "examples": [
                "freebsd-update fetch  # Download updates",
                "freebsd-update install  # Install updates",
                "freebsd-update upgrade -r 13.1-RELEASE  # Upgrade release",
                "freebsd-update cron  # Run from cron"
            ],
            "tags": ["update", "security", "freebsd", "system"]
        },
        {
            "name": "jail", "description": "FreeBSD jail management for creating secure isolated environments and containers",
            "syntax": "jail [options] [command]", "category": "Security",
            "examples": [
                "jail -c name=myjail path=/jails/myjail  # Create jail",
                "jls  # List running jails",
                "jexec myjail /bin/sh  # Execute command in jail",
                "jail -r myjail  # Remove jail"
            ],
            "tags": ["jail", "containers", "isolation", "freebsd"]
        },
        {
            "name": "zfs", "description": "ZFS filesystem management with snapshots, compression, and data integrity features",
            "syntax": "zfs [command] [options] [dataset]", "category": "Disk Management", 
            "examples": [
                "zfs list  # List ZFS datasets",
                "zfs create tank/mydataset  # Create dataset",
                "zfs snapshot tank/mydataset@snap1  # Create snapshot",
                "zfs destroy tank/mydataset@snap1  # Destroy snapshot",
                "zfs clone tank/mydataset@snap1 tank/clone  # Clone snapshot",
                "zfs send tank/mydataset@snap1 | zfs receive backup/mydataset  # Send/receive"
            ],
            "tags": ["zfs", "filesystem", "snapshots", "freebsd"]
        },
        {
            "name": "zpool", "description": "ZFS pool management for creating and managing storage pools with redundancy",
            "syntax": "zpool [command] [options] [pool]", "category": "Disk Management",
            "examples": [
                "zpool create tank /dev/da0  # Create pool",
                "zpool status  # Show pool status",
                "zpool scrub tank  # Scrub pool for errors",
                "zpool add tank /dev/da1  # Add device to pool",
                "zpool destroy tank  # Destroy pool"
            ],
            "tags": ["zpool", "storage", "redundancy", "freebsd"]
        },
        
        # OpenBSD Commands  
        {
            "name": "pkg_add", "description": "OpenBSD package installation utility for adding binary packages from repositories",
            "syntax": "pkg_add [options] [packages...]", "category": "Package Management",
            "examples": [
                "pkg_add nginx  # Install package",
                "pkg_add -u  # Update all packages", 
                "pkg_add -v package  # Verbose installation",
                "pkg_add -n package  # Test installation"
            ],
            "tags": ["package manager", "openbsd", "install"]
        },
        {
            "name": "pkg_delete", "description": "OpenBSD package removal utility for cleanly uninstalling packages",
            "syntax": "pkg_delete [options] [packages...]", "category": "Package Management",
            "examples": [
                "pkg_delete nginx  # Remove package",
                "pkg_delete -a  # Remove all packages",
                "pkg_delete -v package  # Verbose removal"
            ],
            "tags": ["package manager", "openbsd", "remove"]
        },
        {
            "name": "pkg_info", "description": "OpenBSD package information utility for querying installed packages",
            "syntax": "pkg_info [options] [packages...]", "category": "Package Management", 
            "examples": [
                "pkg_info  # List all packages",
                "pkg_info nginx  # Show package info",
                "pkg_info -L package  # List package files",
                "pkg_info -q  # Quiet mode"
            ],
            "tags": ["package manager", "openbsd", "information"]
        },
        {
            "name": "syspatch", "description": "OpenBSD system patch utility for applying security updates automatically",
            "syntax": "syspatch [options]", "category": "System Monitoring",
            "examples": [
                "syspatch  # Apply available patches",
                "syspatch -c  # Check for patches",
                "syspatch -l  # List installed patches",
                "syspatch -R  # Rollback patches"
            ],
            "tags": ["patches", "security", "openbsd", "updates"]
        },
        {
            "name": "pf", "description": "OpenBSD Packet Filter firewall for network security and traffic control",
            "syntax": "pfctl [options]", "category": "Security",
            "examples": [
                "pfctl -f /etc/pf.conf  # Load firewall rules",
                "pfctl -sr  # Show current rules", 
                "pfctl -ss  # Show state table",
                "pfctl -e  # Enable firewall"
            ],
            "tags": ["firewall", "pf", "security", "openbsd"]
        },
        
        # NetBSD Commands
        {
            "name": "pkgin", "description": "NetBSD binary package manager for easy package installation and management", 
            "syntax": "pkgin [command] [options]", "category": "Package Management",
            "examples": [
                "pkgin update  # Update package database",
                "pkgin install nginx  # Install package",
                "pkgin remove package  # Remove package", 
                "pkgin search keyword  # Search packages"
            ],
            "tags": ["package manager", "netbsd", "binary"]
        },
        {
            "name": "pkgsrc", "description": "NetBSD packages collection for building software from source across platforms",
            "syntax": "cd /usr/pkgsrc/category/package && make install", "category": "Package Management",
            "examples": [
                "cd /usr/pkgsrc/www/nginx && make install  # Build and install",
                "make update  # Update package",
                "make deinstall  # Remove package",
                "make show-depends  # Show dependencies"
            ],
            "tags": ["pkgsrc", "netbsd", "source", "portable"]
        },
        
        # ==================== MAJOR LINUX DISTRIBUTIONS ====================
        
        # Linux Mint Commands
        {
            "name": "mintupdate", "description": "Linux Mint update manager for system updates with user-friendly interface",
            "syntax": "mintupdate [options]", "category": "Package Management",
            "examples": [
                "mintupdate  # Launch update manager GUI",
                "mintupdate-cli list  # List available updates",
                "mintupdate-cli upgrade  # Apply updates"
            ],
            "tags": ["updates", "mint", "gui", "user-friendly"]
        },
        {
            "name": "mintwelcome", "description": "Linux Mint welcome screen for first-time setup and system configuration",
            "syntax": "mintwelcome", "category": "System Monitoring",
            "examples": [
                "mintwelcome  # Launch welcome application"
            ],
            "tags": ["welcome", "mint", "setup", "configuration"]
        },
        {
            "name": "mintinstall", "description": "Linux Mint software manager for easy application installation",
            "syntax": "mintinstall [package]", "category": "Package Management",
            "examples": [
                "mintinstall  # Launch software manager",
                "mintinstall firefox  # Install specific package"
            ],
            "tags": ["software", "mint", "gui", "installer"]
        },
        
        # MX Linux Commands  
        {
            "name": "mx-tools", "description": "MX Linux system tools collection for system administration and configuration",
            "syntax": "mx-tools", "category": "System Monitoring",
            "examples": [
                "mx-tools  # Launch MX Tools interface",
                "mx-snapshot  # Create live system snapshot",
                "mx-boot-repair  # Repair boot issues"
            ],
            "tags": ["mx-linux", "tools", "administration", "gui"]
        },
        {
            "name": "mx-snapshot", "description": "MX Linux live system snapshot creator for backup and distribution",
            "syntax": "mx-snapshot [options]", "category": "Archive & Compression",
            "examples": [
                "mx-snapshot  # Create system snapshot",
                "mx-snapshot --compression=xz  # Use XZ compression"
            ],
            "tags": ["snapshot", "mx-linux", "backup", "live"]
        },
        
        # EndeavourOS Commands
        {
            "name": "eos-welcome", "description": "EndeavourOS welcome application for post-install setup and configuration",
            "syntax": "eos-welcome", "category": "System Monitoring", 
            "examples": [
                "eos-welcome  # Launch welcome application"
            ],
            "tags": ["welcome", "endeavouros", "arch", "setup"]
        },
        {
            "name": "eos-update-notifier", "description": "EndeavourOS update notification system for Arch updates",
            "syntax": "eos-update-notifier [options]", "category": "System Monitoring",
            "examples": [
                "eos-update-notifier  # Check for updates",
                "eos-update-notifier --enable  # Enable notifications"
            ],
            "tags": ["updates", "endeavouros", "arch", "notifications"]
        },
        
        # Elementary OS Commands
        {
            "name": "io.elementary.appcenter", "description": "Elementary OS AppCenter for application installation and management",
            "syntax": "io.elementary.appcenter", "category": "Package Management",
            "examples": [
                "io.elementary.appcenter  # Launch AppCenter"
            ],
            "tags": ["appcenter", "elementary", "applications", "gui"]
        },
        {
            "name": "switchboard", "description": "Elementary OS system settings application for configuration management",
            "syntax": "switchboard", "category": "System Monitoring",
            "examples": [
                "switchboard  # Launch system settings"
            ],
            "tags": ["settings", "elementary", "configuration", "gui"]
        },
        
        # Manjaro Commands
        {
            "name": "pamac", "description": "Manjaro package manager with GUI and AUR support for easy software management",
            "syntax": "pamac [command] [options]", "category": "Package Management",
            "examples": [
                "pamac install package  # Install package",
                "pamac update  # Update system",
                "pamac search keyword  # Search packages",
                "pamac build aur-package  # Build AUR package"
            ],
            "tags": ["pamac", "manjaro", "aur", "gui"]
        },
        {
            "name": "manjaro-settings-manager", "description": "Manjaro system configuration tool for hardware and kernel management",
            "syntax": "manjaro-settings-manager", "category": "System Monitoring",
            "examples": [
                "manjaro-settings-manager  # Launch settings manager"
            ],
            "tags": ["settings", "manjaro", "hardware", "kernel"]
        },
        
        # openSUSE Commands
        {
            "name": "yast", "description": "openSUSE system configuration and administration tool with comprehensive modules",
            "syntax": "yast [module]", "category": "System Monitoring",
            "examples": [
                "yast  # Launch YaST control center",
                "yast sw_single  # Software management",
                "yast users  # User management",
                "yast firewall  # Firewall configuration"
            ],
            "tags": ["yast", "suse", "opensuse", "configuration"]
        },
        {
            "name": "zypper", "description": "openSUSE command-line package manager with dependency resolution and repository management",
            "syntax": "zypper [command] [options]", "category": "Package Management",
            "examples": [
                "zypper install package  # Install package",
                "zypper update  # Update packages",
                "zypper search keyword  # Search packages",
                "zypper addrepo URL name  # Add repository",
                "zypper dup  # Distribution upgrade"
            ],
            "tags": ["zypper", "suse", "opensuse", "rpm"]
        },
        {
            "name": "snapper", "description": "openSUSE filesystem snapshot management for Btrfs rollback and recovery",
            "syntax": "snapper [command] [options]", "category": "Archive & Compression",
            "examples": [
                "snapper list  # List snapshots",
                "snapper create -d 'Before update'  # Create snapshot",
                "snapper delete NUMBER  # Delete snapshot",
                "snapper rollback  # Rollback to previous snapshot"
            ],
            "tags": ["snapper", "snapshots", "btrfs", "opensuse"]
        },
        
        # Pop!_OS Commands
        {
            "name": "pop-shop", "description": "Pop!_OS application store based on GNOME Software with Flatpak integration",
            "syntax": "pop-shop", "category": "Package Management",
            "examples": [
                "pop-shop  # Launch Pop Shop"
            ],
            "tags": ["pop-shop", "pop-os", "flatpak", "gui"]
        },
        {
            "name": "system76-power", "description": "System76 power management profiles for gaming, battery, and performance optimization",
            "syntax": "system76-power [profile]", "category": "Hardware Information",
            "examples": [
                "system76-power profile battery  # Battery saving mode",
                "system76-power profile balanced  # Balanced mode", 
                "system76-power profile performance  # Performance mode"
            ],
            "tags": ["power", "system76", "pop-os", "profiles"]
        },
        
        # Zorin OS Commands
        {
            "name": "zorin-appearance", "description": "Zorin OS appearance customization tool for desktop layouts and themes",
            "syntax": "zorin-appearance", "category": "System Monitoring",
            "examples": [
                "zorin-appearance  # Launch appearance settings"
            ],
            "tags": ["appearance", "zorin", "themes", "desktop"]
        },
        
        # Additional Distribution-Specific Tools
        {
            "name": "timeshift", "description": "System restore utility for Linux with automatic snapshots and rollback capability",
            "syntax": "timeshift [options]", "category": "Archive & Compression",
            "examples": [
                "timeshift --list  # List snapshots",
                "timeshift --create  # Create snapshot",
                "timeshift --restore  # Restore from snapshot",
                "timeshift --delete-all  # Delete all snapshots"
            ],
            "tags": ["timeshift", "restore", "snapshots", "mint", "manjaro"]
        },
        {
            "name": "bleachbit", "description": "System cleaner for freeing disk space and maintaining privacy across distributions",
            "syntax": "bleachbit [options]", "category": "System Monitoring",
            "examples": [
                "bleachbit  # Launch GUI cleaner",
                "bleachbit --list  # List cleaners",
                "bleachbit --clean system.*  # Clean system files"
            ],
            "tags": ["cleaner", "privacy", "disk space", "maintenance"]
        },
        {
            "name": "stacer", "description": "Linux system optimizer and monitoring tool with GUI interface",
            "syntax": "stacer", "category": "System Monitoring", 
            "examples": [
                "stacer  # Launch system optimizer"
            ],
            "tags": ["optimizer", "monitoring", "gui", "performance"]
        },
        
        # Container and Virtualization Tools
        {
            "name": "lxc", "description": "Linux Containers userspace tools for system container management",
            "syntax": "lxc [command] [options]", "category": "Development Tools",
            "examples": [
                "lxc launch ubuntu:20.04 mycontainer  # Launch container",
                "lxc list  # List containers",
                "lxc exec mycontainer bash  # Execute shell in container",
                "lxc stop mycontainer  # Stop container"
            ],
            "tags": ["containers", "lxc", "virtualization"]
        },
        {
            "name": "lxd", "description": "Next generation system container manager with REST API and clustering",
            "syntax": "lxd [command] [options]", "category": "Development Tools",
            "examples": [
                "lxd init  # Initialize LXD",
                "lxc remote add myremote https://remote:8443  # Add remote"
            ],
            "tags": ["containers", "lxd", "clustering", "api"]
        },
        
        # Gaming and Multimedia
        {
            "name": "steam", "description": "Steam gaming platform client for Linux with Proton Windows game compatibility",
            "syntax": "steam [options]", "category": "Development Tools",
            "examples": [
                "steam  # Launch Steam client",
                "steam -console  # Launch with console",
                "steam steam://install/appid  # Install specific game"
            ],
            "tags": ["gaming", "steam", "proton", "multimedia"]
        },
        {
            "name": "lutris", "description": "Gaming client for Linux supporting multiple platforms and game launchers",
            "syntax": "lutris [options]", "category": "Development Tools", 
            "examples": [
                "lutris  # Launch Lutris",
                "lutris --list-games  # List installed games",
                "lutris lutris:game-slug  # Launch specific game"
            ],
            "tags": ["gaming", "lutris", "wine", "emulation"]
        },
        
        # Development Environment
        {
            "name": "code", "description": "Visual Studio Code editor for development with extensions and integrated terminal",
            "syntax": "code [options] [files...]", "category": "Development Tools",
            "examples": [
                "code .  # Open current directory",
                "code file.py  # Open specific file",
                "code --install-extension ms-python.python  # Install extension"
            ],
            "tags": ["editor", "vscode", "development", "ide"]
        },
        {
            "name": "codium", "description": "VSCodium - fully open source version of Visual Studio Code",
            "syntax": "codium [options] [files...]", "category": "Development Tools",
            "examples": [
                "codium .  # Open current directory",
                "codium --list-extensions  # List installed extensions"
            ],
            "tags": ["editor", "vscodium", "open source", "development"]
        }
    ]
    
    # Convert to full command format
    full_commands = []
    for cmd_data in distro_commands:
        full_commands.append({
            "id": str(uuid.uuid4()),
            **cmd_data,
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        })
    
    return full_commands

async def add_complete_distros_commands():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        commands = await create_complete_distros_expansion()
        added_count = 0
        updated_count = 0
        
        print("🚀 Adding Complete Distributions & BSD Support...")
        print(f"📦 Processing {len(commands)} distribution-specific commands...")
        
        for i, command in enumerate(commands, 1):
            existing = await db.commands.find_one({"name": command["name"]})
            if not existing:
                await db.commands.insert_one(command)
                print(f"✅ [{i:3d}] Added: {command['name']}")
                added_count += 1
            else:
                # Update with enhanced information
                await db.commands.update_one(
                    {"name": command["name"]}, 
                    {"$set": {
                        "description": command["description"],
                        "examples": command["examples"],
                        "tags": command["tags"],
                        "updated_at": datetime.now(timezone.utc)
                    }}
                )
                print(f"🔄 [{i:3d}] Enhanced: {command['name']}")
                updated_count += 1
        
        # Get final statistics
        total_commands = await db.commands.count_documents({})
        categories = await db.commands.distinct("category")
        tags = await db.commands.distinct("tags")
        
        print(f"\n🎉 Distribution expansion complete!")
        print(f"📊 Commands processed: {len(commands)}")
        print(f"📊 New commands added: {added_count}")
        print(f"📊 Commands enhanced: {updated_count}")
        print(f"📈 TOTAL COMMANDS: {total_commands}")
        print(f"📂 Categories: {len(categories)}")
        print(f"🏷️  Unique tags: {len(tags)}")
        
        # Show new distributions added
        print(f"\n🐧 NEW DISTRIBUTIONS ADDED:")
        print(f"   BSD: FreeBSD, OpenBSD, NetBSD")
        print(f"   Linux: Mint, MX Linux, EndeavourOS, Elementary, Manjaro")
        print(f"   Enterprise: openSUSE with YaST, Snapper")
        print(f"   Modern: Pop!_OS, Zorin OS with specialized tools")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_complete_distros_commands())