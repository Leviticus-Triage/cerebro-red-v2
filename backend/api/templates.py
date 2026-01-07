"""
backend/api/templates.py
========================

Experiment template CRUD operations for CEREBRO-RED v2 API.
Allows saving/loading experiment configurations as reusable templates.
Also provides endpoints for updating jailbreak templates from external repositories.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session, ExperimentTemplateRepository
from core.models import (
    ExperimentTemplateCreate, 
    ExperimentTemplateUpdate, 
    ExperimentTemplateResponse,
    ExperimentTemplateListResponse,
    ExperimentConfig
)
from core.template_updater import get_template_updater
from api.auth import verify_api_key
from api.responses import api_response
import json

router = APIRouter()


# ============================================================================
# Helper Functions
# ============================================================================

def db_to_response(db_template) -> ExperimentTemplateResponse:
    """Convert DB model to response model."""
    # Deserialize config_json back to ExperimentConfig
    config_dict = json.loads(db_template.config_json)
    config = ExperimentConfig(**config_dict)
    
    return ExperimentTemplateResponse(
        template_id=db_template.template_id,
        name=db_template.name,
        description=db_template.description,
        config=config,
        tags=db_template.tags,
        is_public=db_template.is_public,
        created_by=db_template.created_by,
        created_at=db_template.created_at,
        updated_at=db_template.updated_at,
        usage_count=db_template.usage_count
    )


# ============================================================================
# Endpoints
# ============================================================================

# IMPORTANT: Jailbreak routes must come BEFORE parametrized routes like /{template_id}
# FastAPI matches routes in order, so /jailbreak must come before /{template_id}

# ============================================================================
# Jailbreak Template Update Endpoints (MUST BE FIRST)
# ============================================================================

@router.post("/jailbreak/update", dependencies=[Depends(verify_api_key)])
async def update_jailbreak_templates(
    repository: Optional[str] = Query(None, description="Specific repository to update (PyRIT, L1B3RT4S, LLAMATOR, Model-Inversion-Attack-ToolBox). If None, updates all."),
    create_backup: bool = Query(True, description="Create backup before update")
):
    """
    Update jailbreak templates from external repositories.
    
    This endpoint:
    - Updates specified repository (or all repositories if none specified)
    - Extracts templates from updated repositories
    - Merges templates into advanced_payloads.json
    - Creates backup before update (if create_backup=True)
    
    Args:
        repository: Optional repository name to update. If None, updates all.
        create_backup: Whether to create backup before update
        
    Returns:
        Update results with templates added/updated counts
    """
    from core.template_updater import get_template_updater
    
    updater = get_template_updater()
    
    try:
        if repository:
            # Update single repository
            if repository not in updater.REPOSITORIES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unknown repository: {repository}. Available: {', '.join(updater.REPOSITORIES.keys())}"
                )
            
            result = await updater.update_repository(repository, create_backup=create_backup)
            
            if not result.get("success"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result.get("error", "Update failed")
                )
            
            return api_response({
                "message": f"Successfully updated {repository}",
                "repository": repository,
                "templates_added": result["templates_added"],
                "templates_updated": result["templates_updated"],
                "backup_path": result.get("backup_path"),
                "update_message": result["update_message"],
                "extraction_message": result["extraction_message"]
            })
        else:
            # Update all repositories
            result = await updater.update_all_repositories(create_backup=create_backup)
            
            if not result.get("success"):
                # Some repositories may have failed
                failed_repos = [r["repo_name"] for r in result["repositories"] if not r.get("success")]
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Some repositories failed to update: {', '.join(failed_repos)}"
                )
            
            return api_response({
                "message": "Successfully updated all repositories",
                "total_templates_added": result["total_templates_added"],
                "total_templates_updated": result["total_templates_updated"],
                "backup_path": result.get("backup_path"),
                "repositories": result["repositories"],
                "started_at": result["started_at"],
                "completed_at": result["completed_at"]
            })
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating templates: {str(e)}"
        )


@router.get("/jailbreak/status", dependencies=[Depends(verify_api_key)])
async def get_jailbreak_template_status():
    """
    Get status of external repositories (last update, commit hash, etc.).
    
    Returns:
        Repository status information including:
        - Repository existence
        - Last commit hash
        - Last commit date
        - Current branch
    """
    from core.template_updater import get_template_updater
    
    updater = get_template_updater()
    
    try:
        status_info = updater.get_update_status()
        return api_response(status_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting repository status: {str(e)}"
        )


@router.get("/jailbreak/repositories", dependencies=[Depends(verify_api_key)])
async def list_template_repositories():
    """
    List all configured template repositories.
    
    Returns:
        Dictionary with all repository configurations
    """
    from core.repository_config import get_repository_config_manager
    
    config_manager = get_repository_config_manager()
    
    try:
        repositories = config_manager.list_repositories()
        return api_response({
            "repositories": repositories,
            "total": len(repositories)
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing repositories: {str(e)}"
        )


@router.get("/jailbreak/repositories/{repo_name}", dependencies=[Depends(verify_api_key)])
async def get_template_repository(repo_name: str):
    """
    Get a specific repository configuration.
    
    Args:
        repo_name: Name of repository
        
    Returns:
        Repository configuration
    """
    from core.repository_config import get_repository_config_manager
    
    config_manager = get_repository_config_manager()
    
    try:
        repo = config_manager.get_repository(repo_name)
        if not repo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository '{repo_name}' not found"
            )
        return api_response({"name": repo_name, **repo})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting repository: {str(e)}"
        )


@router.post("/jailbreak/repositories", dependencies=[Depends(verify_api_key)])
async def add_template_repository(repo_config: Dict[str, Any]):
    """
    Add a new repository configuration.
    
    Args:
        repo_config: Repository configuration with:
            - name: str (required)
            - url: str (required)
            - path: str (required)
            - extraction_script: Optional[str]
            - categories: List[str]
            - license: str
            - source: str
            
    Returns:
        Success status and repository name
    """
    from core.repository_config import get_repository_config_manager
    
    config_manager = get_repository_config_manager()
    
    try:
        result = config_manager.add_repository(repo_config)
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to add repository")
            )
        
        # Reload repositories in TemplateUpdater
        from core.template_updater import get_template_updater
        updater = get_template_updater()
        updater._load_repositories()
        
        return api_response(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding repository: {str(e)}"
        )


@router.put("/jailbreak/repositories/{repo_name}", dependencies=[Depends(verify_api_key)])
async def update_template_repository(repo_name: str, repo_config: Dict[str, Any]):
    """
    Update an existing repository configuration.
    
    Args:
        repo_name: Name of repository to update
        repo_config: Updated repository configuration
        
    Returns:
        Success status
    """
    from core.repository_config import get_repository_config_manager
    
    config_manager = get_repository_config_manager()
    
    try:
        result = config_manager.update_repository(repo_name, repo_config)
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to update repository")
            )
        
        # Reload repositories in TemplateUpdater
        from core.template_updater import get_template_updater
        updater = get_template_updater()
        updater._load_repositories()
        
        return api_response(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating repository: {str(e)}"
        )


@router.delete("/jailbreak/repositories/{repo_name}", dependencies=[Depends(verify_api_key)])
async def delete_template_repository(repo_name: str):
    """
    Delete a repository configuration.
    
    Args:
        repo_name: Name of repository to delete
        
    Returns:
        Success status
    """
    from core.repository_config import get_repository_config_manager
    
    config_manager = get_repository_config_manager()
    
    try:
        result = config_manager.delete_repository(repo_name)
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Repository not found")
            )
        
        # Reload repositories in TemplateUpdater
        from core.template_updater import get_template_updater
        updater = get_template_updater()
        updater._load_repositories()
        
        return api_response(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting repository: {str(e)}"
        )


@router.get("/jailbreak/repositories/{repo_name}/history", dependencies=[Depends(verify_api_key)])
async def get_repository_update_history(
    repo_name: str,
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Get update history for a specific repository.
    
    Args:
        repo_name: Name of repository
        limit: Maximum number of entries to return
        
    Returns:
        List of update history entries
    """
    from core.repository_config import get_repository_config_manager
    
    config_manager = get_repository_config_manager()
    
    try:
        history = config_manager.get_update_history(repo_name=repo_name, limit=limit)
        return api_response({
            "repository": repo_name,
            "history": history,
            "total": len(history)
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting update history: {str(e)}"
        )


# ============================================================================
# Jailbreak Template CRUD Endpoints
# ============================================================================

@router.get("/jailbreak", dependencies=[Depends(verify_api_key)])
async def list_jailbreak_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in template content")
):
    """
    List all jailbreak templates from advanced_payloads.json.
    
    Returns:
        Dictionary with categories and their templates
    """
    from core.payloads import get_payload_manager
    from pathlib import Path
    import json
    
    try:
        # Load advanced_payloads.json directly
        data_path = Path(__file__).parent.parent / "data" / "advanced_payloads.json"
        
        if not data_path.exists():
            return api_response({
                "categories": {},
                "total_templates": 0,
                "total_categories": 0
            })
        
        with open(data_path, "r", encoding="utf-8") as f:
            payloads_data = json.load(f)
        
        # Filter by category if specified
        categories = {}
        for cat_name, cat_data in payloads_data.items():
            if cat_name in ["version", "source", "last_updated"]:
                continue
            
            # Apply category filter
            if category and cat_name != category:
                continue
            
            # Apply search filter
            if search:
                search_lower = search.lower()
                templates = cat_data.get("templates", [])
                filtered_templates = [
                    t for t in templates
                    if search_lower in t.lower() or search_lower in cat_data.get("description", "").lower()
                ]
                if not filtered_templates:
                    continue
                cat_data = {**cat_data, "templates": filtered_templates}
            
            categories[cat_name] = cat_data
        
        # Calculate totals
        total_templates = sum(len(cat.get("templates", [])) for cat in categories.values())
        
        return api_response({
            "categories": categories,
            "total_templates": total_templates,
            "total_categories": len(categories),
            "version": payloads_data.get("version"),
            "last_updated": payloads_data.get("last_updated")
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading jailbreak templates: {str(e)}"
        )


# IMPORTANT: Specific routes must come BEFORE parametrized routes
# FastAPI matches routes in order, so /jailbreak/categories must come before /jailbreak/{category}

@router.get("/jailbreak/categories", dependencies=[Depends(verify_api_key)])
async def list_jailbreak_categories():
    """
    List all jailbreak template categories.
    
    Returns:
        List of category names with metadata
    """
    from pathlib import Path
    import json
    
    try:
        data_path = Path(__file__).parent.parent / "data" / "advanced_payloads.json"
        
        if not data_path.exists():
            return api_response({"categories": []})
        
        with open(data_path, "r", encoding="utf-8") as f:
            payloads_data = json.load(f)
        
        categories = []
        for cat_name, cat_data in payloads_data.items():
            if cat_name in ["version", "source", "last_updated"]:
                continue
            
            categories.append({
                "name": cat_name,
                "description": cat_data.get("description", ""),
                "severity": cat_data.get("severity", "medium"),
                "template_count": len(cat_data.get("templates", [])),
                "source": cat_data.get("source", ""),
                "license": cat_data.get("license", "")
            })
        
        return api_response({"categories": categories})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading categories: {str(e)}"
        )


