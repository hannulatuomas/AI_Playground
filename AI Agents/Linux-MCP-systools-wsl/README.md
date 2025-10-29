# Kali Linux MCP Server - Complete Edition

A comprehensive Model Context Protocol (MCP) server for Kali Linux that provides **37 powerful tools** across 7 categories for complete Linux system management.

## 🏗️ Architecture

**Modular, maintainable, and extensible** - organized into separate tool categories:

```
~/mcp-bash-server/
├── server.py                    # Main MCP server (routing & initialization)
├── README.md                    # This file
└── tools/
    ├── __init__.py             # Package initialization
    ├── shell_tools.py          # Shell execution (3 tools)
    ├── file_tools.py           # File operations (10 tools)
    ├── filesystem_tools.py     # Filesystem tools (3 tools)
    ├── text_tools.py           # Text processing (3 tools)
    ├── network_tools.py        # Network operations (6 tools)
    ├── archive_tools.py        # Archive management (5 tools)
    └── system_tools.py         # System & processes (7 tools)
```

## 🚀 Features (37 Tools)

### **🐚 Shell Execution** (shell_tools.py)
1. `execute_bash` - Execute bash commands
2. `execute_zsh` - Execute zsh with optional login shell
3. `execute_python` - Execute Python with venv support

### **📁 File Operations** (file_tools.py)
4. `read_file` - Read files (cat/head/tail/follow)
5. `write_file` - Create/append to files
6. `delete_file` - Delete files/directories (rm)
7. `copy_file` - Copy files/directories (cp)
8. `move_file` - Move/rename files (mv)
9. `create_directory` - Create directories (mkdir)
10. `change_permissions` - Change permissions (chmod)
11. `create_symlink` - Create symbolic links (ln -s)
12. `disk_usage` - Show disk usage (du/df)
13. `compare_files` - Compare files (diff)

### **🗂️ Filesystem Tools** (filesystem_tools.py)
14. `list_directory` - List directory contents (ls)
15. `find_files` - Search for files (find)
16. `file_info` - Get detailed file information (stat/file)

### **📝 Text Processing** (text_tools.py)
17. `grep_search` - Search patterns in files (grep)
18. `text_transform` - Transform text (sed/awk/cut/tr)
19. `sort_text` - Sort text files (sort)

### **🌐 Network Tools** (network_tools.py)
20. `http_request` - Make HTTP requests (curl)
21. `download_file` - Download files (wget)
22. `ping_host` - Ping hosts
23. `network_info` - Get network info (ip/ifconfig/netstat)
24. `dns_lookup` - DNS lookups (dig/nslookup)
25. `port_scan` - Scan ports (nc/nmap)

### **📦 Archive Tools** (archive_tools.py)
26. `create_archive` - Create archives (tar/zip)
27. `extract_archive` - Extract archives
28. `list_archive` - List archive contents
29. `compress_file` - Compress files (gzip/bzip2/xz)
30. `decompress_file` - Decompress files

### **⚙️ System Tools** (system_tools.py)
31. `list_processes` - List running processes (ps)
32. `kill_process` - Kill processes
33. `system_info` - Get system information (uname/hostname)
34. `system_resources` - Show resource usage (CPU/memory/disk)
35. `monitor_system` - Monitor system in real-time (top/htop)
36. `service_control` - Control services (systemctl)
37. `environment_info` - Get environment variables

## 📦 Installation

```bash
# Install dependencies
pip install mcp

# Clone or download the server files to home directory
cd ~
git clone <your-repo> mcp-bash-server
cd ~/mcp-bash-server
```

## 🔧 Usage

### Starting the Server

```bash
cd ~/mcp-bash-server
python3 server.py
```

### Example Usage

#### Network Operations
```python
# Make HTTP request
http_request(
    url="https://api.github.com/users/github",
    method="GET",
    show_headers=True
)

# Download file
download_file(
    url="https://example.com/file.zip",
    output_path="/tmp/file.zip"
)

# Ping host
ping_host(host="google.com", count=4)

# DNS lookup
dns_lookup(domain="github.com", record_type="A")

# Port scan
port_scan(host="localhost", ports="80,443,8080")
```

#### Archive Operations
```python
# Create tar.gz archive
create_archive(
    source="/var/www",
    output="/backup/www.tar.gz",
    format="tar.gz",
    exclude=["*.log", "cache/*"]
)

# Extract archive
extract_archive(
    archive="/backup/www.tar.gz",
    destination="/restore"
)

# List archive contents
list_archive(archive="backup.zip", verbose=True)

# Compress file
compress_file(
    file="/var/log/syslog",
    algorithm="gzip",
    level=9
)
```

