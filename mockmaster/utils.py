"""
Utility functions for MockMaster
"""

import re
import json
import random
import string
from datetime import datetime, timezone
from typing import Any, Dict, List, Union


def generate_random_string(length: int = 10) -> str:
    """Generate a random string of specified length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_email() -> str:
    """Generate a random email address."""
    domains = ["example.com", "test.com", "demo.org", "mock.io"]
    username = generate_random_string(8).lower()
    domain = random.choice(domains)
    return f"{username}@{domain}"


def generate_random_uuid() -> str:
    """Generate a random UUID-like string."""
    parts = [
        generate_random_string(8),
        generate_random_string(4),
        generate_random_string(4),
        generate_random_string(4),
        generate_random_string(12)
    ]
    return '-'.join(parts)


def generate_random_date(format_str: str = "%Y-%m-%d") -> str:
    """Generate a random date string."""
    year = random.randint(2020, 2025)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    date_obj = datetime(year, month, day)
    return date_obj.strftime(format_str)


def generate_random_datetime() -> str:
    """Generate a random ISO format datetime."""
    year = random.randint(2020, 2025)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    dt = datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)
    return dt.isoformat()


def generate_random_int(min_val: int = 0, max_val: int = 100) -> int:
    """Generate a random integer."""
    return random.randint(min_val, max_val)


def generate_random_float(min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Generate a random float."""
    return round(random.uniform(min_val, max_val), 2)


def generate_random_bool() -> bool:
    """Generate a random boolean."""
    return random.choice([True, False])


def generate_random_choice(choices: List[Any]) -> Any:
    """Select a random item from choices."""
    return random.choice(choices) if choices else None


def generate_random_lorem(words: int = 10) -> str:
    """Generate random lorem ipsum text."""
    lorem_words = [
        "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit",
        "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore",
        "magna", "aliqua", "ut", "enim", "ad", "minim", "veniam", "quis", "nostrud",
        "exercitation", "ullamco", "laboris", "nisi", "aliquip", "ex", "ea", "commodo",
        "consequat", "duis", "aute", "irure", "in", "reprehenderit", "voluptate",
        "velit", "esse", "cillum", "fugiat", "nulla", "pariatur", "excepteur", "sint",
        "occaecat", "cupidatat", "non", "proident", "sunt", "culpa", "qui", "officia",
        "deserunt", "mollit", "anim", "id", "est", "laborum"
    ]
    return ' '.join(random.choices(lorem_words, k=words))


def parse_content_type(content_type: str) -> str:
    """Parse and normalize content type."""
    if not content_type:
        return "application/json"
    content_type = content_type.lower().split(';')[0].strip()
    return content_type


def is_json_content(content_type: str) -> bool:
    """Check if content type is JSON."""
    return "json" in content_type.lower()


def safe_json_loads(data: str) -> Union[Dict, List, str]:
    """Safely load JSON string."""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return data


def safe_json_dumps(data: Any, indent: int = 2) -> str:
    """Safely dump data to JSON string."""
    try:
        return json.dumps(data, indent=indent, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return str(data)


def match_path_pattern(path: str, pattern: str) -> Union[Dict[str, str], None]:
    """
    Match a path against a pattern with parameters.
    
    Pattern: /users/{id}/posts/{postId}
    Path: /users/123/posts/456
    
    Returns: {"id": "123", "postId": "456"} or None if no match
    """
    # Convert pattern to regex
    param_names = re.findall(r'\{(\w+)\}', pattern)
    regex_pattern = re.sub(r'\{\w+\}', r'([^/]+)', pattern)
    regex_pattern = f'^{regex_pattern}$'
    
    match = re.match(regex_pattern, path)
    if match:
        return dict(zip(param_names, match.groups()))
    return None


def colorize(text: str, color: str) -> str:
    """Add ANSI color codes to text."""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'bold': '\033[1m',
        'reset': '\033[0m'
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


def format_timestamp(dt: datetime = None) -> str:
    """Format datetime to ISO string."""
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.isoformat()


def truncate_string(text: str, max_length: int = 100) -> str:
    """Truncate string to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def parse_query_string(query_string: str) -> Dict[str, Union[str, List[str]]]:
    """Parse query string into dictionary."""
    if not query_string:
        return {}
    
    params = {}
    for param in query_string.split('&'):
        if '=' in param:
            key, value = param.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            if key in params:
                if not isinstance(params[key], list):
                    params[key] = [params[key]]
                params[key].append(value)
            else:
                params[key] = value
    return params


# Template variable generators mapping
TEMPLATE_GENERATORS = {
    'random_string': generate_random_string,
    'random_email': generate_random_email,
    'random_uuid': generate_random_uuid,
    'random_date': generate_random_date,
    'random_datetime': generate_random_datetime,
    'random_int': generate_random_int,
    'random_float': generate_random_float,
    'random_bool': generate_random_bool,
    'random_choice': generate_random_choice,
    'lorem': generate_random_lorem,
    'now': lambda: datetime.now(timezone.utc).isoformat(),
    'today': lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"),
}