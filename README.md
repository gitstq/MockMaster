# MockMaster - API Mock Server Intelligent Manager

🎯 A lightweight CLI tool for rapid API mock server creation, management, and switching.

## Project Overview

MockMaster is a zero-dependency Python CLI tool that helps developers quickly spin up API mock servers for testing and development. It supports YAML/JSON configuration, dynamic route generation, response templating, and intelligent request/response logging.

## Core Features

- 🚀 **Quick Mock Server Creation** - Start a mock server in seconds with simple YAML config
- 🔄 **Multi-Project Management** - Manage multiple mock server profiles
- 📊 **Request/Response Logging** - Built-in HTTP traffic monitoring
- 🎭 **Dynamic Response Templating** - Support for variables, conditions, and random data
- 🔌 **Hot Reload** - Auto-reload on configuration changes
- 📦 **Zero Dependencies** - Pure Python 3.8+, no external packages required
- 🌐 **CORS Support** - Built-in cross-origin handling for frontend development

## Project Structure

```
mockmaster/
├── mockmaster/
│   ├── __init__.py
│   ├── cli.py              # CLI entry point
│   ├── server.py           # HTTP mock server
│   ├── config.py           # Configuration parser
│   ├── templates.py        # Response templating engine
│   ├── storage.py          # Project storage manager
│   ├── logger.py           # Request/response logger
│   └── utils.py            # Utility functions
├── tests/
│   └── test_mockmaster.py
├── examples/
│   └── sample-api.yaml
├── requirements.txt
├── setup.py
├── pyproject.toml
├── LICENSE
└── README.md
```

## Technical Stack

- Python 3.8+
- Built-in http.server (no external HTTP library)
- PyYAML for configuration parsing
- Jinja2-style templating (lightweight implementation)