#### System Management
```python
# List top CPU processes
list_processes(
    filter_type="top_cpu",
    limit=10
)

# Kill process
kill_process(
    name="firefox",
    signal="TERM"
)

# Get system info
system_info(info_type="all")

# Check system resources
system_resources(resource="all")

# Monitor system
monitor_system(duration=10)

# Control service
service_control(
    service="apache2",
    action="restart"
)

# Get environment
environment_info(show_all=True)
```

## 🎯 Tool Categories Summary

| Category | Tools | Description |
|----------|-------|-------------|
| **Shell** | 3 | Execute bash, zsh, Python code |
| **File Ops** | 10 | Complete file management |
| **Filesystem** | 3 | List, find, inspect files |
| **Text** | 3 | Search, transform, sort text |
| **Network** | 6 | HTTP, downloads, ping, DNS, ports |
| **Archive** | 5 | tar, zip, gzip compression |
| **System** | 7 | Processes, resources, services |
| **TOTAL** | **37** | Complete Linux toolset |

## 🛡️ Security Features

- ✅ **Command injection protection** via `shlex.quote()`
- ✅ **Timeout limits** on all operations
- ✅ **Input validation** for all parameters
- ✅ **Comprehensive logging** for audit trails
- ✅ **Safe defaults** (no force flags by default)
- ✅ **Error handling** with user-friendly messages

## 🔄 Adding New Tools

The modular architecture makes it easy to extend:

1. **Create a new tool file** in `tools/` (e.g., `database_tools.py`)
2. **Implement two functions**:
   ```python
   def register_database_tools() -> list[Tool]:
       return [Tool(...)]
   
   async def handle_database_tools(name: str, arguments: dict) -> list[TextContent] | None:
       if name == "my_tool":
           return await my_tool(arguments)
       return None
   ```
3. **Update `tools/__init__.py`** to export your functions
4. **Update `server.py`** to import and register your tools

## 📊 Performance

- **Fast**: Async/await for non-blocking operations
- **Efficient**: Direct shell execution, no overhead
- **Scalable**: Modular design supports unlimited tools
- **Reliable**: Comprehensive error handling and timeouts

## 📝 Version History

- **v4.0.0** - Added network, archive, and system tools (37 total tools)
- **v3.0.0** - Modular refactoring, improved maintainability
- **v2.1.0** - Added zsh and text processing tools
- **v2.0.0** - Added Python execution with venv support
- **v1.0.0** - Initial release with bash execution

## 🤝 Contributing

Guidelines for contributions:

1. **Follow existing patterns** - Check similar tools for structure
2. **Add comprehensive docstrings** - Explain what the tool does
3. **Validate all inputs** - Never trust user input
4. **Use `shlex.quote()`** - Protect against injection
5. **Add timeout protection** - Prevent hanging operations
6. **Log all operations** - Use the logger for debugging
7. **Return friendly messages** - Add success indicators (✓)
8. **Test thoroughly** - Verify on real Kali Linux system

## 📄 License

MIT License - Free to use, modify, and distribute.

## 🐛 Troubleshooting

**Import errors:**
```bash
cd ~/mcp-bash-server
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 server.py
```

**Permission denied:**
```bash
chmod +x ~/mcp-bash-server/server.py
```

**Missing commands:**
```bash
# Install required tools
sudo apt update
sudo apt install curl wget net-tools dnsutils netcat nmap
```

## 💡 Use Cases

### Development
- Execute code in isolated venvs
- Manage project files and directories
- Search and transform source code
- Monitor system resources during builds

### DevOps
- Deploy applications with archive tools
- Monitor services and processes
- Manage system resources
- Network diagnostics and testing

### Security/Pentesting
- Port scanning and reconnaissance
- Network traffic analysis
- System enumeration
- Process investigation

### System Administration
- File and directory management
- Service control and monitoring
- Resource usage tracking
- Log file analysis

## 🎓 Learning Resources

Each tool category includes practical examples in the code. Check:
- Tool docstrings for parameter details
- `inputSchema` for all available options
- Handler functions for implementation patterns

## 📞 Support

- Check the logs for detailed error messages
- Review tool input schemas for parameter requirements
- Test commands manually first with `execute_bash`

## 🌟 Highlights

- **37 comprehensive tools** covering all Linux basics
- **Modular architecture** - easy to maintain and extend
- **Production-ready** with proper error handling
- **Well-documented** with examples and schemas
- **Secure by default** with command injection protection
- **Actively maintained** and ready for contributions

## 🔮 Future Enhancements

Potential additions for future versions:
- Database management tools (MySQL, PostgreSQL)
- Container tools (Docker, Podman)
- Git operations
- Package management (apt, dpkg)
- User/group management
- Firewall configuration
- Log analysis tools
- Backup/restore utilities

---

**Built with ❤️ for the Kali Linux and MCP community**

**Server Version:** 4.0.0  
**Total Tools:** 37  
**Categories:** 7  
**License:** MIT