@router.get("/jailbreak/backups", dependencies=[Depends(verify_api_key)])
async def list_jailbreak_backups():
    """
    List all available backup files.
    
    Returns:
        List of backup files with metadata
    """
    from core.template_updater import get_template_updater
    
    try:
        updater = get_template_updater()
        backups = updater.list_backups()
        
        return api_response({
            "backups": backups,
            "total": len(backups)
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing backups: {str(e)}"
        )


@router.post("/jailbreak/import", dependencies=[Depends(verify_api_key)])
async def import_jailbreak_templates(
    file_content: str = Query(..., description="JSON content to import"),
    merge: bool = Query(True, description="Merge with existing templates instead of replacing")
):
    """
    Import jailbreak templates from JSON.
    
    Args:
        file_content: JSON string containing templates
        merge: If True, merge with existing. If False, replace.
    """
    from pathlib import Path
    import json
    from core.template_updater import get_template_updater
    
    try:
        data_path = Path(__file__).parent.parent / "data" / "advanced_payloads.json"
        
        # Create backup before import
        updater = get_template_updater()
        backup_path = updater._backup_file(data_path) if data_path.exists() else None
        
        # Parse imported data
        imported_data = json.loads(file_content)
        
        if merge and data_path.exists():
            # Load existing data
            with open(data_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            
            # Merge categories
            for category, cat_data in imported_data.items():
                if category in ["version", "source", "last_updated"]:
                    continue
                
                if category in existing_data:
                    # Merge templates
                    existing_templates = set(existing_data[category].get("templates", []))
                    new_templates = cat_data.get("templates", [])
                    
                    for template in new_templates:
                        if template not in existing_templates:
                            existing_data[category]["templates"].append(template)
                    
                    existing_data[category]["last_updated"] = datetime.now().isoformat()
                else:
                    # New category
                    existing_data[category] = cat_data
            
            existing_data["last_updated"] = datetime.now().isoformat()
            final_data = existing_data
        else:
            # Replace
            final_data = imported_data
            final_data["last_updated"] = datetime.now().isoformat()
        
        # Save
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)
        
        # Count imported templates
        total_imported = sum(len(cat.get("templates", [])) for cat in final_data.values() if isinstance(cat, dict) and "templates" in cat)
        
        return api_response({
            "message": "Templates imported successfully",
            "total_templates": total_imported,
            "total_categories": len([k for k in final_data.keys() if k not in ["version", "source", "last_updated"]]),
            "backup_path": str(backup_path) if backup_path else None,
            "merge": merge
        })
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing templates: {str(e)}"
        )


