"""
HTTP request/response logger for MockMaster
"""

import json
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from collections import deque


class RequestLogger:
    """Log HTTP requests and responses."""
    
    def __init__(
        self,
        max_entries: int = 1000,
        log_file: Optional[str] = None,
        enabled: bool = True
    ):
        """
        Initialize request logger.
        
        Args:
            max_entries: Maximum number of entries to keep in memory
            log_file: Optional file path to persist logs
            enabled: Whether logging is enabled
        """
        self.enabled = enabled
        self.max_entries = max_entries
        self.log_file = log_file
        self.entries: deque = deque(maxlen=max_entries)
        self.request_count = 0
        self.error_count = 0
        self.start_time = time.time()
    
    def log_request(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: Any = None,
        query_params: Dict[str, Any] = None
    ) -> int:
        """
        Log an incoming request.
        
        Args:
            method: HTTP method
            path: Request path
            headers: Request headers
            body: Request body
            query_params: Query parameters
            
        Returns:
            Request ID
        """
        if not self.enabled:
            return -1
        
        self.request_count += 1
        request_id = self.request_count
        
        entry = {
            'id': request_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'type': 'request',
            'method': method,
            'path': path,
            'headers': dict(headers),
            'query_params': query_params or {},
            'body': self._truncate_body(body),
            'response': None,
            'duration_ms': None
        }
        
        self.entries.append(entry)
        self._persist_if_needed()
        
        return request_id
    
    def log_response(
        self,
        request_id: int,
        status: int,
        headers: Dict[str, str],
        body: Any = None,
        duration_ms: float = None
    ):
        """
        Log a response.
        
        Args:
            request_id: ID of the corresponding request
            status: HTTP status code
            headers: Response headers
            body: Response body
            duration_ms: Request duration in milliseconds
        """
        if not self.enabled or request_id < 0:
            return
        
        # Find the request entry
        for entry in self.entries:
            if entry['id'] == request_id and entry['type'] == 'request':
                entry['response'] = {
                    'status': status,
                    'headers': dict(headers),
                    'body': self._truncate_body(body)
                }
                entry['duration_ms'] = duration_ms
                
                if status >= 400:
                    self.error_count += 1
                
                self._persist_if_needed()
                break
    
    def _truncate_body(self, body: Any, max_length: int = 10000) -> Any:
        """Truncate body if it's too long."""
        if body is None:
            return None
        
        if isinstance(body, (dict, list)):
            body_str = json.dumps(body)
            if len(body_str) > max_length:
                return body_str[:max_length] + "... [truncated]"
            return body
        
        body_str = str(body)
        if len(body_str) > max_length:
            return body_str[:max_length] + "... [truncated]"
        
        return body
    
    def _persist_if_needed(self):
        """Persist logs to file if configured."""
        if self.log_file:
            try:
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    json.dump(list(self.entries), f, indent=2, default=str)
            except Exception:
                pass  # Fail silently for logging
    
    def get_entries(
        self,
        limit: int = 100,
        method: str = None,
        path_pattern: str = None,
        status_code: int = None
    ) -> List[Dict[str, Any]]:
        """
        Get log entries with optional filtering.
        
        Args:
            limit: Maximum number of entries to return
            method: Filter by HTTP method
            path_pattern: Filter by path pattern (substring match)
            status_code: Filter by response status code
            
        Returns:
            List of log entries
        """
        entries = list(self.entries)
        
        # Apply filters
        if method:
            entries = [e for e in entries if e['method'].upper() == method.upper()]
        
        if path_pattern:
            entries = [e for e in entries if path_pattern in e['path']]
        
        if status_code is not None:
            entries = [
                e for e in entries
                if e.get('response') and e['response'].get('status') == status_code
            ]
        
        # Return most recent first
        return list(reversed(entries[-limit:]))
    
    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific entry by ID.
        
        Args:
            entry_id: Entry ID
            
        Returns:
            Entry or None
        """
        for entry in self.entries:
            if entry['id'] == entry_id:
                return entry
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get logging statistics.
        
        Returns:
            Statistics dictionary
        """
        uptime_seconds = time.time() - self.start_time
        
        # Calculate method distribution
        method_counts = {}
        status_counts = {}
        
        for entry in self.entries:
            method = entry['method']
            method_counts[method] = method_counts.get(method, 0) + 1
            
            if entry.get('response'):
                status = entry['response']['status']
                status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'total_requests': self.request_count,
            'error_count': self.error_count,
            'error_rate': round(self.error_count / max(self.request_count, 1) * 100, 2),
            'uptime_seconds': round(uptime_seconds, 2),
            'requests_per_minute': round(self.request_count / max(uptime_seconds / 60, 1), 2),
            'method_distribution': method_counts,
            'status_distribution': status_counts,
            'entries_in_memory': len(self.entries)
        }
    
    def clear(self):
        """Clear all log entries."""
        self.entries.clear()
        self.request_count = 0
        self.error_count = 0
        self._persist_if_needed()
    
    def export_to_file(self, filepath: str, format: str = 'json') -> bool:
        """
        Export logs to a file.
        
        Args:
            filepath: Output file path
            format: Export format ('json' or 'csv')
            
        Returns:
            True if successful
        """
        try:
            if format == 'json':
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(list(self.entries), f, indent=2, default=str)
            elif format == 'csv':
                import csv
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    if self.entries:
                        writer = csv.DictWriter(f, fieldnames=self.entries[0].keys())
                        writer.writeheader()
                        for entry in self.entries:
                            writer.writerow(entry)
            return True
        except Exception:
            return False
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent error responses (status >= 400).
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of error entries
        """
        errors = [
            e for e in self.entries
            if e.get('response') and e['response'].get('status', 0) >= 400
        ]
        return list(reversed(errors[-limit:]))