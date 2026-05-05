"""
Configuration parser for MockMaster
Supports YAML and JSON configuration files
"""

import os
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class ConfigParser:
    """Parse mock server configuration from YAML or JSON files."""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        content = self.config_path.read_text(encoding='utf-8')
        
        # Try JSON first (more reliable), then YAML
        if self.config_path.suffix == '.json':
            self.config = json.loads(content)
        elif self.config_path.suffix in ['.yaml', '.yml']:
            self.config = self._parse_yaml(content)
        else:
            # Try JSON first, fallback to YAML
            try:
                self.config = json.loads(content)
            except json.JSONDecodeError:
                self.config = self._parse_yaml(content)
    
    def _parse_yaml(self, content: str) -> Dict[str, Any]:
        """
        Parse YAML content to Python dict.
        This is a simplified YAML parser that handles the most common constructs.
        For complex YAML, users should use JSON format instead.
        """
        lines = content.split('\n')
        result = {}
        
        # Stack of (container, indent_level)
        stack = [(result, -1)]
        pending_list_key = None
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Skip empty lines and comments
            stripped = line.lstrip()
            if not stripped or stripped.startswith('#'):
                i += 1
                continue
            
            indent = len(line) - len(stripped)
            
            # Pop stack until we find the right parent
            while len(stack) > 1 and stack[-1][1] >= indent:
                stack.pop()
            
            current_container, current_indent = stack[-1]
            
            # Handle list items
            if stripped.startswith('- '):
                item_content = stripped[2:].strip()
                
                # If we have a pending list key, add the list to parent first
                if pending_list_key and isinstance(current_container, dict):
                    if pending_list_key not in current_container:
                        current_container[pending_list_key] = []
                    current_list = current_container[pending_list_key]
                elif isinstance(current_container, list):
                    current_list = current_container
                else:
                    # Create a new list
                    current_list = []
                    if isinstance(current_container, dict):
                        # Use a default key
                        current_container['_items'] = current_list
                
                # Check if item_content contains a key-value pair
                if ':' in item_content and not item_content.startswith('{'):
                    key, value = self._split_key_value(item_content)
                    if value == '':
                        # This is a nested object in the list
                        new_obj = {}
                        current_list.append(new_obj)
                        stack.append((new_obj, indent))
                    else:
                        # Simple key-value in list item
                        current_list.append({key: self._parse_value(value)})
                else:
                    # Simple value
                    current_list.append(self._parse_value(item_content))
                
                pending_list_key = None
            
            # Handle key-value pairs
            elif ':' in stripped:
                key, value = self._split_key_value(stripped)
                
                if value == '':
                    # Look ahead to determine if this is a list or dict
                    next_is_list = False
                    next_indent = indent
                    
                    for j in range(i + 1, len(lines)):
                        next_line = lines[j]
                        next_stripped = next_line.lstrip()
                        
                        if not next_stripped or next_stripped.startswith('#'):
                            continue
                        
                        next_indent = len(next_line) - len(next_stripped)
                        
                        if next_stripped.startswith('- '):
                            next_is_list = True
                        break
                    
                    if next_is_list:
                        # Mark this key as pending a list
                        pending_list_key = key
                        # Don't add to container yet
                    else:
                        # This key holds a dict
                        new_dict = {}
                        current_container[key] = new_dict
                        stack.append((new_dict, indent))
                        pending_list_key = None
                else:
                    current_container[key] = self._parse_value(value)
                    pending_list_key = None
            
            i += 1
        
        return result
    
    def _split_key_value(self, line: str) -> tuple:
        """Split a line into key and value."""
        # Handle quoted keys
        if line.startswith('"'):
            end_quote = line.find('"', 1)
            if end_quote != -1 and line[end_quote + 1:].lstrip().startswith(':'):
                key = line[1:end_quote]
                value = line[end_quote + 2:].strip()
                return key, value
        elif line.startswith("'"):
            end_quote = line.find("'", 1)
            if end_quote != -1 and line[end_quote + 1:].lstrip().startswith(':'):
                key = line[1:end_quote]
                value = line[end_quote + 2:].strip()
                return key, value
        
        # Standard key: value
        colon_pos = line.find(':')
        key = line[:colon_pos].strip()
        value = line[colon_pos + 1:].strip()
        return key, value
    
    def _parse_value(self, value: str) -> Any:
        """Parse a YAML value to appropriate Python type."""
        value = value.strip()
        
        # Handle quoted strings
        if len(value) >= 2:
            if (value[0] == '"' and value[-1] == '"') or \
               (value[0] == "'" and value[-1] == "'"):
                return value[1:-1]
        
        # Handle null
        if value.lower() in ['null', '~', '']:
            return None
        
        # Handle booleans
        if value.lower() in ['true', 'yes', 'on']:
            return True
        if value.lower() in ['false', 'no', 'off']:
            return False
        
        # Handle inline arrays [a, b, c]
        if value.startswith('[') and value.endswith(']'):
            inner = value[1:-1]
            if not inner.strip():
                return []
            items = []
            for item in inner.split(','):
                items.append(self._parse_value(item.strip()))
            return items
        
        # Handle inline objects {a: 1, b: 2}
        if value.startswith('{') and value.endswith('}'):
            inner = value[1:-1]
            if not inner.strip():
                return {}
            result = {}
            for pair in inner.split(','):
                if ':' in pair:
                    k, v = pair.split(':', 1)
                    result[k.strip()] = self._parse_value(v.strip())
            return result
        
        # Handle integers
        try:
            return int(value)
        except ValueError:
            pass
        
        # Handle floats
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration."""
        return self.config.get('server', {})
    
    def get_routes(self) -> List[Dict[str, Any]]:
        """Get route definitions."""
        return self.config.get('routes', [])
    
    def get_middleware(self) -> List[Dict[str, Any]]:
        """Get middleware configuration."""
        return self.config.get('middleware', [])
    
    def get_port(self) -> int:
        """Get server port."""
        server = self.get_server_config()
        return server.get('port', 8080)
    
    def get_host(self) -> str:
        """Get server host."""
        server = self.get_server_config()
        return server.get('host', 'localhost')
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration."""
        server = self.get_server_config()
        return server.get('cors', {'enabled': True})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        server = self.get_server_config()
        return server.get('logging', {'enabled': True, 'level': 'info'})
    
    def find_route(self, method: str, path: str) -> Optional[Dict[str, Any]]:
        """
        Find a matching route for the given method and path.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            
        Returns:
            Route configuration or None
        """
        from .utils import match_path_pattern
        
        routes = self.get_routes()
        for route in routes:
            route_methods = route.get('methods', ['GET'])
            if isinstance(route_methods, str):
                route_methods = [route_methods]
            
            if method.upper() not in [m.upper() for m in route_methods]:
                continue
            
            route_path = route.get('path', '')
            
            # Exact match
            if route_path == path:
                return route
            
            # Pattern match with parameters
            if '{' in route_path:
                params = match_path_pattern(path, route_path)
                if params is not None:
                    route_copy = route.copy()
                    route_copy['_path_params'] = params
                    return route_copy
        
        return None
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        # Check required fields
        if 'routes' not in self.config:
            errors.append("Missing required field: 'routes'")
        elif not isinstance(self.config['routes'], list):
            errors.append("'routes' must be a list")
        else:
            # Validate each route
            for i, route in enumerate(self.config['routes']):
                if not isinstance(route, dict):
                    errors.append(f"Route {i} must be an object")
                    continue
                
                if 'path' not in route:
                    errors.append(f"Route {i} missing required field: 'path'")
                
                if 'response' not in route:
                    errors.append(f"Route {i} missing required field: 'response'")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Return the full configuration as a dictionary."""
        return self.config.copy()