@router.get("/jailbreak/export", dependencies=[Depends(verify_api_key)])
async def export_jailbreak_templates(
    category: Optional[str] = Query(None, description="Export specific category only")
):
    """
    Export jailbreak templates as JSON.
    
    Returns:
        JSON string of all templates or specific category
    """
    from pathlib import Path
    import json
    
    try:
        data_path = Path(__file__).parent.parent / "data" / "advanced_payloads.json"
        
        if not data_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="advanced_payloads.json not found"
            )
        
        with open(data_path, "r", encoding="utf-8") as f:
            payloads_data = json.load(f)
        
        if category:
            if category not in payloads_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category '{category}' not found"
                )
            export_data = {category: payloads_data[category]}
        else:
            export_data = payloads_data
        
        return api_response({
            "data": export_data,
            "exported_at": datetime.now().isoformat(),
            "category": category if category else "all"
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting templates: {str(e)}"
        )


@router.post("/jailbreak/restore", dependencies=[Depends(verify_api_key)])
async def restore_jailbreak_templates(
    backup_path: str = Query(..., description="Path to backup file to restore from")
):
    """
    Restore jailbreak templates from a backup file.
    
    Args:
        backup_path: Path to backup file (relative to data directory or absolute)
    """
    from core.template_updater import get_template_updater
    from pathlib import Path
    
    try:
        updater = get_template_updater()
        
        # Resolve backup path
        backup_file = Path(backup_path)
        if not backup_file.is_absolute():
            # Relative to data directory
            backup_file = updater.data_path / backup_path
        
        result = updater.restore_from_backup(str(backup_file))
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Restore failed")
            )
        
        return api_response(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error restoring from backup: {str(e)}"
        )


