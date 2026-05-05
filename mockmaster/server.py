"""
HTTP Mock Server for MockMaster
Zero-dependency HTTP server using Python's built-in http.server
"""

import json
import time
import signal
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict, List, Optional, Callable
from urllib.parse import urlparse, parse_qs

from .config import ConfigParser
from .templates import ResponseBuilder, get_template
from .logger import RequestLogger
from .utils import (
    parse_content_type, is_json_content, safe_json_loads, safe_json_dumps,
    parse_query_string, colorize
)


class MockRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for mock server."""
    
    # Class-level attributes set by MockServer
    config: ConfigParser = None
    response_builder: ResponseBuilder = None
    logger: RequestLogger = None
    cors_enabled: bool = True
    
    def log_message(self, format: str, *args):
        """Suppress default logging - we use our own logger."""
        pass
    
    def do_GET(self):
        self._handle_request('GET')
    
    def do_POST(self):
        self._handle_request('POST')
    
    def do_PUT(self):
        self._handle_request('PUT')
    
    def do_DELETE(self):
        self._handle_request('DELETE')
    
    def do_PATCH(self):
        self._handle_request('PATCH')
    
    def do_OPTIONS(self):
        self._handle_request('OPTIONS')
    
    def do_HEAD(self):
        self._handle_request('HEAD')
    
    def _handle_request(self, method: str):
        """Handle incoming HTTP request."""
        start_time = time.time()
        
        # Parse URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_string = parsed_url.query
        query_params = parse_qs(query_string)
        
        # Flatten query params (convert single-item lists to values)
        query_params = {
            k: v[0] if len(v) == 1 else v
            for k, v in query_params.items()
        }
        
        # Read headers
        headers = dict(self.headers)
        
        # Read body
        body = None
        content_length = self.headers.get('Content-Length')
        if content_length:
            try:
                content_length = int(content_length)
                body_data = self.rfile.read(content_length)
                content_type = self.headers.get('Content-Type', '')
                
                if is_json_content(content_type):
                    body = safe_json_loads(body_data.decode('utf-8'))
                else:
                    body = body_data.decode('utf-8')
            except Exception:
                body = None
        
        # Log request
        request_id = -1
        if self.logger:
            request_id = self.logger.log_request(
                method=method,
                path=path,
                headers=headers,
                body=body,
                query_params=query_params
            )
        
        # Find matching route
        route = self.config.find_route(method, path) if self.config else None
        
        if route:
            # Get response configuration
            response_config = route.get('response', {})
            
            # Get path parameters
            path_params = route.get('_path_params', {})
            
            # Build response
            response = self.response_builder.build_response(
                response_config=response_config,
                path_params=path_params,
                query_params=query_params,
                request_body=body,
                request_headers=headers
            )
            
            # Apply delay if configured
            delay = self.response_builder.build_delay(response_config)
            if delay > 0:
                time.sleep(delay)
        else:
            # Return 404
            response = self.response_builder.build_error_response(
                status=404,
                message=f"Route not found: {method} {path}",
                error_code="ROUTE_NOT_FOUND"
            )
        
        # Send response
        self._send_response(response)
        
        # Log response
        if self.logger and request_id >= 0:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_response(
                request_id=request_id,
                status=response['status'],
                headers=response.get('headers', {}),
                body=response.get('body'),
                duration_ms=duration_ms
            )
    
    def _send_response(self, response: Dict[str, Any]):
        """Send HTTP response."""
        status = response.get('status', 200)
        headers = response.get('headers', {})
        body = response.get('body')
        
        # Send status
        self.send_response(status)
        
        # Send CORS headers if enabled
        if self.cors_enabled:
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        
        # Send custom headers
        for header, value in headers.items():
            self.send_header(header, value)
        
        self.end_headers()
        
        # Send body
        if body is not None:
            if isinstance(body, (dict, list)):
                body = safe_json_dumps(body)
            if isinstance(body, str):
                body = body.encode('utf-8')
            self.wfile.write(body)


class MockServer:
    """Mock HTTP server manager."""
    
    def __init__(
        self,
        config_path: str,
        host: str = 'localhost',
        port: int = None,
        cors_enabled: bool = True,
        log_requests: bool = True,
        max_log_entries: int = 1000
    ):
        """
        Initialize mock server.
        
        Args:
            config_path: Path to configuration file
            host: Server host
            port: Server port (overrides config)
            cors_enabled: Enable CORS headers
            log_requests: Enable request logging
            max_log_entries: Maximum log entries to keep
        """
        self.config_path = config_path
        self.config = ConfigParser(config_path)
        
        # Validate configuration
        errors = self.config.validate()
        if errors:
            raise ValueError(f"Configuration errors:\n" + "\n".join(errors))
        
        # Get server settings
        self.host = host or self.config.get_host()
        self.port = port or self.config.get_port()
        self.cors_enabled = cors_enabled
        
        # Initialize components
        self.response_builder = ResponseBuilder()
        self.logger = RequestLogger(
            max_entries=max_log_entries,
            enabled=log_requests
        )
        
        # Set up request handler class
        MockRequestHandler.config = self.config
        MockRequestHandler.response_builder = self.response_builder
        MockRequestHandler.logger = self.logger
        MockRequestHandler.cors_enabled = self.cors_enabled
        
        # Server instance
        self.server: Optional[HTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.is_running = False
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n{colorize('Received signal, shutting down...', 'yellow')}")
        self.stop()
    
    def start(self, blocking: bool = True):
        """
        Start the mock server.
        
        Args:
            blocking: If True, block until server stops
        """
        if self.is_running:
            print(colorize("Server is already running", 'yellow'))
            return
        
        try:
            self.server = HTTPServer((self.host, self.port), MockRequestHandler)
            self.is_running = True
            
            print(colorize(f"🚀 MockServer started on http://{self.host}:{self.port}", 'green'))
            print(colorize(f"📁 Config: {self.config_path}", 'cyan'))
            print(colorize(f"📝 Logging: {'enabled' if self.logger.enabled else 'disabled'}", 'cyan'))
            print(colorize(f"🌐 CORS: {'enabled' if self.cors_enabled else 'disabled'}", 'cyan'))
            print(colorize("\nPress Ctrl+C to stop\n", 'yellow'))
            
            if blocking:
                self.server.serve_forever()
            else:
                self.server_thread = threading.Thread(target=self.server.serve_forever)
                self.server_thread.daemon = True
                self.server_thread.start()
                
        except OSError as e:
            print(colorize(f"❌ Failed to start server: {e}", 'red'))
            self.is_running = False
            raise
    
    def stop(self):
        """Stop the mock server."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        
        print(colorize("\n✅ Server stopped", 'green'))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        return {
            'is_running': self.is_running,
            'host': self.host,
            'port': self.port,
            'config_path': self.config_path,
            'routes_count': len(self.config.get_routes()),
            'logging': self.logger.get_stats() if self.logger else None
        }
    
    def get_logs(self, limit: int = 100, **filters) -> List[Dict[str, Any]]:
        """Get request logs."""
        if self.logger:
            return self.logger.get_entries(limit=limit, **filters)
        return []
    
    def clear_logs(self):
        """Clear request logs."""
        if self.logger:
            self.logger.clear()