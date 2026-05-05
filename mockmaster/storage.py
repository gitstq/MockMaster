"""
Project storage manager for MockMaster
Handles saving, loading, and managing mock server projects
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


class ProjectStorage:
    """Manage mock server projects and their configurations."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize project storage.
        
        Args:
            storage_dir: Directory to store projects. Defaults to ~/.mockmaster
        """
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = Path.home() / '.mockmaster'
        
        self.projects_file = self.storage_dir / 'projects.json'
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Ensure storage directory exists."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Create projects file if it doesn't exist
        if not self.projects_file.exists():
            self._save_projects({})
    
    def _load_projects(self) -> Dict[str, Any]:
        """Load projects from storage."""
        try:
            with open(self.projects_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_projects(self, projects: Dict[str, Any]):
        """Save projects to storage."""
        with open(self.projects_file, 'w', encoding='utf-8') as f:
            json.dump(projects, f, indent=2, ensure_ascii=False, default=str)
    
    def create_project(
        self,
        name: str,
        config_path: str,
        description: str = "",
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new project.
        
        Args:
            name: Project name
            config_path: Path to configuration file
            description: Project description
            tags: List of tags
            
        Returns:
            Project information
        """
        projects = self._load_projects()
        
        if name in projects:
            raise ValueError(f"Project '{name}' already exists")
        
        project = {
            'name': name,
            'config_path': str(config_path),
            'description': description,
            'tags': tags or [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'last_used': None,
            'use_count': 0
        }
        
        projects[name] = project
        self._save_projects(projects)
        
        return project
    
    def get_project(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get project by name.
        
        Args:
            name: Project name
            
        Returns:
            Project information or None
        """
        projects = self._load_projects()
        return projects.get(name)
    
    def update_project(self, name: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Update project information.
        
        Args:
            name: Project name
            **kwargs: Fields to update
            
        Returns:
            Updated project information or None
        """
        projects = self._load_projects()
        
        if name not in projects:
            return None
        
        # Update allowed fields
        allowed_fields = ['description', 'tags', 'config_path']
        for field in allowed_fields:
            if field in kwargs:
                projects[name][field] = kwargs[field]
        
        projects[name]['updated_at'] = datetime.now().isoformat()
        self._save_projects(projects)
        
        return projects[name]
    
    def delete_project(self, name: str) -> bool:
        """
        Delete a project.
        
        Args:
            name: Project name
            
        Returns:
            True if deleted, False if not found
        """
        projects = self._load_projects()
        
        if name not in projects:
            return False
        
        del projects[name]
        self._save_projects(projects)
        
        return True
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all projects.
        
        Returns:
            List of project information
        """
        projects = self._load_projects()
        return list(projects.values())
    
    def search_projects(self, query: str) -> List[Dict[str, Any]]:
        """
        Search projects by name, description, or tags.
        
        Args:
            query: Search query
            
        Returns:
            List of matching projects
        """
        projects = self._load_projects()
        query_lower = query.lower()
        
        results = []
        for project in projects.values():
            if (query_lower in project['name'].lower() or
                query_lower in project.get('description', '').lower() or
                any(query_lower in tag.lower() for tag in project.get('tags', []))):
                results.append(project)
        
        return results
    
    def record_usage(self, name: str):
        """
        Record that a project was used.
        
        Args:
            name: Project name
        """
        projects = self._load_projects()
        
        if name in projects:
            projects[name]['last_used'] = datetime.now().isoformat()
            projects[name]['use_count'] = projects[name].get('use_count', 0) + 1
            self._save_projects(projects)
    
    def get_recent_projects(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recently used projects.
        
        Args:
            limit: Maximum number of projects to return
            
        Returns:
            List of recently used projects
        """
        projects = self._load_projects()
        
        # Filter projects with last_used and sort by it
        used_projects = [
            p for p in projects.values()
            if p.get('last_used')
        ]
        used_projects.sort(key=lambda p: p['last_used'], reverse=True)
        
        return used_projects[:limit]
    
    def get_most_used_projects(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get most frequently used projects.
        
        Args:
            limit: Maximum number of projects to return
            
        Returns:
            List of most used projects
        """
        projects = self._load_projects()
        
        sorted_projects = sorted(
            projects.values(),
            key=lambda p: p.get('use_count', 0),
            reverse=True
        )
        
        return sorted_projects[:limit]
    
    def export_project(self, name: str, export_path: str) -> bool:
        """
        Export a project to a file.
        
        Args:
            name: Project name
            export_path: Path to export to
            
        Returns:
            True if exported successfully
        """
        project = self.get_project(name)
        if not project:
            return False
        
        # Load config file
        config_path = Path(project['config_path'])
        if not config_path.exists():
            return False
        
        export_data = {
            'project': project,
            'config': config_path.read_text(encoding='utf-8')
        }
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return True
    
    def import_project(self, import_path: str, new_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Import a project from a file.
        
        Args:
            import_path: Path to import from
            new_name: Optional new name for the project
            
        Returns:
            Imported project information or None
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None
        
        project = data.get('project')
        config_content = data.get('config')
        
        if not project or not config_content:
            return None
        
        # Save config file
        name = new_name or project['name']
        config_filename = f"{name}.yaml"
        config_path = self.storage_dir / config_filename
        
        # Handle duplicate names
        counter = 1
        original_name = name
        while config_path.exists() or self.get_project(name):
            name = f"{original_name}_{counter}"
            config_filename = f"{name}.yaml"
            config_path = self.storage_dir / config_filename
            counter += 1
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        # Create project
        return self.create_project(
            name=name,
            config_path=str(config_path),
            description=project.get('description', ''),
            tags=project.get('tags', [])
        )
    
    def duplicate_project(self, name: str, new_name: str) -> Optional[Dict[str, Any]]:
        """
        Duplicate an existing project.
        
        Args:
            name: Source project name
            new_name: New project name
            
        Returns:
            New project information or None
        """
        project = self.get_project(name)
        if not project:
            return None
        
        # Copy config file
        source_config = Path(project['config_path'])
        if not source_config.exists():
            return None
        
        new_config_path = self.storage_dir / f"{new_name}.yaml"
        
        # Handle duplicate names
        counter = 1
        original_new_name = new_name
        while new_config_path.exists() or self.get_project(new_name):
            new_name = f"{original_new_name}_{counter}"
            new_config_path = self.storage_dir / f"{new_name}.yaml"
            counter += 1
        
        # Copy config content
        config_content = source_config.read_text(encoding='utf-8')
        with open(new_config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        # Create new project
        return self.create_project(
            name=new_name,
            config_path=str(new_config_path),
            description=f"Copy of {name}: {project.get('description', '')}",
            tags=project.get('tags', []).copy()
        )