# Now parametrized routes can be defined
@router.get("/jailbreak/{category}", dependencies=[Depends(verify_api_key)])
async def get_jailbreak_category(category: str):
    """
    Get all templates for a specific category.
    
    Returns:
        Category data with all templates
    """
    from pathlib import Path
    import json
    
    try:
        data_path = Path(__file__).parent.parent / "data" / "advanced_payloads.json"
        
        if not data_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category}' not found"
            )
        
        with open(data_path, "r", encoding="utf-8") as f:
            payloads_data = json.load(f)
        
        if category not in payloads_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category}' not found"
            )
        
        return api_response(payloads_data[category])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading category: {str(e)}"
        )


@router.post("/jailbreak/{category}", dependencies=[Depends(verify_api_key)])
async def add_jailbreak_template(
    category: str,
    template: str = Query(..., description="Template string to add")
):
    """
    Add a new template to a category.
    
    Creates category if it doesn't exist.
    """
    from pathlib import Path
    import json
    
    try:
        data_path = Path(__file__).parent.parent / "data" / "advanced_payloads.json"
        
        # Load existing data
        if data_path.exists():
            with open(data_path, "r", encoding="utf-8") as f:
                payloads_data = json.load(f)
        else:
            payloads_data = {
                "version": "2.1.0",
                "source": "User-added",
                "last_updated": datetime.now().isoformat()
            }
        
        # Create category if it doesn't exist
        if category not in payloads_data:
            payloads_data[category] = {
                "description": f"User-added {category} templates",
                "severity": "medium",
                "templates": [],
                "source": "User-added",
                "last_updated": datetime.now().isoformat()
            }
        
        # Add template if not already present
        templates = payloads_data[category].get("templates", [])
        if template not in templates:
            templates.append(template)
            payloads_data[category]["templates"] = templates
            payloads_data[category]["last_updated"] = datetime.now().isoformat()
            payloads_data["last_updated"] = datetime.now().isoformat()
        
        # Save
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(payloads_data, f, indent=2, ensure_ascii=False)
        
        return api_response({
            "message": f"Template added to category '{category}'",
            "category": category,
            "template_count": len(templates)
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding template: {str(e)}"
        )


@router.put("/jailbreak/{category}/{template_index}", dependencies=[Depends(verify_api_key)])
async def update_jailbreak_template(
    category: str,
    template_index: int,
    template: str = Query(..., description="Updated template string")
):
    """
    Update a template at a specific index in a category.
    """
    from pathlib import Path
    import json
    from core.template_updater import get_template_updater
    
    try:
        data_path = Path(__file__).parent.parent / "data" / "advanced_payloads.json"
        
        if not data_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="advanced_payloads.json not found"
            )
        
        # Create backup before modification
        updater = get_template_updater()
        backup_path = updater._backup_file(data_path)
        
        # Load data
        with open(data_path, "r", encoding="utf-8") as f:
            payloads_data = json.load(f)
        
        if category not in payloads_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category}' not found"
            )
        
        templates = payloads_data[category].get("templates", [])
        if template_index < 0 or template_index >= len(templates):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Template index {template_index} out of range (0-{len(templates)-1})"
            )
        
        # Update template
        templates[template_index] = template
        payloads_data[category]["templates"] = templates
        payloads_data[category]["last_updated"] = datetime.now().isoformat()
        payloads_data["last_updated"] = datetime.now().isoformat()
        
        # Save
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(payloads_data, f, indent=2, ensure_ascii=False)
        
        return api_response({
            "message": f"Template updated in category '{category}'",
            "category": category,
            "template_index": template_index,
            "backup_path": str(backup_path)
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating template: {str(e)}"
        )


@router.delete("/jailbreak/{category}/{template_index}", dependencies=[Depends(verify_api_key)])
async def delete_jailbreak_template(
    category: str,
    template_index: int
):
    """
    Delete a template from a category.
    """
    from pathlib import Path
    import json
    from core.template_updater import get_template_updater
    
    try:
        data_path = Path(__file__).parent.parent / "data" / "advanced_payloads.json"
        
        if not data_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="advanced_payloads.json not found"
            )
        
        # Create backup before modification
        updater = get_template_updater()
        backup_path = updater._backup_file(data_path)
        
        # Load data
        with open(data_path, "r", encoding="utf-8") as f:
            payloads_data = json.load(f)
        
        if category not in payloads_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category}' not found"
            )
        
        templates = payloads_data[category].get("templates", [])
        if template_index < 0 or template_index >= len(templates):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Template index {template_index} out of range (0-{len(templates)-1})"
            )
        
        # Delete template
        deleted_template = templates.pop(template_index)
        payloads_data[category]["templates"] = templates
        payloads_data[category]["last_updated"] = datetime.now().isoformat()
        payloads_data["last_updated"] = datetime.now().isoformat()
        
        # Save
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(payloads_data, f, indent=2, ensure_ascii=False)
        
        return api_response({
            "message": f"Template deleted from category '{category}'",
            "category": category,
            "template_index": template_index,
            "deleted_template": deleted_template,
            "backup_path": str(backup_path)
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting template: {str(e)}"
        )


@router.delete("/jailbreak/{category}", dependencies=[Depends(verify_api_key)])
async def delete_jailbreak_category(category: str):
    """
    Delete an entire category.
    """
    from pathlib import Path
    import json
    from core.template_updater import get_template_updater
    
    try:
        data_path = Path(__file__).parent.parent / "data" / "advanced_payloads.json"
        
        if not data_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="advanced_payloads.json not found"
            )
        
        # Create backup before modification
        updater = get_template_updater()
        backup_path = updater._backup_file(data_path)
        
        # Load data
        with open(data_path, "r", encoding="utf-8") as f:
            payloads_data = json.load(f)
        
        if category not in payloads_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category}' not found"
            )
        
        # Delete category
        deleted_category = payloads_data.pop(category)
        payloads_data["last_updated"] = datetime.now().isoformat()
        
        # Save
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(payloads_data, f, indent=2, ensure_ascii=False)
        
        return api_response({
            "message": f"Category '{category}' deleted",
            "category": category,
            "templates_deleted": len(deleted_category.get("templates", [])),
            "backup_path": str(backup_path)
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting category: {str(e)}"
        )


# ============================================================================
# Experiment Template CRUD Endpoints (AFTER all jailbreak routes)
# ============================================================================

@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_api_key)])
async def create_template(
    template: ExperimentTemplateCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new experiment template.
    
    Saves the complete ExperimentConfig as a reusable template.
    """
    repo = ExperimentTemplateRepository(session)
    db_template = await repo.create(template)
    await session.commit()
    
    return api_response(db_to_response(db_template))


@router.get("", dependencies=[Depends(verify_api_key)])
async def list_templates(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    is_public: Optional[bool] = Query(None, description="Filter by public/private"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter"),
    session: AsyncSession = Depends(get_session)
):
    """
    List all experiment templates with pagination and filters.
    """
    from sqlalchemy import select, func
    from core.database import ExperimentTemplateDB
    
    repo = ExperimentTemplateRepository(session)
    offset = (page - 1) * page_size
    
    # Parse tags
    tag_list = [t.strip() for t in tags.split(',')] if tags else None
    
    # list_all now returns (templates, total_count) with tag filtering applied
    templates, total = await repo.list_all(
        limit=page_size,
        offset=offset,
        is_public=is_public,
        created_by=created_by,
        tags=tag_list
    )
    
    response = ExperimentTemplateListResponse(
        items=[db_to_response(t) for t in templates],
        total=total,
        page=page,
        page_size=page_size
    )
    return api_response(response)


@router.get("/{template_id}", dependencies=[Depends(verify_api_key)])
async def get_template(
    template_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """
    Get template by ID.
    """
    repo = ExperimentTemplateRepository(session)
    template = await repo.get_by_id(template_id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found"
        )
    
    return api_response(db_to_response(template))


@router.put("/{template_id}", dependencies=[Depends(verify_api_key)])
async def update_template(
    template_id: UUID,
    update_data: ExperimentTemplateUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update template.
    """
    repo = ExperimentTemplateRepository(session)
    template = await repo.update(template_id, update_data)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found"
        )
    
    await session.commit()
    return api_response(db_to_response(template))


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_api_key)])
async def delete_template(
    template_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete template.
    """
    repo = ExperimentTemplateRepository(session)
    success = await repo.delete(template_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found"
        )
    
    await session.commit()


@router.post("/{template_id}/use", dependencies=[Depends(verify_api_key)])
async def use_template(
    template_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    """
    Increment usage count and return template config.
    
    This endpoint is called when a user loads a template into the experiment form.
    """
    repo = ExperimentTemplateRepository(session)
    template = await repo.get_by_id(template_id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found"
        )
    
    # Increment usage count
    await repo.increment_usage(template_id)
    await session.commit()
    
    # Refresh template to get updated usage_count (Comment 2)
    await session.refresh(template)
    
    return api_response(db_to_response(template))


