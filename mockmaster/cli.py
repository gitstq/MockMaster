#!/usr/bin/env python3
"""
MockMaster CLI - API Mock Server Intelligent Manager

A lightweight CLI tool for rapid API mock server creation, management, and switching.
Zero dependencies, pure Python 3.8+ implementation.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional

from . import __version__, __title__, __description__
from .server import MockServer
from .storage import ProjectStorage
from .config import ConfigParser
from .utils import colorize


def print_banner():
    """Print application banner."""
    banner = f"""
{colorize('╔══════════════════════════════════════════════════════════╗', 'cyan')}
{colorize('║', 'cyan')}  {colorize('🎯 MockMaster', 'bold')} - API Mock Server Intelligent Manager  {colorize('║', 'cyan')}
{colorize('║', 'cyan')}  {colorize(f'v{__version__}', 'yellow')} - Zero-dependency, pure Python 3.8+         {colorize('║', 'cyan')}
{colorize('╚══════════════════════════════════════════════════════════╝', 'cyan')}
"""
    print(banner)


def cmd_start(args):
    """Start mock server command."""
    config_path = args.config or args.project
    
    # If project name provided, look it up
    if args.project and not args.config:
        storage = ProjectStorage()
        project = storage.get_project(args.project)
        if not project:
            print(colorize(f"❌ Project '{args.project}' not found", 'red'))
            print(f"Run '{colorize('mockmaster list', 'cyan')}' to see available projects")
            return 1
        config_path = project['config_path']
        storage.record_usage(args.project)
    
    if not config_path:
        print(colorize("❌ Configuration file or project name required", 'red'))
        print(f"Usage: mockmaster start --config <file.yaml> OR mockmaster start --project <name>")
        return 1
    
    if not Path(config_path).exists():
        print(colorize(f"❌ Configuration file not found: {config_path}", 'red'))
        return 1
    
    try:
        server = MockServer(
            config_path=config_path,
            host=args.host,
            port=args.port,
            cors_enabled=not args.no_cors,
            log_requests=not args.no_log
        )
        server.start(blocking=True)
        return 0
    except ValueError as e:
        print(colorize(f"❌ Configuration error: {e}", 'red'))
        return 1
    except Exception as e:
        print(colorize(f"❌ Server error: {e}", 'red'))
        return 1


def cmd_create(args):
    """Create new project command."""
    storage = ProjectStorage()
    
    # Check if project already exists
    if storage.get_project(args.name):
        print(colorize(f"❌ Project '{args.name}' already exists", 'red'))
        return 1
    
    # Create config file if it doesn't exist
    config_path = args.config or f"{args.name}.yaml"
    config_path = Path(config_path).resolve()
    
    if not config_path.exists():
        # Create sample configuration
        sample_config = f'''# MockMaster Configuration for {args.name}
# Generated automatically

server:
  port: {args.port or 8080}
  host: localhost
  cors:
    enabled: true
  logging:
    enabled: true
    level: info

routes:
  - path: /
    methods: [GET]
    response:
      status: 200
      headers:
        Content-Type: application/json
      body:
        message: "Welcome to {args.name} Mock API"
        version: "1.0.0"
  
  - path: /health
    methods: [GET]
    response:
      status: 200
      headers:
        Content-Type: application/json
      body:
        status: "healthy"
        timestamp: "{{{{ now() }}}}"
  
  - path: /api/users
    methods: [GET]
    response:
      status: 200
      headers:
        Content-Type: application/json
      body:
        users:
          - id: "{{{{ random_uuid() }}}}"
            name: "John Doe"
            email: "{{{{ random_email() }}}}"
          - id: "{{{{ random_uuid() }}}}"
            name: "Jane Smith"
            email: "{{{{ random_email() }}}}"
  
  - path: /api/users/{{id}}
    methods: [GET]
    response:
      status: 200
      headers:
        Content-Type: application/json
      body:
        id: "{{{{ id }}}}"
        name: "{{{{ random_choice(['Alice', 'Bob', 'Charlie', 'Diana']) }}}}"
        email: "{{{{ random_email() }}}}"
        created_at: "{{{{ random_datetime() }}}}"
  
  - path: /api/users
    methods: [POST]
    response:
      status: 201
      headers:
        Content-Type: application/json
      body:
        id: "{{{{ random_uuid() }}}}"
        message: "User created successfully"
        created_at: "{{{{ now() }}}}"
  
  - path: /api/error
    methods: [GET]
    response:
      status: 500
      headers:
        Content-Type: application/json
      body:
        error:
          code: "INTERNAL_ERROR"
          message: "Something went wrong"
'''
        config_path.write_text(sample_config, encoding='utf-8')
        print(colorize(f"✅ Created configuration file: {config_path}", 'green'))
    
    # Create project
    try:
        project = storage.create_project(
            name=args.name,
            config_path=str(config_path),
            description=args.description or "",
            tags=args.tags or []
        )
        print(colorize(f"✅ Created project: {args.name}", 'green'))
        print(f"\nTo start the server:")
        print(f"  {colorize(f'mockmaster start --project {args.name}', 'cyan')}")
        print(f"  {colorize(f'mockmaster start --config {config_path}', 'cyan')}")
        return 0
    except ValueError as e:
        print(colorize(f"❌ {e}", 'red'))
        return 1


def cmd_list(args):
    """List projects command."""
    storage = ProjectStorage()
    projects = storage.list_projects()
    
    if not projects:
        print(colorize("No projects found. Create one with:", 'yellow'))
        print(f"  {colorize('mockmaster create --name <project-name>', 'cyan')}")
        return 0
    
    print(colorize(f"\n📁 Projects ({len(projects)} total):\n", 'bold'))
    
    for project in projects:
        name = project['name']
        description = project.get('description', '')
        tags = project.get('tags', [])
        use_count = project.get('use_count', 0)
        last_used = project.get('last_used')
        
        print(f"  {colorize('•', 'cyan')} {colorize(name, 'bold')}")
        if description:
            print(f"    {description}")
        if tags:
            print(f"    Tags: {', '.join(tags)}")
        print(f"    Used: {use_count} times" + (f" (last: {last_used[:10]})" if last_used else ""))
        print()
    
    return 0


def cmd_show(args):
    """Show project details command."""
    storage = ProjectStorage()
    project = storage.get_project(args.name)
    
    if not project:
        print(colorize(f"❌ Project '{args.name}' not found", 'red'))
        return 1
    
    print(colorize(f"\n📁 Project: {project['name']}\n", 'bold'))
    print(f"  Description: {project.get('description') or 'N/A'}")
    print(f"  Config file: {project['config_path']}")
    print(f"  Tags: {', '.join(project.get('tags', [])) or 'None'}")
    print(f"  Created: {project['created_at']}")
    print(f"  Updated: {project['updated_at']}")
    print(f"  Last used: {project.get('last_used') or 'Never'}")
    print(f"  Use count: {project.get('use_count', 0)}")
    
    # Show routes if config exists
    config_path = Path(project['config_path'])
    if config_path.exists():
        try:
            config = ConfigParser(str(config_path))
            routes = config.get_routes()
            print(f"\n  Routes ({len(routes)}):")
            for route in routes:
                methods = route.get('methods', ['GET'])
                if isinstance(methods, str):
                    methods = [methods]
                path = route.get('path', '/')
                status = route.get('response', {}).get('status', 200)
                print(f"    {colorize(','.join(methods), 'yellow'):<10} {path:<30} → {status}")
        except Exception as e:
            print(f"\n  ⚠️  Could not parse config: {e}")
    
    print()
    return 0


def cmd_delete(args):
    """Delete project command."""
    storage = ProjectStorage()
    
    if not storage.get_project(args.name):
        print(colorize(f"❌ Project '{args.name}' not found", 'red'))
        return 1
    
    if args.yes:
        confirm = 'y'
    else:
        confirm = input(f"Delete project '{args.name}'? [y/N]: ").lower()
    
    if confirm == 'y':
        if storage.delete_project(args.name):
            print(colorize(f"✅ Deleted project: {args.name}", 'green'))
            return 0
        else:
            print(colorize(f"❌ Failed to delete project", 'red'))
            return 1
    else:
        print("Cancelled")
        return 0


def cmd_validate(args):
    """Validate configuration file command."""
    config_path = args.config
    
    if not Path(config_path).exists():
        print(colorize(f"❌ Configuration file not found: {config_path}", 'red'))
        return 1
    
    try:
        config = ConfigParser(config_path)
        errors = config.validate()
        
        if errors:
            print(colorize(f"❌ Validation failed for: {config_path}", 'red'))
            for error in errors:
                print(f"  • {error}")
            return 1
        else:
            print(colorize(f"✅ Configuration is valid: {config_path}", 'green'))
            
            # Show summary
            server = config.get_server_config()
            routes = config.get_routes()
            
            print(f"\nServer configuration:")
            print(f"  Host: {config.get_host()}")
            print(f"  Port: {config.get_port()}")
            print(f"  CORS: {config.get_cors_config().get('enabled', True)}")
            
            print(f"\nRoutes ({len(routes)}):")
            for route in routes:
                methods = route.get('methods', ['GET'])
                if isinstance(methods, str):
                    methods = [methods]
                path = route.get('path', '/')
                status = route.get('response', {}).get('status', 200)
                print(f"  {colorize(','.join(methods), 'yellow'):<10} {path:<30} → {status}")
            
            return 0
    except Exception as e:
        print(colorize(f"❌ Error parsing configuration: {e}", 'red'))
        return 1


def cmd_export(args):
    """Export project command."""
    storage = ProjectStorage()
    
    if not storage.get_project(args.name):
        print(colorize(f"❌ Project '{args.name}' not found", 'red'))
        return 1
    
    export_path = args.output or f"{args.name}.json"
    
    if storage.export_project(args.name, export_path):
        print(colorize(f"✅ Exported project to: {export_path}", 'green'))
        return 0
    else:
        print(colorize(f"❌ Failed to export project", 'red'))
        return 1


def cmd_import(args):
    """Import project command."""
    storage = ProjectStorage()
    
    if not Path(args.file).exists():
        print(colorize(f"❌ Import file not found: {args.file}", 'red'))
        return 1
    
    project = storage.import_project(args.file, args.name)
    
    if project:
        print(colorize(f"✅ Imported project: {project['name']}", 'green'))
        return 0
    else:
        print(colorize(f"❌ Failed to import project", 'red'))
        return 1


def cmd_duplicate(args):
    """Duplicate project command."""
    storage = ProjectStorage()
    
    if not storage.get_project(args.source):
        print(colorize(f"❌ Source project '{args.source}' not found", 'red'))
        return 1
    
    project = storage.duplicate_project(args.source, args.name)
    
    if project:
        print(colorize(f"✅ Duplicated project: {args.source} → {project['name']}", 'green'))
        return 0
    else:
        print(colorize(f"❌ Failed to duplicate project", 'red'))
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog='mockmaster',
        description=f'{__title__} - {__description__}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mockmaster create --name my-api --port 3000
  mockmaster start --project my-api
  mockmaster start --config ./api.yaml --port 8080
  mockmaster list
  mockmaster show my-api
  mockmaster validate ./api.yaml
        """
    )
    
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start mock server')
    start_parser.add_argument('--config', '-c', help='Configuration file path')
    start_parser.add_argument('--project', '-p', help='Project name')
    start_parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    start_parser.add_argument('--port', '-P', type=int, help='Server port')
    start_parser.add_argument('--no-cors', action='store_true', help='Disable CORS')
    start_parser.add_argument('--no-log', action='store_true', help='Disable request logging')
    start_parser.set_defaults(func=cmd_start)
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create new project')
    create_parser.add_argument('--name', '-n', required=True, help='Project name')
    create_parser.add_argument('--config', '-c', help='Configuration file path')
    create_parser.add_argument('--port', '-P', type=int, help='Default server port')
    create_parser.add_argument('--description', '-d', help='Project description')
    create_parser.add_argument('--tags', '-t', nargs='+', help='Project tags')
    create_parser.set_defaults(func=cmd_create)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all projects')
    list_parser.set_defaults(func=cmd_list)
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show project details')
    show_parser.add_argument('name', help='Project name')
    show_parser.set_defaults(func=cmd_show)
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete project')
    delete_parser.add_argument('name', help='Project name')
    delete_parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation')
    delete_parser.set_defaults(func=cmd_delete)
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate configuration file')
    validate_parser.add_argument('config', help='Configuration file path')
    validate_parser.set_defaults(func=cmd_validate)
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export project')
    export_parser.add_argument('name', help='Project name')
    export_parser.add_argument('--output', '-o', help='Output file path')
    export_parser.set_defaults(func=cmd_export)
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import project')
    import_parser.add_argument('file', help='Import file path')
    import_parser.add_argument('--name', '-n', help='New project name')
    import_parser.set_defaults(func=cmd_import)
    
    # Duplicate command
    duplicate_parser = subparsers.add_parser('duplicate', help='Duplicate project')
    duplicate_parser.add_argument('source', help='Source project name')
    duplicate_parser.add_argument('name', help='New project name')
    duplicate_parser.set_defaults(func=cmd_duplicate)
    
    args = parser.parse_args(argv)
    
    if args.command is None:
        print_banner()
        parser.print_help()
        return 0
    
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print(colorize("\n\n⚠️  Interrupted by user", 'yellow'))
        return 130
    except Exception as e:
        print(colorize(f"\n❌ Error: {e}", 'red'))
        return 1


if __name__ == '__main__':
    sys.exit(main())