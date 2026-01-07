"""
backend/core/template_updater.py
=================================

Automatic template updater for jailbreak templates from external repositories.

This module provides functionality to:
- Update external repositories (PyRIT, L1B3RT4S, LLAMATOR, Model-Inversion-Attack-ToolBox)
- Extract templates from updated repositories
- Merge templates into advanced_payloads.json
- Create backups before updates
- Schedule automatic updates

References:
- PyRIT: https://github.com/Azure/PyRIT
- L1B3RT4S: https://github.com/elder-plinius/L1B3RT4S
- LLAMATOR: https://github.com/LLAMATOR-Core/llamator
- Model-Inversion-Attack-ToolBox: https://github.com/ffhibnese/Model-Inversion-Attack-ToolBox
"""

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from uuid import UUID

from .telemetry import get_audit_logger


class TemplateUpdater:
    """
    Automatic updater for jailbreak templates from external repositories.
    
    This class manages:
    - Repository synchronization (git pull)
    - Template extraction from updated repos
    - Merging templates into advanced_payloads.json
    - Backup creation before updates
    - Update logging and telemetry
    
    Example:
        >>> updater = TemplateUpdater()
        >>> result = await updater.update_all_repositories()
        >>> print(f"Updated {result['templates_added']} templates")
    """
    
    # Repository configurations
    REPOSITORIES = {
        "PyRIT": {
            "url": "https://github.com/Azure/PyRIT.git",
            "path": "PyRIT",
            "extraction_script": "scripts/extract_pyrit_templates.py",
            "categories": [
                "jailbreak_dan", "jailbreak_aim", "jailbreak_dude",
                "jailbreak_developer_mode", "many_shot_jailbreak",
                "crescendo_attack", "skeleton_key", "research_pre_jailbreak"
            ],
            "license": "MIT",
            "source": "PyRIT"
        },
        "L1B3RT4S": {
            "url": "https://github.com/elder-plinius/L1B3RT4S.git",
            "path": "L1B3RT4S",
            "extraction_script": "scripts/extract_l1b3rt4s_prompts.py",
            "categories": [
                "obfuscation_unicode", "obfuscation_leetspeak",
                "obfuscation_token_smuggling", "obfuscation_morse",
                "obfuscation_binary", "jailbreak_developer_mode"
            ],
            "license": "MIT",
            "source": "L1B3RT4S"
        },
        "LLAMATOR": {
            "url": "https://github.com/LLAMATOR-Core/llamator.git",
            "path": "llamator",
            "extraction_script": None,  # Manual extraction or future script
            "categories": [
                "rag_poisoning", "rag_bypass", "virtualization",
                "direct_injection", "indirect_injection"
            ],
            "license": "CC BY-NC-SA 4.0",
            "source": "LLAMATOR"
        },
        "Model-Inversion-Attack-ToolBox": {
            "url": "https://github.com/ffhibnese/Model-Inversion-Attack-ToolBox.git",
            "path": "Model-Inversion-Attack-ToolBox",
            "extraction_script": None,  # Manual extraction or future script
            "categories": [
                "system_prompt_extraction", "gradient_based"
            ],
            "license": "MIT",
            "source": "Model-Inversion-Attack-ToolBox"
        }
    }
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize TemplateUpdater.
        
        Args:
            base_path: Base path to project root. If None, auto-detects from script location.
        """
        if base_path is None:
            # Auto-detect: go up from core to app root
            # In container: /app/core/template_updater.py -> /app
            # In local dev: backend/core/template_updater.py -> project root
            file_path = Path(__file__).resolve()
            if file_path.parts[-3] == "backend" and file_path.parts[-2] == "core":
                # Local development: go up 3 levels
                base_path = file_path.parent.parent.parent
            else:
                # Container: go up 2 levels (core -> app)
                base_path = file_path.parent.parent
        
        self.base_path = Path(base_path)
        self.data_path = self.base_path / "backend" / "data"
        self.scripts_path = self.base_path / "backend" / "scripts"
        self.advanced_payloads_file = self.data_path / "advanced_payloads.json"
        self.audit_logger = get_audit_logger()
        
        # Load repositories from config file (if exists) or use defaults
        self._load_repositories()
    
    def _load_repositories(self) -> None:
        """
        Load repository configurations from config file or use defaults.
        
        If repository_configs.json exists, loads from there.
        Otherwise, uses hardcoded REPOSITORIES.
        """
        try:
            from .repository_config import get_repository_config_manager
            config_manager = get_repository_config_manager()
            config_repos = config_manager.list_repositories()
            
            if config_repos:
                # Merge with defaults (config file takes precedence)
                self.REPOSITORIES = {**self.REPOSITORIES, **config_repos}
        except Exception:
            # If config manager fails, use defaults
            pass
    
    def _backup_file(self, file_path: Path) -> Path:
        """
        Create a timestamped backup of a file.
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            Path to backup file
        """
        if not file_path.exists():
            return file_path
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.parent / f"{file_path.stem}.backup.{timestamp}{file_path.suffix}"
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def restore_from_backup(self, backup_path: str) -> Dict[str, Any]:
        """
        Restore advanced_payloads.json from a backup file.
        
        Args:
            backup_path: Path to backup file to restore from
            
        Returns:
            Dictionary with restore results
        """
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            return {
                "success": False,
                "error": f"Backup file not found: {backup_path}"
            }
        
        try:
            # Create backup of current file before restoring
            if self.advanced_payloads_file.exists():
                current_backup = self._backup_file(self.advanced_payloads_file)
            else:
                current_backup = None
            
            # Restore from backup
            shutil.copy2(backup_file, self.advanced_payloads_file)
            
            # Log restore action
            self.audit_logger.log_event(
                event_type="template_restore",
                metadata={
                    "backup_path": str(backup_path),
                    "current_backup": str(current_backup) if current_backup else None
                }
            )
            
            return {
                "success": True,
                "message": f"Successfully restored from backup: {backup_path}",
                "backup_used": str(backup_path),
                "current_backup": str(current_backup) if current_backup else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error restoring from backup: {str(e)}"
            }
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backup files.
        
        Returns:
            List of backup file information dictionaries
        """
        backups = []
        backup_pattern = f"{self.advanced_payloads_file.stem}.backup.*{self.advanced_payloads_file.suffix}"
        
        for backup_file in self.data_path.glob(backup_pattern):
            try:
                stat = backup_file.stat()
                backups.append({
                    "path": str(backup_file),
                    "filename": backup_file.name,
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "timestamp": backup_file.stem.split('.backup.')[-1] if '.backup.' in backup_file.stem else None
                })
            except Exception:
                continue
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x["created_at"], reverse=True)
        return backups
    
    def _update_repository(self, repo_name: str, repo_config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Update a single repository using git pull.
        
        Args:
            repo_name: Name of repository
            repo_config: Repository configuration dict
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        repo_path = self.base_path / repo_config["path"]
        
        if not repo_path.exists():
            # Clone repository if it doesn't exist
            try:
                subprocess.run(
                    ["git", "clone", repo_config["url"], str(repo_path)],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                return True, f"Cloned {repo_name} repository"
            except subprocess.TimeoutExpired:
                return False, f"Timeout cloning {repo_name}"
            except subprocess.CalledProcessError as e:
                return False, f"Error cloning {repo_name}: {e.stderr}"
            except FileNotFoundError:
                return False, "git command not found - install git to update repositories"
        
        # Update existing repository
        try:
            # Check if it's a git repository
            git_dir = repo_path / ".git"
            if not git_dir.exists():
                return False, f"{repo_name} directory exists but is not a git repository"
            
            # Pull latest changes
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=repo_path,
                check=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Check if there were updates
            if "Already up to date" in result.stdout:
                return True, f"{repo_name} already up to date"
            else:
                return True, f"{repo_name} updated successfully"
                
        except subprocess.TimeoutExpired:
            return False, f"Timeout updating {repo_name}"
        except subprocess.CalledProcessError as e:
            return False, f"Error updating {repo_name}: {e.stderr}"
        except FileNotFoundError:
            return False, "git command not found"
    
    def _extract_templates(self, repo_name: str, repo_config: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """
        Extract templates from a repository using extraction script.
        
        Args:
            repo_name: Name of repository
            repo_config: Repository configuration dict
            
        Returns:
            Tuple of (success: bool, extracted_data: dict, message: str)
        """
        extraction_script = repo_config.get("extraction_script")
        
        if not extraction_script:
            # Return a more helpful error message with available repositories
            available_repos = ", ".join([name for name, config in self.REPOSITORIES.items() if config.get("extraction_script")])
            return False, {}, f"No extraction script configured for {repo_name}. Repositories with extraction scripts: {available_repos if available_repos else 'None'}. Please implement an extraction script or use a different repository."
        
        script_path = self.base_path / extraction_script
        
        if not script_path.exists():
            return False, {}, f"Extraction script not found: {script_path}"
        
        try:
            # Run extraction script
            result = subprocess.run(
                ["python3", str(script_path)],
                cwd=self.base_path,
                check=True,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            # Scripts write to files, not stdout - check for output files
            # PyRIT writes to pyrit_extracted.json, L1B3RT4S to l1b3rt4s_extracted.json
            # Check both possible filenames
            possible_files = {
                "PyRIT": [
                    self.data_path / "pyrit_extracted.json",
                    self.data_path / "pyrit_templates_extracted.json"
                ],
                "L1B3RT4S": [
                    self.data_path / "l1b3rt4s_extracted.json"
                ]
            }
            
            # Try to find output file
            output_file = None
            if repo_name in possible_files:
                for file_path in possible_files[repo_name]:
                    if file_path.exists():
                        output_file = file_path
                        break
            
            if output_file and output_file.exists():
                # Read extracted JSON file
                with open(output_file, "r", encoding="utf-8") as f:
                    extracted_data = json.load(f)
                return True, extracted_data, f"Extracted templates from {repo_name}"
            else:
                # Try parsing stdout as fallback
                try:
                    if result.stdout.strip():
                        extracted_data = json.loads(result.stdout)
                        return True, extracted_data, f"Extracted templates from {repo_name} (from stdout)"
                except json.JSONDecodeError:
                    pass
                
                checked_files = [str(f) for f in possible_files.get(repo_name, [])]
                return False, {}, f"Extraction script output not found for {repo_name}. Checked: {', '.join(checked_files) if checked_files else 'N/A'}"
                
        except subprocess.TimeoutExpired:
            return False, {}, f"Timeout extracting templates from {repo_name}"
        except subprocess.CalledProcessError as e:
            return False, {}, f"Error extracting templates from {repo_name}: {e.stderr}"
        except FileNotFoundError:
            return False, {}, "python3 command not found"
    
    def _merge_templates(
        self,
        extracted_data: Dict[str, Any],
        repo_config: Dict[str, Any]
    ) -> Tuple[int, int]:
        """
        Merge extracted templates into advanced_payloads.json.
        
        Args:
            extracted_data: Extracted templates dict (category -> templates)
            repo_config: Repository configuration dict
            
        Returns:
            Tuple of (templates_added: int, templates_updated: int)
        """
        # Load existing advanced_payloads.json
        if self.advanced_payloads_file.exists():
            with open(self.advanced_payloads_file, "r", encoding="utf-8") as f:
                advanced_data = json.load(f)
        else:
            advanced_data = {
                "version": "2.1.0",
                "source": repo_config["source"],
                "last_updated": datetime.now().isoformat(),
            }
        
        templates_added = 0
        templates_updated = 0
        
        # Merge extracted templates
        # Extracted data structure: { category: { description, severity, source, templates: [...] } }
        for category, category_data in extracted_data.items():
            if category in ["version", "source", "last_updated"]:
                continue  # Skip metadata
            
            # Extract templates list from category_data
            if isinstance(category_data, dict) and "templates" in category_data:
                new_templates = category_data["templates"]
                category_description = category_data.get("description", f"{repo_config['source']} templates")
                category_severity = category_data.get("severity", "medium")
            elif isinstance(category_data, list):
                # Direct list of templates (fallback)
                new_templates = category_data
                category_description = f"{repo_config['source']} templates"
                category_severity = "medium"
            else:
                continue  # Skip malformed categories
            
            if category not in advanced_data:
                # New category
                advanced_data[category] = {
                    "description": category_description,
                    "severity": category_severity,
                    "templates": new_templates if isinstance(new_templates, list) else [new_templates],
                    "source": repo_config["source"],
                    "license": repo_config["license"],
                    "last_updated": datetime.now().isoformat()
                }
                templates_added += len(advanced_data[category]["templates"])
            else:
                # Existing category - merge templates
                existing_templates = set(advanced_data[category].get("templates", []))
                new_templates_list = new_templates if isinstance(new_templates, list) else [new_templates]
                
                for template in new_templates_list:
                    if template not in existing_templates:
                        advanced_data[category]["templates"].append(template)
                        templates_added += 1
                    else:
                        templates_updated += 1
                
                # Update metadata
                advanced_data[category]["last_updated"] = datetime.now().isoformat()
                # Update description if it's more specific
                if category_description and category_description != advanced_data[category].get("description"):
                    advanced_data[category]["description"] = category_description
                if "source" not in advanced_data[category] or repo_config["source"] not in advanced_data[category].get("source", ""):
                    sources = advanced_data[category].get("source", "").split(", ")
                    if repo_config["source"] not in sources:
                        sources.append(repo_config["source"])
                        advanced_data[category]["source"] = ", ".join(sources)
        
        # Update global metadata
        advanced_data["last_updated"] = datetime.now().isoformat()
        if repo_config["source"] not in advanced_data.get("source", ""):
            sources = advanced_data.get("source", "").split(", ")
            if repo_config["source"] not in sources:
                sources.append(repo_config["source"])
                advanced_data["source"] = ", ".join(sources)
        
        # Save merged data
        with open(self.advanced_payloads_file, "w", encoding="utf-8") as f:
            json.dump(advanced_data, f, indent=2, ensure_ascii=False)
        
        return templates_added, templates_updated
    
    async def update_repository(
        self,
        repo_name: str,
        create_backup: bool = True
    ) -> Dict[str, Any]:
        """
        Update a single repository and merge templates.
        
        Args:
            repo_name: Name of repository to update
            create_backup: Whether to create backup before update
            
        Returns:
            Dictionary with update results:
            - success: bool
            - repo_name: str
            - update_message: str
            - extraction_message: str
            - templates_added: int
            - templates_updated: int
            - backup_path: Optional[str]
        """
        if repo_name not in self.REPOSITORIES:
            return {
                "success": False,
                "repo_name": repo_name,
                "error": f"Unknown repository: {repo_name}"
            }
        
        repo_config = self.REPOSITORIES[repo_name]
        result = {
            "success": False,
            "repo_name": repo_name,
            "update_message": "",
            "extraction_message": "",
            "templates_added": 0,
            "templates_updated": 0,
            "backup_path": None
        }
        
        # Create backup if requested
        if create_backup and self.advanced_payloads_file.exists():
            backup_path = self._backup_file(self.advanced_payloads_file)
            result["backup_path"] = str(backup_path)
        
        # Update repository
        update_success, update_message = self._update_repository(repo_name, repo_config)
        result["update_message"] = update_message
        
        if not update_success:
            result["error"] = update_message
            # Log failed update to history
            try:
                from .repository_config import get_repository_config_manager
                config_manager = get_repository_config_manager()
                config_manager.add_update_history(
                    repo_name=repo_name,
                    templates_added=0,
                    templates_updated=0,
                    success=False,
                    error=update_message
                )
            except Exception:
                pass
            return result
        
        # Extract templates
        extract_success, extracted_data, extract_message = self._extract_templates(repo_name, repo_config)
        result["extraction_message"] = extract_message
        
        if not extract_success:
            result["error"] = extract_message
            # Log failed extraction to history
            try:
                from .repository_config import get_repository_config_manager
                config_manager = get_repository_config_manager()
                config_manager.add_update_history(
                    repo_name=repo_name,
                    templates_added=0,
                    templates_updated=0,
                    success=False,
                    error=extract_message
                )
            except Exception:
                pass
            return result
        
        # Merge templates
        templates_added, templates_updated = self._merge_templates(extracted_data, repo_config)
        result["templates_added"] = templates_added
        result["templates_updated"] = templates_updated
        result["success"] = True
        
        # Log to telemetry
        self.audit_logger.log_event(
            event_type="template_update",
            metadata={
                "repo_name": repo_name,
                "templates_added": templates_added,
                "templates_updated": templates_updated,
                "update_message": update_message,
                "extraction_message": extract_message
            }
        )
        
        # Add to update history
        try:
            from .repository_config import get_repository_config_manager
            config_manager = get_repository_config_manager()
            config_manager.add_update_history(
                repo_name=repo_name,
                templates_added=templates_added,
                templates_updated=templates_updated,
                success=result["success"],
                error=result.get("error")
            )
        except Exception:
            pass  # History logging is optional
        
        return result
    
    async def update_all_repositories(
        self,
        create_backup: bool = True
    ) -> Dict[str, Any]:
        """
        Update all repositories and merge templates.
        
        Args:
            create_backup: Whether to create backup before update
            
        Returns:
            Dictionary with overall results:
            - success: bool
            - total_templates_added: int
            - total_templates_updated: int
            - repositories: List[Dict] (individual repo results)
            - backup_path: Optional[str]
        """
        # Create single backup for all updates
        backup_path = None
        if create_backup and self.advanced_payloads_file.exists():
            backup_path = self._backup_file(self.advanced_payloads_file)
        
        results = {
            "success": True,
            "total_templates_added": 0,
            "total_templates_updated": 0,
            "repositories": [],
            "backup_path": str(backup_path) if backup_path else None,
            "started_at": datetime.now().isoformat()
        }
        
        # Update each repository
        for repo_name in self.REPOSITORIES.keys():
            repo_result = await self.update_repository(repo_name, create_backup=False)
            results["repositories"].append(repo_result)
            
            if repo_result.get("success"):
                results["total_templates_added"] += repo_result.get("templates_added", 0)
                results["total_templates_updated"] += repo_result.get("templates_updated", 0)
            else:
                results["success"] = False  # At least one failed
        
        results["completed_at"] = datetime.now().isoformat()
        
        # Log overall update
        self.audit_logger.log_event(
            event_type="template_update_all",
            metadata=results
        )
        
        # Add to update history for each repository
        try:
            from .repository_config import get_repository_config_manager
            config_manager = get_repository_config_manager()
            for repo_result in results["repositories"]:
                config_manager.add_update_history(
                    repo_name=repo_result.get("repo_name", ""),
                    templates_added=repo_result.get("templates_added", 0),
                    templates_updated=repo_result.get("templates_updated", 0),
                    success=repo_result.get("success", False),
                    error=repo_result.get("error")
                )
        except Exception:
            pass  # History logging is optional
        
        return results
    
    def get_update_status(self) -> Dict[str, Any]:
        """
        Get status of repositories (last update, commit hash, etc.).
        
        Returns:
            Dictionary with repository status information
        """
        status = {
            "repositories": {}
        }
        
        for repo_name, repo_config in self.REPOSITORIES.items():
            repo_path = self.base_path / repo_config["path"]
            repo_status = {
                "exists": repo_path.exists(),
                "is_git": (repo_path / ".git").exists() if repo_path.exists() else False,
                "last_commit": None,
                "last_commit_date": None,
                "branch": None
            }
            
            if repo_status["is_git"]:
                try:
                    # Get last commit hash
                    result = subprocess.run(
                        ["git", "rev-parse", "HEAD"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        repo_status["last_commit"] = result.stdout.strip()
                    
                    # Get last commit date
                    result = subprocess.run(
                        ["git", "log", "-1", "--format=%ci"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        repo_status["last_commit_date"] = result.stdout.strip()
                    
                    # Get current branch
                    result = subprocess.run(
                        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        repo_status["branch"] = result.stdout.strip()
                        
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                    pass  # Git commands failed, status already set
            
            status["repositories"][repo_name] = repo_status
        
        return status


# Singleton instance
_template_updater_instance: Optional[TemplateUpdater] = None


def get_template_updater() -> TemplateUpdater:
    """
    Get singleton TemplateUpdater instance.
    
    Returns:
        Cached TemplateUpdater instance
    """
    global _template_updater_instance
    if _template_updater_instance is None:
        _template_updater_instance = TemplateUpdater()
    return _template_updater_instance
