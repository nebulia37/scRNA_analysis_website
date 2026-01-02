from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import json

router = APIRouter()

# Schemas
class JobCreate(BaseModel):
    job_name: str
    job_type: str  # clustering, annotation, differential_expression
    input_file_id: str
    parameters: dict

class JobResponse(BaseModel):
    id: int
    job_name: str
    job_type: str
    status: str
    progress_percent: int
    current_step: Optional[str]
    submitted_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    result_summary: Optional[str]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True

class JobParameters(BaseModel):
    # Clustering parameters
    resolution: Optional[float] = 0.8
    n_pcs: Optional[int] = 50
    
    # Annotation parameters
    reference_dataset: Optional[str] = None
    
    # Differential expression parameters
    group1: Optional[List[str]] = None
    group2: Optional[List[str]] = None
    test_method: Optional[str] = "wilcoxon"

@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new analysis job"""
    from app.models.job import AnalysisJob, JobStatus
    from app.tasks.analysis import run_analysis
    
    # Check user quota
    if not check_user_quota(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usage quota exceeded. Please upgrade your subscription."
        )
    
    # Validate input file exists and belongs to user
    input_file = get_user_file(job_data.input_file_id, current_user.id, db)
    if not input_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Input file not found"
        )
    
    # Create job record
    db_job = AnalysisJob(
        user_id=current_user.id,
        job_name=job_data.job_name,
        job_type=job_data.job_type,
        input_file_path=input_file.file_path,
        parameters=json.dumps(job_data.parameters),
        status=JobStatus.PENDING
    )
    
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    # Submit to Celery queue
    run_analysis.delay(db_job.id)
    
    return db_job

@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all jobs for current user"""
    from app.models.job import AnalysisJob
    
    query = db.query(AnalysisJob).filter(AnalysisJob.user_id == current_user.id)
    
    if status:
        query = query.filter(AnalysisJob.status == status)
    
    jobs = query.order_by(AnalysisJob.submitted_at.desc()).offset(skip).limit(limit).all()
    
    return jobs

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get job details"""
    from app.models.job import AnalysisJob
    
    job = db.query(AnalysisJob).filter(
        AnalysisJob.id == job_id,
        AnalysisJob.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_job(
    job_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a running job"""
    from app.models.job import AnalysisJob, JobStatus
    
    job = db.query(AnalysisJob).filter(
        AnalysisJob.id == job_id,
        AnalysisJob.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed or failed job"
        )
    
    # Update status and revoke Celery task
    job.status = JobStatus.CANCELLED
    db.commit()
    
    # Revoke the Celery task
    from app.tasks.analysis import celery_app
    celery_app.control.revoke(str(job.id), terminate=True)
    
    return None

@router.get("/{job_id}/results")
async def get_job_results(
    job_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get job results and output files"""
    from app.models.job import AnalysisJob, JobStatus
    import os
    
    job = db.query(AnalysisJob).filter(
        AnalysisJob.id == job_id,
        AnalysisJob.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is not completed yet"
        )
    
    # List output files
    output_files = []
    if job.output_directory and os.path.exists(job.output_directory):
        for filename in os.listdir(job.output_directory):
            file_path = os.path.join(job.output_directory, filename)
            output_files.append({
                "filename": filename,
                "size": os.path.getsize(file_path),
                "download_url": f"/api/jobs/{job_id}/download/{filename}"
            })
    
    return {
        "job_id": job.id,
        "status": job.status,
        "result_summary": json.loads(job.result_summary) if job.result_summary else None,
        "output_files": output_files
    }

# Helper functions
def check_user_quota(user, db) -> bool:
    """Check if user has available quota"""
    # Implement quota checking logic based on subscription tier
    return True

def get_user_file(file_id: str, user_id: int, db):
    """Get file by ID if it belongs to user"""
    # Implement file retrieval logic
    pass

def get_current_user():
    """Get current authenticated user (placeholder)"""
    pass

def get_db():
    """Get database session (placeholder)"""
    pass