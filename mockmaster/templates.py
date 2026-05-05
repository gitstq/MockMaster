"""
Response templating engine for MockMaster
Supports variable substitution and dynamic content generation
"""

import re
import json
import random
from typing import Any, Dict, List, Union
from .utils import TEMPLATE_GENERATORS, safe_json_dumps


class TemplateEngine:
    """Simple template engine for dynamic response generation."""
    
    def __init__(self):
        self.pattern = re.compile(r'\{\{\s*(\w+)(?:\(([^)]*)\))?\s*\}\}')
    
    def render(self, template: Union[str, Dict, List], context: Dict[str, Any] = None) -> Union[str, Dict, List]:
        """
        Render a template with variable substitution.
        
        Args:
            template: Template string, dict, or list
            context: Additional context variables
            
        Returns:
            Rendered template
        """
        if context is None:
            context = {}
        
        if isinstance(template, str):
            return self._render_string(template, context)
        elif isinstance(template, dict):
            return {key: self.render(value, context) for key, value in template.items()}
        elif isinstance(template, list):
            return [self.render(item, context) for item in template]
        else:
            return template
    
    def _render_string(self, template: str, context: Dict[str, Any]) -> str:
        """Render a string template."""
        def replace_match(match):
            func_name = match.group(1)
            args_str = match.group(2)
            
            # Check context first
            if func_name in context:
                return str(context[func_name])
            
            # Check template generators
            if func_name in TEMPLATE_GENERATORS:
                generator = TEMPLATE_GENERATORS[func_name]
                try:
                    if args_str:
                        # Parse arguments
                        args = self._parse_args(args_str)
                        return str(generator(*args))
                    else:
                        return str(generator())
                except Exception:
                    return match.group(0)
            
            # Return original if not found
            return match.group(0)
        
        return self.pattern.sub(replace_match, template)
    
    def _parse_args(self, args_str: str) -> List[Any]:
        """Parse function arguments from string."""
        args = []
        for arg in args_str.split(','):
            arg = arg.strip()
            # Try to parse as int
            try:
                args.append(int(arg))
                continue
            except ValueError:
                pass
            # Try to parse as float
            try:
                args.append(float(arg))
                continue
            except ValueError:
                pass
            # Treat as string (remove quotes if present)
            if (arg.startswith('"') and arg.endswith('"')) or \
               (arg.startswith("'") and arg.endswith("'")):
                arg = arg[1:-1]
            args.append(arg)
        return args


class ResponseBuilder:
    """Build HTTP responses with templating support."""
    
    def __init__(self):
        self.template_engine = TemplateEngine()
    
    def build_response(
        self,
        response_config: Dict[str, Any],
        path_params: Dict[str, str] = None,
        query_params: Dict[str, Any] = None,
        request_body: Any = None,
        request_headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Build a response based on configuration.
        
        Args:
            response_config: Response configuration from YAML
            path_params: URL path parameters
            query_params: URL query parameters
            request_body: Request body data
            request_headers: Request headers
            
        Returns:
            Response dict with status, headers, and body
        """
        # Build context
        context = {
            'path_params': path_params or {},
            'query_params': query_params or {},
            'request_body': request_body or {},
            'request_headers': request_headers or {},
        }
        
        # Add path params directly to context for easy access
        context.update(path_params or {})
        
        # Get status code
        status = response_config.get('status', 200)
        
        # Get headers
        headers = response_config.get('headers', {})
        headers = self.template_engine.render(headers, context)
        
        # Ensure Content-Type is set
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
        
        # Get body
        body = response_config.get('body')
        if body is not None:
            body = self.template_engine.render(body, context)
            
            # Convert dict/list to JSON string if needed
            if isinstance(body, (dict, list)):
                body = safe_json_dumps(body)
        
        return {
            'status': status,
            'headers': headers,
            'body': body
        }
    
    def build_error_response(
        self,
        status: int = 500,
        message: str = "Internal Server Error",
        error_code: str = None
    ) -> Dict[str, Any]:
        """Build an error response."""
        body = {
            'error': {
                'code': error_code or f"ERR_{status}",
                'message': message,
                'status': status
            }
        }
        
        return {
            'status': status,
            'headers': {'Content-Type': 'application/json'},
            'body': safe_json_dumps(body)
        }
    
    def build_delay(self, response_config: Dict[str, Any]) -> float:
        """Extract delay from response config."""
        delay = response_config.get('delay', 0)
        if isinstance(delay, dict):
            # Random delay between min and max
            min_delay = delay.get('min', 0)
            max_delay = delay.get('max', min_delay)
            return random.uniform(min_delay, max_delay)
        return float(delay)


# Common response templates
COMMON_TEMPLATES = {
    'success': {
        'status': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': {'success': True, 'message': 'Operation completed successfully'}
    },
    'created': {
        'status': 201,
        'headers': {'Content-Type': 'application/json'},
        'body': {'success': True, 'message': 'Resource created successfully', 'id': '{{ random_uuid() }}'}
    },
    'bad_request': {
        'status': 400,
        'headers': {'Content-Type': 'application/json'},
        'body': {'error': {'code': 'BAD_REQUEST', 'message': 'Invalid request parameters'}}
    },
    'unauthorized': {
        'status': 401,
        'headers': {'Content-Type': 'application/json'},
        'body': {'error': {'code': 'UNAUTHORIZED', 'message': 'Authentication required'}}
    },
    'forbidden': {
        'status': 403,
        'headers': {'Content-Type': 'application/json'},
        'body': {'error': {'code': 'FORBIDDEN', 'message': 'Access denied'}}
    },
    'not_found': {
        'status': 404,
        'headers': {'Content-Type': 'application/json'},
        'body': {'error': {'code': 'NOT_FOUND', 'message': 'Resource not found'}}
    },
    'validation_error': {
        'status': 422,
        'headers': {'Content-Type': 'application/json'},
        'body': {'error': {'code': 'VALIDATION_ERROR', 'message': 'Validation failed', 'errors': []}}
    },
    'server_error': {
        'status': 500,
        'headers': {'Content-Type': 'application/json'},
        'body': {'error': {'code': 'INTERNAL_ERROR', 'message': 'Internal server error'}}
    }
}


def get_template(name: str) -> Dict[str, Any]:
    """Get a common response template by name."""
    return COMMON_TEMPLATES.get(name, COMMON_TEMPLATES['success']).copy()