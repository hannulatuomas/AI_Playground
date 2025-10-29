"""
Event Logger

Logs events for learning and improvement.
"""

from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class LogEntry:
    """Event log entry."""
    timestamp: str
    module: str
    action: str
    input_data: Dict
    output_data: Dict
    success: bool
    error: Optional[str] = None
    error_type: Optional[str] = None
    context: Optional[Dict] = None
    feedback: Optional[str] = None


class EventLogger:
    """Logs events for analysis and learning."""
    
    def __init__(self, log_file: str = "events.jsonl"):
        """
        Initialize event logger.
        
        Args:
            log_file: File to store logs (JSONL format)
        """
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_event(self, module: str, action: str,
                 input_data: Dict, output_data: Dict,
                 success: bool, error: Optional[str] = None,
                 error_type: Optional[str] = None,
                 context: Optional[Dict] = None,
                 feedback: Optional[str] = None) -> LogEntry:
        """
        Log an event.
        
        Args:
            module: Module name
            action: Action performed
            input_data: Input data
            output_data: Output data
            success: Whether action succeeded
            error: Error message if failed
            error_type: Type of error
            context: Additional context
            feedback: User feedback
            
        Returns:
            LogEntry object
        """
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            module=module,
            action=action,
            input_data=input_data,
            output_data=output_data,
            success=success,
            error=error,
            error_type=error_type,
            context=context,
            feedback=feedback
        )
        
        self._write_entry(entry)
        return entry
    
    def _write_entry(self, entry: LogEntry):
        """Write entry to log file."""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                json.dump(asdict(entry), f)
                f.write('\n')
        except Exception as e:
            print(f"Error writing log entry: {e}")
    
    def read_logs(self, limit: Optional[int] = None,
                 module: Optional[str] = None,
                 success_only: bool = False,
                 errors_only: bool = False) -> List[LogEntry]:
        """
        Read log entries.
        
        Args:
            limit: Maximum number of entries to return
            module: Filter by module
            success_only: Only successful entries
            errors_only: Only failed entries
            
        Returns:
            List of LogEntry objects
        """
        if not self.log_file.exists():
            return []
        
        entries = []
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    data = json.loads(line)
                    entry = LogEntry(**data)
                    
                    # Apply filters
                    if module and entry.module != module:
                        continue
                    if success_only and not entry.success:
                        continue
                    if errors_only and entry.success:
                        continue
                    
                    entries.append(entry)
                    
                    if limit and len(entries) >= limit:
                        break
        
        except Exception as e:
            print(f"Error reading logs: {e}")
        
        return entries
    
    def get_recent_errors(self, limit: int = 50) -> List[LogEntry]:
        """Get recent error entries."""
        return self.read_logs(limit=limit, errors_only=True)
    
    def get_success_rate(self, module: Optional[str] = None) -> float:
        """
        Calculate success rate.
        
        Args:
            module: Optional module filter
            
        Returns:
            Success rate (0-1)
        """
        entries = self.read_logs(module=module)
        
        if not entries:
            return 0.0
        
        successful = sum(1 for e in entries if e.success)
        return successful / len(entries)
    
    def get_error_frequency(self, error_type: Optional[str] = None) -> Dict[str, int]:
        """
        Get frequency of errors.
        
        Args:
            error_type: Optional error type filter
            
        Returns:
            Dictionary of error_type: count
        """
        errors = self.get_recent_errors(limit=1000)
        
        frequency: Dict[str, int] = {}
        
        for entry in errors:
            if error_type and entry.error_type != error_type:
                continue
            
            err_type = entry.error_type or 'unknown'
            frequency[err_type] = frequency.get(err_type, 0) + 1
        
        return dict(sorted(frequency.items(), key=lambda x: x[1], reverse=True))
    
    def clear_logs(self):
        """Clear all logs."""
        if self.log_file.exists():
            self.log_file.unlink()
    
    def export_logs(self, output_file: str, format: str = 'json'):
        """
        Export logs to file.
        
        Args:
            output_file: Output file path
            format: Export format ('json' or 'csv')
        """
        entries = self.read_logs()
        
        if format == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(e) for e in entries], f, indent=2)
        
        elif format == 'csv':
            import csv
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                if entries:
                    writer = csv.DictWriter(f, fieldnames=asdict(entries[0]).keys())
                    writer.writeheader()
                    for entry in entries:
                        writer.writerow(asdict(entry))
