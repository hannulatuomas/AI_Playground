# Quick Reference Guide

## Tool Categories

### 🐚 Shell Execution
```python
execute_bash(command="ls -la")
execute_zsh(command="git status", use_login_shell=True)
execute_python(code="print('hello')", venv_path="/tmp/venv", packages=["requests"])
```

### 📁 File Operations
```python
read_file(path="/etc/hosts", mode="cat")
write_file(path="/tmp/file.txt", content="data", append=False)
delete_file(path="/tmp/old", recursive=True)
copy_file(source="/a", destination="/b", recursive=True)
move_file(source="/old", destination="/new")
create_directory(path="/tmp/new/dir", parents=True)
change_permissions(path="/script.sh", mode="755")
create_symlink(target="/usr/bin/python3", link_name="/usr/local/bin/python")
disk_usage(path="/home", command="du", summary=True)
compare_files(file1="/a", file2="/b", unified=True)
```

### 🗂️ Filesystem
```python
list_directory(path="/var", show_hidden=True, long_format=True)
find_files(path="/home", name_pattern="*.py", file_type="f")
file_info(path="/etc/passwd")
```

### 📝 Text Processing
```python
grep_search(pattern="error", path="/var/log", recursive=True, ignore_case=True)
text_transform(input_path="/file", operation="sed", sed_pattern="s/old/new/g")
sort_text(input_path="/numbers.txt", numeric=True, unique=True)
```

### 🌐 Network
```python
http_request(url="https://api.github.com", method="GET", show_headers=True)
download_file(url="https://example.com/file.zip", output_path="/tmp/file.zip")
ping_host(host="google.com", count=4)
network_info(command="interfaces")
dns_lookup(domain="github.com", record_type="A")
port_scan(host="localhost", ports="1-1000")
```

### 📦 Archives
```python
create_archive(source="/data", output="/backup.tar.gz", format="tar.gz")
extract_archive(archive="/backup.tar.gz", destination="/restore")
list_archive(archive="/backup.zip", verbose=True)
compress_file(file="/log.txt", algorithm="gzip", level=9)
decompress_file(file="/log.txt.gz", keep_original=True)
```

### ⚙️ System
```python
list_processes(filter_type="top_cpu", limit=10)
kill_process(pid=1234, signal="TERM")
system_info(info_type="all")
system_resources(resource="all")
monitor_system(duration=5)
service_control(service="apache2", action="status")
environment_info(show_all=False)
```

## Common Patterns

### File Management Workflow
```python
# Create project structure
create_directory(path="/project/src", parents=True)
create_directory(path="/project/tests", parents=True)

# Write files
write_file(path="/project/README.md", content="# My Project")
write_file(path="/project/src/main.py", content="print('Hello')")

# Set permissions
change_permissions(path="/project/src/main.py", mode="755")

# List contents
list_directory(path="/project", recursive=True)
```

### Backup Workflow
```python
# Create backup
create_archive(
    source="/var/www",
    output="/backups/www-2025-01-10.tar.gz",
    format="tar.gz",
    exclude=["*.log", "cache/*"]
)

# Verify archive
list_archive(archive="/backups/www-2025-01-10.tar.gz")

# Check size
disk_usage(path="/backups", summary=True)
```

### System Monitoring
```python
# Check system
system_info(info_type="all")
system_resources(resource="all")

# Check processes
list_processes(filter_type="top_cpu", limit=10)
list_processes(filter_type="top_mem", limit=10)

# Monitor services
service_control(service="apache2", action="status")
service_control(service="mysql", action="status")
```

### Network Diagnostics
```python
# Check connectivity
ping_host(host="google.com", count=4)

# DNS lookup
dns_lookup(domain="example.com", record_type="A")

# Check open ports
port_scan(host="localhost", ports="1-1000")

# Get network info
network_info(command="interfaces")
network_info(command="connections")
```

## Tips & Best Practices

### Security
- Always use `force=False` for destructive operations initially
- Test with `list_only=True` for archives before extracting
- Check file permissions before modifying
- Use `--dry-run` equivalent options when available

### Performance
- Use `summary=True` for disk_usage on large directories
- Limit process lists with `limit` parameter
- Use appropriate timeouts for long-running operations
- Use streaming for large file operations

### Debugging
- Check logs for detailed error messages
- Use `verbose=True` options for more output
- Test commands with `execute_bash` first
- Verify paths exist before operations

### Efficiency
- Combine operations with shell execution when appropriate
- Use recursive options instead of loops
- Leverage pipes and redirects in bash/zsh
- Cache frequently accessed data

## Error Handling

All tools return structured responses:
```
Exit Code: 0

STDOUT:
<command output>

STDERR:
<error messages if any>

✓ Success message (if applicable)
```

Exit codes:
- `0` = Success
- `1` = General error
- `2` = Misuse of shell command
- `124` = Timeout
- `127` = Command not found

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Command not found | Install required package |
| Permission denied | Use appropriate user or sudo |
| Timeout | Increase timeout parameter |
| File not found | Check path and existence |
| Network error | Check connectivity and firewall |
| Archive error | Verify archive integrity |
| Process error | Check PID/name exists |

## Environment Variables

Common variables used:
- `$PATH` - Command search path
- `$HOME` - User home directory
- `$USER` - Current username
- `$SHELL` - Current shell
- `$PWD` - Present working directory

Access with:
```python
environment_info(variable="PATH")
```
