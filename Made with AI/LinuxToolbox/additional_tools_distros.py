#!/usr/bin/env python3

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

# Additional Tools and Distributions
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'linux_admin_tool')

async def add_more_tools_and_distros():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # More specialized tools and commands
    additional_commands = [
        # More Kali Tools
        {
            "id": str(uuid.uuid4()),
            "name": "sqlmap",
            "description": "Automatic SQL injection and database takeover tool",
            "syntax": "sqlmap [options]",
            "examples": [
                "sqlmap -u 'http://example.com/page?id=1'",
                "sqlmap -r request.txt",
                "sqlmap --dbs -u 'http://example.com/page?id=1'",
                "sqlmap --dump -D database -T table -u 'target'"
            ],
            "category": "Web Application Security",
            "tags": ["sql injection", "database", "web security", "kali", "penetration testing"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "nikto",
            "description": "Web server scanner for identifying dangerous files and programs",
            "syntax": "nikto [options]",
            "examples": [
                "nikto -h http://example.com",
                "nikto -h https://example.com -p 443",
                "nikto -h example.com -Format htm -output report.html"
            ],
            "category": "Web Application Security",
            "tags": ["web scanner", "vulnerability", "kali", "security", "web security"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "gobuster",
            "description": "Directory/file & DNS busting tool written in Go",
            "syntax": "gobuster [mode] [flags]",
            "examples": [
                "gobuster dir -u http://example.com -w /usr/share/wordlists/dirb/common.txt",
                "gobuster dns -d example.com -w subdomains.txt",
                "gobuster vhost -u http://example.com -w vhosts.txt"
            ],
            "category": "Web Application Security",
            "tags": ["directory busting", "dns", "enumeration", "kali", "go"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "dirb",
            "description": "Web Content Scanner for finding existing web objects",
            "syntax": "dirb <url> [wordlist] [options]",
            "examples": [
                "dirb http://example.com",
                "dirb http://example.com /usr/share/dirb/wordlists/common.txt",
                "dirb https://example.com -X .php,.html"
            ],
            "category": "Web Application Security",
            "tags": ["web scanner", "directory", "enumeration", "kali"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "hydra",
            "description": "Very fast network logon cracker supporting many protocols",
            "syntax": "hydra [options] target protocol",
            "examples": [
                "hydra -l admin -P passwords.txt ssh://192.168.1.1",
                "hydra -L users.txt -P pass.txt ftp://192.168.1.100",
                "hydra -l admin -p password http-get://example.com/admin/"
            ],
            "category": "Password Attacks",
            "tags": ["brute force", "password", "network", "kali", "cracking"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # Container and Virtualization Tools
        {
            "id": str(uuid.uuid4()),
            "name": "podman",
            "description": "Daemonless container engine for developing, managing, and running OCI Containers",
            "syntax": "podman [global options] command [command options]",
            "examples": [
                "podman run -it ubuntu bash",
                "podman ps -a",
                "podman build -t myapp .",
                "podman pod create --name mypod"
            ],
            "category": "Development Tools",
            "tags": ["containers", "podman", "oci", "rhel", "fedora", "rootless"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "vagrant",
            "description": "Build and maintain portable virtual software development environments",
            "syntax": "vagrant [command] [options]",
            "examples": [
                "vagrant init ubuntu/bionic64",
                "vagrant up",
                "vagrant ssh",
                "vagrant destroy"
            ],
            "category": "Development Tools",
            "tags": ["virtualization", "vagrant", "development", "vm", "ubuntu", "debian"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # System Performance and Debugging
        {
            "id": str(uuid.uuid4()),
            "name": "strace",
            "description": "Trace system calls and signals for debugging",
            "syntax": "strace [options] command [args]",
            "examples": [
                "strace ls",
                "strace -p 1234",
                "strace -o output.txt command",
                "strace -e trace=network curl google.com"
            ],
            "category": "System Monitoring",
            "tags": ["debugging", "system calls", "trace", "ubuntu", "debian", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "perf",
            "description": "Linux profiling with performance counters",
            "syntax": "perf [command] [options]",
            "examples": [
                "perf top",
                "perf record ./myprogram",
                "perf report",
                "perf stat ls"
            ],
            "category": "System Monitoring",
            "tags": ["performance", "profiling", "cpu", "ubuntu", "debian", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # Advanced Text Processing
        {
            "id": str(uuid.uuid4()),
            "name": "jq",
            "description": "Command-line JSON processor for parsing and manipulating JSON data",
            "syntax": "jq [options] filter [files...]",
            "examples": [
                "curl -s api.example.com | jq '.'",
                "cat data.json | jq '.items[]'",
                "jq '.name, .version' package.json",
                "echo '{\"name\":\"test\"}' | jq -r '.name'"
            ],
            "category": "Text Processing",
            "tags": ["json", "parsing", "api", "ubuntu", "debian", "arch", "fedora"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "yq",
            "description": "YAML/XML/TOML processor - jq wrapper for non-JSON formats",
            "syntax": "yq [options] expression [files...]",
            "examples": [
                "yq '.spec.containers[0].image' deployment.yaml",
                "yq eval '.database.host' config.yaml",
                "yq -i '.version = \"2.0\"' config.yaml"
            ],
            "category": "Text Processing",
            "tags": ["yaml", "xml", "parsing", "config", "ubuntu", "debian", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # Modern CLI Tools
        {
            "id": str(uuid.uuid4()),
            "name": "fd",
            "description": "Simple, fast and user-friendly alternative to find",
            "syntax": "fd [options] [pattern] [path...]",
            "examples": [
                "fd pattern",
                "fd -e js",
                "fd -t f -x wc -l",
                "fd . /home --type f --size +1m"
            ],
            "category": "File Management",
            "tags": ["find", "search", "modern", "rust", "ubuntu", "debian", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "ripgrep",
            "description": "Recursively searches directories for a regex pattern (rg)",
            "syntax": "rg [options] pattern [path...]",
            "examples": [
                "rg 'pattern' .",
                "rg -i case_insensitive",
                "rg --type py 'import'",
                "rg -n 'TODO' src/"
            ],
            "category": "Text Processing",
            "tags": ["grep", "search", "rust", "fast", "ubuntu", "debian", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "bat",
            "description": "Cat clone with syntax highlighting and Git integration",
            "syntax": "bat [options] [files...]",
            "examples": [
                "bat file.py",
                "bat -n file.txt",
                "bat --style=plain file.md",
                "curl -s https://sh.rustup.rs | bat -l sh"
            ],
            "category": "Text Processing",
            "tags": ["cat", "syntax highlighting", "rust", "ubuntu", "debian", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "exa",
            "description": "Modern replacement for ls with colors and icons",
            "syntax": "exa [options] [files...]",
            "examples": [
                "exa -la",
                "exa --tree",
                "exa --grid --icons",
                "exa -lh --git"
            ],
            "category": "File Management",
            "tags": ["ls", "listing", "modern", "rust", "ubuntu", "debian", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # Cloud Native Tools
        {
            "id": str(uuid.uuid4()),
            "name": "helm",
            "description": "Package manager for Kubernetes applications",
            "syntax": "helm [command] [options]",
            "examples": [
                "helm install myapp ./mychart",
                "helm list",
                "helm upgrade myapp ./mychart",
                "helm uninstall myapp"
            ],
            "category": "Development Tools",
            "tags": ["kubernetes", "helm", "package manager", "cloud", "ubuntu", "rhel"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "istio",
            "description": "Service mesh for microservices with traffic management and security",
            "syntax": "istioctl [command] [options]",
            "examples": [
                "istioctl install",
                "istioctl analyze",
                "istioctl proxy-status",
                "istioctl kube-inject -f deployment.yaml"
            ],
            "category": "Development Tools",
            "tags": ["service mesh", "microservices", "kubernetes", "cloud", "ubuntu"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # Package managers for different distros
        {
            "id": str(uuid.uuid4()),
            "name": "emerge",
            "description": "Gentoo's package management system for compiling from source",
            "syntax": "emerge [options] [packages...]",
            "examples": [
                "emerge package_name",
                "emerge --sync",
                "emerge -uDN @world",
                "emerge --search keyword"
            ],
            "category": "Package Management",
            "tags": ["package manager", "gentoo", "source", "compile"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "apk",
            "description": "Alpine Package Keeper for Alpine Linux package management",
            "syntax": "apk [options] command [packages...]",
            "examples": [
                "apk add package_name",
                "apk update",
                "apk upgrade",
                "apk del package_name",
                "apk search keyword"
            ],
            "category": "Package Management",
            "tags": ["package manager", "alpine", "docker", "lightweight"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "flatpak",
            "description": "Universal package management system for Linux applications",
            "syntax": "flatpak [options] command [args...]",
            "examples": [
                "flatpak install flathub org.gimp.GIMP",
                "flatpak list",
                "flatpak update",
                "flatpak run org.gimp.GIMP"
            ],
            "category": "Package Management",
            "tags": ["universal packages", "flatpak", "ubuntu", "debian", "fedora", "arch"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "snap",
            "description": "Universal Linux package management system by Canonical",
            "syntax": "snap [options] command [args...]",
            "examples": [
                "snap install discord",
                "snap list",
                "snap refresh",
                "snap remove discord"
            ],
            "category": "Package Management",
            "tags": ["universal packages", "snap", "ubuntu", "canonical"],
            "created_by": "system",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ]
    
    try:
        # Insert additional commands
        added_count = 0
        for command in additional_commands:
            existing = await db.commands.find_one({"name": command["name"]})
            if not existing:
                await db.commands.insert_one(command)
                print(f"✅ Added command: {command['name']}")
                added_count += 1
            else:
                print(f"⏭️  Skipping existing command: {command['name']}")
        
        print(f"\n🎉 Additional tools and distros population complete!")
        print(f"📊 New commands added: {added_count}")
        
        # Update database statistics
        total_commands = await db.commands.count_documents({})
        categories = await db.commands.distinct("category")
        tags = await db.commands.distinct("tags")
        
        print(f"\n📈 Updated Database Statistics:")
        print(f"   Total commands: {total_commands}")
        print(f"   Categories: {len(categories)}")
        print(f"   Unique tags: {len(tags)}")
        
        # Show some new distributions added
        distro_tags = [tag for tag in tags if tag.lower() in ['alpine', 'gentoo', 'manjaro', 'elementary']]
        if distro_tags:
            print(f"   New distributions: {', '.join(distro_tags)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_more_tools_and_distros())