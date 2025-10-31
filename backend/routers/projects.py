from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from fastapi.responses import FileResponse
import os
from uuid import uuid4
from datetime import datetime
from typing import Dict
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from middleware.auth import get_current_user

router = APIRouter()

# In-memory storage for demo (replace with database)
projects_db: Dict[str, dict] = {}
reports_db: Dict[str, dict] = {}

# Ensure reports directory exists
REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

class ProjectCreate(BaseModel):
    name: str
    location: str
    engineer_name: str
    pole_type: str

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    engineer_name: Optional[str] = None
    pole_type: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    name: str
    location: str
    engineer_name: str
    pole_type: str
    created_at: datetime
    updated_at: datetime
    user_id: str

@router.get("/", response_model=List[ProjectResponse])
async def get_projects(current_user: dict = Depends(get_current_user)):
    """Get all projects for the current user"""
    user_id = current_user["ocid"]
    user_projects = [p for p in projects_db.values() if p["user_id"] == user_id]
    return user_projects

@router.post("/", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, current_user: dict = Depends(get_current_user)):
    """Create a new project"""
    user_id = current_user["ocid"]
    project_id = f"proj_{len(projects_db) + 1}"
    
    new_project = {
        "id": project_id,
        "name": project.name,
        "location": project.location,
        "engineer_name": project.engineer_name,
        "pole_type": project.pole_type,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "user_id": user_id
    }
    
    projects_db[project_id] = new_project
    return new_project


@router.post("/{project_id}/reports", status_code=status.HTTP_201_CREATED)
async def upload_project_report(project_id: str, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Upload a PDF report for a project"""
    user_id = current_user["ocid"]

    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]
    if project["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Save file
    report_id = f"rep_{len(reports_db) + 1}_{uuid4().hex[:8]}"
    filename = f"{project_id}_{report_id}.pdf"
    file_path = os.path.join(REPORTS_DIR, filename)

    with open(file_path, 'wb') as f:
        content = await file.read()
        f.write(content)

    report_meta = {
        "id": report_id,
        "project_id": project_id,
        "user_id": user_id,
        "filename": filename,
        "original_name": file.filename,
        "content_type": file.content_type,
        "created_at": datetime.utcnow(),
        "path": file_path
    }

    reports_db[report_id] = report_meta

    # Attach report list to project for easy retrieval (in-memory)
    project_reports = project.get("reports", [])
    project_reports.append(report_meta)
    project["reports"] = project_reports

    return {"id": report_id, "filename": filename, "original_name": file.filename, "created_at": report_meta["created_at"]}


@router.get("/{project_id}/reports")
async def list_project_reports(project_id: str, current_user: dict = Depends(get_current_user)):
    """List reports for a given project"""
    user_id = current_user["ocid"]
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]
    if project["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return project.get("reports", [])


@router.get("/{project_id}/reports/{report_id}")
async def download_project_report(project_id: str, report_id: str, current_user: dict = Depends(get_current_user)):
    """Download a saved PDF report"""
    user_id = current_user["ocid"]
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]
    if project["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if report_id not in reports_db:
        raise HTTPException(status_code=404, detail="Report not found")

    report = reports_db[report_id]
    if report["project_id"] != project_id or report["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return FileResponse(report["path"], media_type=report.get("content_type", "application/pdf"), filename=report.get("original_name", report.get("filename")))

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific project"""
    user_id = current_user["ocid"]
    
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    if project["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, project_update: ProjectUpdate, current_user: dict = Depends(get_current_user)):
    """Update a project"""
    user_id = current_user["ocid"]
    
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    if project["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update fields
    for field, value in project_update.dict(exclude_unset=True).items():
        project[field] = value
    
    project["updated_at"] = datetime.utcnow()
    projects_db[project_id] = project
    
    return project

@router.delete("/{project_id}")
async def delete_project(project_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a project"""
    user_id = current_user["ocid"]
    
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    if project["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    del projects_db[project_id]
    return {"message": "Project deleted successfully"}
