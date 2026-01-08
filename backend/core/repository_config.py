"""
backend/core/repository_config.py
=================================

Repository configuration management for template updater.

Stores repository configurations in a JSON file and provides CRUD operations.
Also tracks update history per repository.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from uuid import uuid4

from .telemetry import get_audit_logger


class RepositoryConfigManager:
    """
    Manages repository configurations and update history.
    
    Stores configurations in backend/data/repository_configs.json
    Stores update history in backend/data/repository_update_history.json
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize RepositoryConfigManager.
        
        Args:
            base_path: Base path to project root. If None, auto-detects.
        """
        if base_path is None:
            base_path = Path(__file__).parent.parent.parent
        
        self.base_path = Path(base_path)
        self.data_path = self.base_path / "backend" / "data"
        self.config_file = self.data_path / "repository_configs.json"
        self.history_file = self.data_path / "repository_update_history.json"
        self.audit_logger = get_audit_logger()
        
        # Ensure data directory exists
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize files if they don't exist
        if not self.config_file.exists():
            self._initialize_config_file()
        if not self.history_file.exists():
            self._initialize_history_file()
    
    def _initialize_config_file(self):
        """Initialize repository config file with default repositories."""
        from .template_updater import TemplateUpdater
        updater = TemplateUpdater()
        
        default_config = {
            "repositories": updater.REPOSITORIES,
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat()
        }
        
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
    
    def _initialize_history_file(self):
        """Initialize update history file."""
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump({"history": []}, f, indent=2, ensure_ascii=False)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load repository configurations from file."""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._initialize_config_file()
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save repository configurations to file."""
        config["last_updated"] = datetime.now().isoformat()
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def _load_history(self) -> Dict[str, Any]:
        """Load update history from file."""
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._initialize_history_file()
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
    
    def _save_history(self, history: Dict[str, Any]) -> None:
        """Save update history to file."""
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    
    def list_repositories(self) -> Dict[str, Any]:
        """
        List all configured repositories.
        
        Returns:
            Dictionary with repository configurations
        """
        config = self._load_config()
        return config.get("repositories", {})
    
    def get_repository(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific repository configuration.
        
        Args:
            repo_name: Name of repository
            
        Returns:
            Repository configuration dict or None if not found
        """
        config = self._load_config()
        repositories = config.get("repositories", {})
        return repositories.get(repo_name)
    
    def add_repository(self, repo_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new repository configuration.
        
        Args:
            repo_config: Repository configuration dict with:
                - name: str (required)
                - url: str (required)
                - path: str (required)
                - extraction_script: Optional[str]
                - categories: List[str]
                - license: str
                - source: str
                
        Returns:
            Dictionary with success status and repository name
        """
        config = self._load_config()
        repositories = config.get("repositories", {})
        
        repo_name = repo_config.get("name")
        if not repo_name:
            return {"success": False, "error": "Repository name is required"}
        
        if repo_name in repositories:
            return {"success": False, "error": f"Repository '{repo_name}' already exists"}
        
        # Validate required fields
        required_fields = ["url", "path"]
        for field in required_fields:
            if field not in repo_config or not repo_config[field]:
                return {"success": False, "error": f"Field '{field}' is required"}
        
        # Add repository
        repositories[repo_name] = {
            "url": repo_config["url"],
            "path": repo_config["path"],
            "extraction_script": repo_config.get("extraction_script"),
            "categories": repo_config.get("categories", []),
            "license": repo_config.get("license", "MIT"),
            "source": repo_config.get("source", repo_name)
        }
        
        config["repositories"] = repositories
        self._save_config(config)
        
        # Log action
        self.audit_logger.log_event(
            event_type="repository_added",
            metadata={"repo_name": repo_name, "config": repo_config}
        )
        
        return {"success": True, "repo_name": repo_name}
    
    def update_repository(self, repo_name: str, repo_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing repository configuration.
        
        Args:
            repo_name: Name of repository to update
            repo_config: Updated repository configuration dict
            
        Returns:
            Dictionary with success status
        """
        config = self._load_config()
        repositories = config.get("repositories", {})
        
        if repo_name not in repositories:
            return {"success": False, "error": f"Repository '{repo_name}' not found"}
        
        # Validate required fields
        required_fields = ["url", "path"]
        for field in required_fields:
            if field in repo_config and not repo_config[field]:
                return {"success": False, "error": f"Field '{field}' cannot be empty"}
        
        # Update repository
        if "url" in repo_config:
            repositories[repo_name]["url"] = repo_config["url"]
        if "path" in repo_config:
            repositories[repo_name]["path"] = repo_config["path"]
        if "extraction_script" in repo_config:
            repositories[repo_name]["extraction_script"] = repo_config["extraction_script"]
        if "categories" in repo_config:
            repositories[repo_name]["categories"] = repo_config["categories"]
        if "license" in repo_config:
            repositories[repo_name]["license"] = repo_config["license"]
        if "source" in repo_config:
            repositories[repo_name]["source"] = repo_config["source"]
        
        config["repositories"] = repositories
        self._save_config(config)
        
        # Log action
        self.audit_logger.log_event(
            event_type="repository_updated",
            metadata={"repo_name": repo_name, "config": repo_config}
        )
        
        return {"success": True, "repo_name": repo_name}
    
    def delete_repository(self, repo_name: str) -> Dict[str, Any]:
        """
        Delete a repository configuration.
        
        Args:
            repo_name: Name of repository to delete
            
        Returns:
            Dictionary with success status
        """
        config = self._load_config()
        repositories = config.get("repositories", {})
        
        if repo_name not in repositories:
            return {"success": False, "error": f"Repository '{repo_name}' not found"}
        
        del repositories[repo_name]
        config["repositories"] = repositories
        self._save_config(config)
        
        # Log action
        self.audit_logger.log_event(
            event_type="repository_deleted",
            metadata={"repo_name": repo_name}
        )
        
        return {"success": True, "repo_name": repo_name}
    
    def add_update_history(
        self,
        repo_name: str,
        templates_added: int,
        templates_updated: int,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """
        Add an entry to update history.
        
        Args:
            repo_name: Name of repository
            templates_added: Number of templates added
            templates_updated: Number of templates updated
            success: Whether update was successful
            error: Error message if update failed
        """
        history = self._load_history()
        history_entries = history.get("history", [])
        
        history_entries.append({
            "id": str(uuid4()),
            "repository": repo_name,
            "timestamp": datetime.now().isoformat(),
            "templates_added": templates_added,
            "templates_updated": templates_updated,
            "success": success,
            "error": error
        })
        
        # Keep only last 1000 entries
        history_entries = history_entries[-1000:]
        
        history["history"] = history_entries
        self._save_history(history)
    
    def get_update_history(
        self,
        repo_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get update history for repositories.
        
        Args:
            repo_name: Optional repository name to filter by
            limit: Maximum number of entries to return
            
        Returns:
            List of update history entries
        """
        history = self._load_history()
        history_entries = history.get("history", [])
        
        # Filter by repository if specified
        if repo_name:
            history_entries = [
                entry for entry in history_entries
                if entry.get("repository") == repo_name
            ]
        
        # Sort by timestamp (newest first) and limit
        history_entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return history_entries[:limit]


# Singleton instance
_repository_config_manager_instance: Optional[RepositoryConfigManager] = None


def get_repository_config_manager() -> RepositoryConfigManager:
    """
    Get singleton RepositoryConfigManager instance.
    
    Returns:
        Cached RepositoryConfigManager instance
    """
    global _repository_config_manager_instance
    if _repository_config_manager_instance is None:
        _repository_config_manager_instance = RepositoryConfigManager()
    return _repository_config_manager_instance
