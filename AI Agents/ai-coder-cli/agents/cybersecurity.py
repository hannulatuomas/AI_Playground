
"""
Cybersecurity Agent

Production-ready implementation for cybersecurity tasks with ethical safeguards.
"""

from typing import Dict, Any, List, Optional, Tuple, Set
import re
import socket
import hashlib
import ssl
import time
from datetime import datetime, timedelta
from pathlib import Path

from .base import Agent


class CybersecurityAgent(Agent):
    """
    Production-ready Cybersecurity Agent.
    
    ⚠️  LEGAL NOTICE: Only scan systems you own or have explicit permission to test.
    Unauthorized scanning is illegal.
    
    Features:
        - Password strength analysis
        - Port scanning (with authorization)
        - SSL/TLS certificate validation
        - File hash computation
        - Security recommendations
    """
    
    COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 8080, 8443]
    MAX_SCANS_PER_MINUTE = 10
    PASSWORD_MIN_LENGTH = 8
    
    def __init__(self, name: str = "cybersecurity", 
                 description: str = "Cybersecurity agent", **kwargs):
        super().__init__(name=name, description=description, **kwargs)
        self._scan_history: List[datetime] = []
        self.logger.info("Cybersecurity Agent initialized")
        self.logger.warning("NOTICE: Only scan systems you own or have permission to test")
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute cybersecurity task."""
        self._log_action("Security task", task[:100])
        
        try:
            operation = context.get('operation', self._detect_operation(task))
            
            if operation == 'password_strength':
                return self._check_password_strength(context.get('password', ''))
            elif operation == 'port_scan':
                return self._handle_port_scan(context)
            elif operation == 'ssl_check':
                return self._check_ssl(context)
            elif operation == 'file_hash':
                return self._compute_hashes(context.get('file_path', ''))
            elif operation == 'recommendations':
                return self._get_recommendations()
            else:
                return self._build_error_result("Unknown operation. Specify 'operation' in context")
        except Exception as e:
            self.logger.error(f"Task failed: {e}", exc_info=True)
            return self._build_error_result(f"Task failed: {str(e)}", error=e)
    
    def _detect_operation(self, task: str) -> str:
        """Detect operation from task description."""
        task_lower = task.lower()
        if 'password' in task_lower:
            return 'password_strength'
        elif 'port' in task_lower or 'scan' in task_lower:
            return 'port_scan'
        elif 'ssl' in task_lower or 'cert' in task_lower:
            return 'ssl_check'
        elif 'hash' in task_lower:
            return 'file_hash'
        elif 'recommend' in task_lower:
            return 'recommendations'
        return 'unknown'
    
    def _check_password_strength(self, password: str) -> Dict[str, Any]:
        """Analyze password strength."""
        if not password:
            return self._build_error_result("Password required in context")
        
        analysis = {
            'length': len(password),
            'has_lowercase': bool(re.search(r'[a-z]', password)),
            'has_uppercase': bool(re.search(r'[A-Z]', password)),
            'has_digit': bool(re.search(r'\d', password)),
            'has_special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        }
        
        score = sum([
            analysis['length'] >= 8,
            analysis['length'] >= 12,
            analysis['has_lowercase'],
            analysis['has_uppercase'],
            analysis['has_digit'],
            analysis['has_special']
        ])
        
        rating = 'strong' if score >= 5 else 'moderate' if score >= 3 else 'weak'
        
        return self._build_success_result(
            f"Password strength: {rating} ({score}/6)",
            data={**analysis, 'score': score, 'rating': rating}
        )
    
    def _handle_port_scan(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle port scanning with authorization check."""
        target = context.get('target', 'localhost')
        
        # MANDATORY AUTHORIZATION
        if not context.get('authorized') or not context.get('authorization_token'):
            return self._build_error_result(
                "⚠️  PORT SCANNING REQUIRES AUTHORIZATION\n"
                "Set 'authorized': True and 'authorization_token' in context.\n"
                "Only scan systems you own or have written permission to test."
            )
        
        if not self._check_rate_limit():
            return self._build_error_result("Rate limit exceeded")
        
        self._record_scan()
        ports = context.get('ports', self.COMMON_PORTS[:5])  # Limit to 5 ports by default
        
        return self._scan_ports(target, ports)
    
    def _scan_ports(self, target: str, ports: List[int]) -> Dict[str, Any]:
        """Perform port scanning."""
        try:
            open_ports = []
            for port in ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((target, port))
                    if result == 0:
                        open_ports.append(port)
                    sock.close()
                    time.sleep(0.1)  # Rate limiting
                except:
                    pass
            
            return self._build_success_result(
                f"Scan complete: {len(open_ports)} open ports",
                data={'target': target, 'open_ports': open_ports, 'scanned': len(ports)}
            )
        except Exception as e:
            return self._build_error_result(f"Scan failed: {str(e)}", error=e)
    
    def _check_ssl(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check SSL certificate."""
        host = context.get('host')
        if not host:
            return self._build_error_result("SSL check requires 'host' in context")
        
        port = context.get('port', 443)
        
        try:
            context_ssl = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=10) as sock:
                with context_ssl.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    
            info = {
                'subject': dict(x[0] for x in cert.get('subject', [])),
                'issuer': dict(x[0] for x in cert.get('issuer', [])),
                'version': cert.get('version'),
                'not_before': cert.get('notBefore'),
                'not_after': cert.get('notAfter')
            }
            
            return self._build_success_result(
                f"SSL certificate retrieved for {host}",
                data=info
            )
        except Exception as e:
            return self._build_error_result(f"SSL check failed: {str(e)}", error=e)
    
    def _compute_hashes(self, file_path: str) -> Dict[str, Any]:
        """Compute file hashes."""
        if not file_path:
            return self._build_error_result("File path required")
        
        path = Path(file_path)
        if not path.exists():
            return self._build_error_result(f"File not found: {file_path}")
        
        try:
            md5 = hashlib.md5()
            sha256 = hashlib.sha256()
            
            with open(path, 'rb') as f:
                while chunk := f.read(8192):
                    md5.update(chunk)
                    sha256.update(chunk)
            
            return self._build_success_result(
                "Hashes computed",
                data={
                    'file': str(path),
                    'md5': md5.hexdigest(),
                    'sha256': sha256.hexdigest()
                }
            )
        except Exception as e:
            return self._build_error_result(f"Hash computation failed: {str(e)}", error=e)
    
    def _get_recommendations(self) -> Dict[str, Any]:
        """Provide security recommendations."""
        recommendations = [
            "Use strong, unique passwords (12+ chars, mixed case, numbers, symbols)",
            "Enable two-factor authentication (2FA)",
            "Keep software and systems updated",
            "Use HTTPS everywhere",
            "Regular security audits",
            "Implement principle of least privilege",
            "Regular backups",
            "Monitor logs for suspicious activity"
        ]
        
        return self._build_success_result(
            "Security recommendations",
            data={'recommendations': recommendations}
        )
    
    def _check_rate_limit(self) -> bool:
        """Check rate limiting."""
        cutoff = datetime.now() - timedelta(minutes=1)
        self._scan_history = [t for t in self._scan_history if t > cutoff]
        return len(self._scan_history) < self.MAX_SCANS_PER_MINUTE
    
    def _record_scan(self) -> None:
        """Record scan for rate limiting."""
        self._scan_history.append(datetime.now())
