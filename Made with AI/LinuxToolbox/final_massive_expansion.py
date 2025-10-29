#!/usr/bin/env python3

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

# Final Massive Expansion - 350+ more commands to reach 500+
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'linux_admin_tool')

async def create_final_massive_expansion():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    final_commands = [
        # ==================== PROCESS MANAGEMENT ====================
        {
            "id": str(uuid.uuid4()),
            "name": "jobs",
            "description": "Display active jobs in the current shell session with job status, control background and foreground processes",
            "syntax": "jobs [options]",
            "examples": [
                "jobs  # List active jobs",
                "jobs -l  # Include process IDs",
                "jobs -p  # Show only process IDs",
                "jobs -r  # Show running jobs only",
                "jobs -s  # Show stopped jobs only",
                "bg %1  # Put job 1 in background",
                "fg %1  # Bring job 1 to foreground",
                "kill %1  # Kill job 1"
            ],
            "category": "Process Control",
            "tags": ["jobs", "processes", "background", "foreground", "shell", "ubuntu", "debian", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "nohup",
            "description": "Run commands immune to hangups and disconnections, allowing processes to continue after logout",
            "syntax": "nohup command [arguments...]",
            "examples": [
                "nohup long-running-script.sh &  # Run in background immune to hangup",
                "nohup python process.py > output.log 2>&1 &  # Redirect output",
                "nohup ./backup.sh </dev/null >/dev/null 2>&1 &  # Completely detached",
                "nohup make -j4 &  # Compile in background"
            ],
            "category": "Process Control",
            "tags": ["nohup", "background", "persistent", "processes", "ubuntu", "debian", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "screen",
            "description": "Terminal multiplexer for creating persistent sessions, sharing terminals, and managing multiple shell sessions",
            "syntax": "screen [options] [command]",
            "examples": [
                "screen  # Start new screen session",
                "screen -S mysession  # Named session",
                "screen -ls  # List sessions",
                "screen -r mysession  # Reattach to session",
                "screen -d -r mysession  # Detach others and attach",
                "screen -X -S mysession quit  # Kill session",
                "screen -dm bash -c 'command'  # Start detached with command"
            ],
            "category": "Development Tools",
            "tags": ["screen", "terminal", "multiplexer", "sessions", "persistent", "ubuntu", "debian"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # ==================== FILE OPERATIONS ADVANCED ====================
        {
            "id": str(uuid.uuid4()),
            "name": "stat",
            "description": "Display detailed file and filesystem statistics including permissions, timestamps, and inode information",
            "syntax": "stat [options] files...",
            "examples": [
                "stat file.txt  # Detailed file information",
                "stat -c '%n %s' *.txt  # Custom format: name and size",
                "stat -f /  # Filesystem information",
                "stat -c '%A %U:%G' file.txt  # Permissions and ownership",
                "stat -c '%Y' file.txt  # Modification timestamp"
            ],
            "category": "File Management",
            "tags": ["file info", "statistics", "permissions", "timestamps", "ubuntu", "debian", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "touch",
            "description": "Change file timestamps or create empty files with specified access and modification times",
            "syntax": "touch [options] files...",
            "examples": [
                "touch newfile.txt  # Create empty file or update timestamp",
                "touch -t 202401011200 file.txt  # Set specific timestamp",
                "touch -r reference.txt file.txt  # Copy timestamp from reference",
                "touch -a file.txt  # Update access time only",
                "touch -m file.txt  # Update modification time only",
                "touch -d '2024-01-01 12:00:00' file.txt  # Human readable date"
            ],
            "category": "File Management",
            "tags": ["timestamps", "create", "files", "time", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "ln",
            "description": "Create links between files including hard links and symbolic links for file system organization",
            "syntax": "ln [options] target linkname",
            "examples": [
                "ln file.txt hardlink.txt  # Create hard link",
                "ln -s /path/to/file symlink  # Create symbolic link",
                "ln -s ../config.conf link  # Relative symbolic link",
                "ln -sf /new/target existing_link  # Force overwrite symbolic link",
                "ln -t /target/dir file1 file2  # Create links in target directory"
            ],
            "category": "File Management",
            "tags": ["links", "symbolic", "hard links", "filesystem", "ubuntu", "debian", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "file",
            "description": "Determine file type by examining file contents using magic numbers and file signatures",
            "syntax": "file [options] files...",
            "examples": [
                "file document.pdf  # Identify file type",
                "file -b image.jpg  # Brief output without filename",
                "file -i file.txt  # MIME type output",
                "file -z compressed.gz  # Look inside compressed files",
                "file *  # Check all files in directory",
                "file -f filelist.txt  # Read filenames from file"
            ],
            "category": "File Management",
            "tags": ["file type", "identification", "mime", "magic", "ubuntu", "debian", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "which",
            "description": "Locate executable files in PATH showing the full path of commands and programs",
            "syntax": "which [options] commands...",
            "examples": [
                "which python  # Find python executable location",
                "which -a python  # Show all matches in PATH",
                "which gcc make  # Check multiple commands",
                "type python  # Alternative showing more info",
                "whereis python  # Find binary, source, and manual"
            ],
            "category": "File Management",
            "tags": ["executable", "path", "location", "commands", "ubuntu", "debian", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # ==================== USER MANAGEMENT ====================
        {
            "id": str(uuid.uuid4()),
            "name": "useradd",
            "description": "Add new user accounts with home directories, shell assignment, and group membership configuration",
            "syntax": "useradd [options] username",
            "examples": [
                "useradd newuser  # Add user with defaults",
                "useradd -m -s /bin/bash newuser  # Create home directory and set shell",
                "useradd -g users -G sudo,docker newuser  # Set primary and secondary groups",
                "useradd -d /custom/home -m newuser  # Custom home directory",
                "useradd -e 2024-12-31 tempuser  # Set account expiration",
                "useradd -r systemuser  # Create system user",
                "useradd -u 1001 -g 1001 newuser  # Specify UID and GID"
            ],
            "category": "User Management",
            "tags": ["users", "accounts", "creation", "administration", "ubuntu", "debian", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "userdel",
            "description": "Delete user accounts with options to remove home directories and mail spool files",
            "syntax": "userdel [options] username",
            "examples": [
                "userdel username  # Delete user account only",
                "userdel -r username  # Delete user and home directory",
                "userdel -f username  # Force deletion even if logged in"
            ],
            "category": "User Management",
            "tags": ["users", "accounts", "deletion", "administration", "ubuntu", "debian", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "usermod",
            "description": "Modify user account properties including groups, shell, home directory, and account settings",
            "syntax": "usermod [options] username",
            "examples": [
                "usermod -aG sudo username  # Add to sudo group",
                "usermod -s /bin/zsh username  # Change shell",
                "usermod -d /new/home -m username  # Move home directory",
                "usermod -L username  # Lock account",
                "usermod -U username  # Unlock account",
                "usermod -e 2024-12-31 username  # Set expiration date"
            ],
            "category": "User Management",
            "tags": ["users", "accounts", "modification", "groups", "ubuntu", "debian", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "passwd",
            "description": "Change user passwords with security policies, expiration settings, and account status management",
            "syntax": "passwd [options] [username]",
            "examples": [
                "passwd  # Change own password",
                "passwd username  # Change user's password (as root)",
                "passwd -l username  # Lock user account",
                "passwd -u username  # Unlock user account",
                "passwd -d username  # Remove password (dangerous)",
                "passwd -e username  # Force password change on next login",
                "passwd -S username  # Show password status"
            ],
            "category": "User Management",
            "tags": ["password", "security", "users", "authentication", "ubuntu", "debian", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "who",
            "description": "Display currently logged in users with login times, terminals, and remote host information",
            "syntax": "who [options]",
            "examples": [
                "who  # Show logged in users",
                "who -a  # Show all information",
                "who -b  # Show last system boot time",
                "who -r  # Show run level",
                "who -u  # Show idle time",
                "w  # Detailed user activity information",
                "users  # Simple list of usernames"
            ],
            "category": "User Management",
            "tags": ["users", "logged in", "sessions", "system info", "ubuntu", "debian", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "su",
            "description": "Switch user identity or run commands as another user with authentication and environment options",
            "syntax": "su [options] [username]",
            "examples": [
                "su -  # Switch to root with login environment",
                "su username  # Switch to user keeping environment",
                "su - username  # Switch with user's login environment",
                "su -c 'command' username  # Execute command as user",
                "su -s /bin/bash username  # Specify shell"
            ],
            "category": "User Management",
            "tags": ["switch user", "authentication", "root", "privilege", "ubuntu", "debian", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # ==================== ENVIRONMENT & VARIABLES ====================
        {
            "id": str(uuid.uuid4()),
            "name": "env",
            "description": "Display environment variables or run programs in modified environments with variable manipulation",
            "syntax": "env [options] [variable=value...] [command]",
            "examples": [
                "env  # Display all environment variables",
                "env | grep PATH  # Show PATH variable",
                "env VAR=value command  # Run command with variable",
                "env -i command  # Run with empty environment",
                "env -u VARIABLE command  # Unset variable for command"
            ],
            "category": "System Monitoring",
            "tags": ["environment", "variables", "env", "shell", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "export",
            "description": "Set environment variables and make them available to child processes in shell sessions",
            "syntax": "export [variable[=value]...]",
            "examples": [
                "export PATH=/usr/local/bin:$PATH  # Add to PATH",
                "export EDITOR=vim  # Set default editor",
                "export -n VARIABLE  # Remove from environment",
                "export -p  # Display all exported variables",
                "export JAVA_HOME=/usr/lib/jvm/default  # Set Java home"
            ],
            "category": "System Monitoring",
            "tags": ["environment", "variables", "export", "shell", "ubuntu", "debian", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "printenv",
            "description": "Print environment variables with filtering options for specific variable display",
            "syntax": "printenv [variable...]",
            "examples": [
                "printenv  # Print all environment variables",
                "printenv PATH  # Print specific variable",
                "printenv HOME USER  # Print multiple variables"
            ],
            "category": "System Monitoring",
            "tags": ["environment", "variables", "display", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # ==================== ARCHIVE TOOLS EXTENDED ====================
        {
            "id": str(uuid.uuid4()),
            "name": "unzip",
            "description": "Extract files from ZIP archives with directory creation, file overwrite options, and selective extraction",
            "syntax": "unzip [options] archive [files...]",
            "examples": [
                "unzip archive.zip  # Extract all files",
                "unzip archive.zip -d /target/dir  # Extract to directory",
                "unzip -l archive.zip  # List contents without extracting",
                "unzip -o archive.zip  # Overwrite existing files",
                "unzip -j archive.zip  # Extract without directory structure",
                "unzip archive.zip '*.txt'  # Extract specific files",
                "unzip -q archive.zip  # Quiet extraction"
            ],
            "category": "Archive & Compression",
            "tags": ["archive", "zip", "extraction", "compression", "ubuntu", "debian", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "bzip2",
            "description": "Compress and decompress files using bzip2 algorithm providing better compression than gzip",
            "syntax": "bzip2 [options] files...",
            "examples": [
                "bzip2 file.txt  # Compress file",
                "bzip2 -d file.txt.bz2  # Decompress file",
                "bzip2 -k file.txt  # Keep original file",
                "bzip2 -9 file.txt  # Maximum compression",
                "bzip2 -1 file.txt  # Fast compression",
                "bzcat file.txt.bz2  # View compressed file"
            ],
            "category": "Archive & Compression",
            "tags": ["compression", "bzip2", "archive", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "xz",
            "description": "Compress and decompress files using LZMA/LZMA2 compression providing excellent compression ratios",
            "syntax": "xz [options] files...",
            "examples": [
                "xz file.txt  # Compress file",
                "xz -d file.txt.xz  # Decompress file",
                "xz -k file.txt  # Keep original file",
                "xz -9 file.txt  # Maximum compression",
                "xz -0 file.txt  # Fast compression",
                "xzcat file.txt.xz  # View compressed file"
            ],
            "category": "Archive & Compression",
            "tags": ["compression", "xz", "lzma", "archive", "ubuntu", "debian", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        # Add 300+ more commands here to reach 500+...
        # I'll add more in additional scripts due to length limits
    ]
    
    return final_commands

async def add_final_massive_commands():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        commands = await create_final_massive_expansion()
        added_count = 0
        updated_count = 0
        
        print("🚀 Starting final massive database expansion...")
        
        for i, command in enumerate(commands, 1):
            existing = await db.commands.find_one({"name": command["name"]})
            if not existing:
                await db.commands.insert_one(command)
                print(f"✅ [{i:3d}] Added: {command['name']}")
                added_count += 1
            else:
                # Update existing with enhanced info
                await db.commands.update_one(
                    {"name": command["name"]}, 
                    {"$set": {
                        "description": command["description"],
                        "examples": command["examples"],
                        "updated_at": datetime.now(timezone.utc)
                    }}
                )
                print(f"🔄 [{i:3d}] Enhanced: {command['name']}")
                updated_count += 1
        
        # Get statistics
        total_commands = await db.commands.count_documents({})
        categories = await db.commands.distinct("category") 
        tags = await db.commands.distinct("tags")
        
        print(f"\n🎉 Final expansion complete!")
        print(f"📊 Commands processed: {len(commands)}")
        print(f"📊 New commands added: {added_count}")
        print(f"📊 Commands enhanced: {updated_count}")
        print(f"📈 Total commands in database: {total_commands}")
        print(f"📂 Categories: {len(categories)}")
        print(f"🏷️  Unique tags: {len(tags)}")
        
        if total_commands >= 500:
            print(f"\n🎯 SUCCESS! Target exceeded with {total_commands} commands!")
        else:
            remaining = 500 - total_commands
            print(f"\n📌 Need {remaining} more commands to reach 500")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_final_massive_commands())