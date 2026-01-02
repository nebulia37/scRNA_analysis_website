from celery import Celery
import subprocess
import json
import os
from datetime import datetime
import time

# Initialize Celery
celery_app = Celery(
    'scrna_analysis',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600 * 4,  # 4 hours max
    task_soft_time_limit=3600 * 3.5,  # 3.5 hours soft limit
)

@celery_app.task(bind=True, name='run_analysis')
def run_analysis(self, job_id: int):
    """
    Execute single-cell RNA analysis job
    This task calls your existing R/Python analysis scripts
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models.job import AnalysisJob, JobStatus
    
    # Database connection
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/scrna_db'))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Get job details
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if not job:
            raise Exception(f"Job {job_id} not found")
        
        # Update job status
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        db.commit()
        
        # Parse parameters
        params = json.loads(job.parameters) if job.parameters else {}
        
        # Create output directory
        output_dir = f"/data/outputs/job_{job_id}"
        os.makedirs(output_dir, exist_ok=True)
        job.output_directory = output_dir
        db.commit()
        
        # Update progress
        self.update_state(state='PROGRESS', meta={'progress': 10, 'step': 'Initializing'})
        job.progress_percent = 10
        job.current_step = 'Initializing'
        db.commit()
        
        # Route to appropriate analysis function
        if job.job_type == 'clustering':
            result = run_clustering_analysis(job, params, output_dir, self, db)
        elif job.job_type == 'annotation':
            result = run_annotation_analysis(job, params, output_dir, self, db)
        elif job.job_type == 'differential_expression':
            result = run_de_analysis(job, params, output_dir, self, db)
        else:
            raise ValueError(f"Unknown job type: {job.job_type}")
        
        # Update job with results
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.result_summary = json.dumps(result)
        job.progress_percent = 100
        job.current_step = 'Completed'
        
        # Calculate resource usage
        end_time = datetime.utcnow()
        duration_hours = (end_time - job.started_at).total_seconds() / 3600
        job.cpu_hours = duration_hours  # Simplified, should track actual CPU usage
        
        db.commit()
        
        return {"status": "completed", "job_id": job_id, "result": result}
        
    except Exception as e:
        # Handle failure
        job.status = JobStatus.FAILED
        job.completed_at = datetime.utcnow()
        job.error_message = str(e)
        db.commit()
        
        raise
        
    finally:
        db.close()

def run_clustering_analysis(job, params, output_dir, task, db):
    """
    Run clustering analysis using your existing R/Python scripts
    """
    # Update progress
    task.update_state(state='PROGRESS', meta={'progress': 20, 'step': 'Loading data'})
    job.progress_percent = 20
    job.current_step = 'Loading data'
    db.commit()
    
    # Prepare command to call your analysis script
    # Example with R script
    cmd = [
        'Rscript',
        '/app/scripts/clustering.R',
        '--input', job.input_file_path,
        '--output', output_dir,
        '--resolution', str(params.get('resolution', 0.8)),
        '--n_pcs', str(params.get('n_pcs', 50))
    ]
    
    # Or with Python script
    # cmd = [
    #     'python',
    #     '/app/scripts/clustering.py',
    #     '--input', job.input_file_path,
    #     '--output', output_dir,
    #     '--resolution', str(params.get('resolution', 0.8))
    # ]
    
    # Update progress
    task.update_state(state='PROGRESS', meta={'progress': 40, 'step': 'Running clustering'})
    job.progress_percent = 40
    job.current_step = 'Running clustering'
    db.commit()
    
    # Execute analysis
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    stdout, stderr = process.communicate()
    
    if process.returncode != 0:
        raise Exception(f"Analysis failed: {stderr}")
    
    # Update progress
    task.update_state(state='PROGRESS', meta={'progress': 80, 'step': 'Generating visualizations'})
    job.progress_percent = 80
    job.current_step = 'Generating visualizations'
    db.commit()
    
    # Parse results (assuming your script outputs a JSON summary)
    result_file = os.path.join(output_dir, 'summary.json')
    if os.path.exists(result_file):
        with open(result_file, 'r') as f:
            results = json.load(f)
    else:
        results = {
            "n_clusters": "Unknown",
            "message": "Analysis completed but summary not found"
        }
    
    return results

def run_annotation_analysis(job, params, output_dir, task, db):
    """Run cell type annotation"""
    task.update_state(state='PROGRESS', meta={'progress': 30, 'step': 'Annotating cells'})
    job.progress_percent = 30
    job.current_step = 'Annotating cells'
    db.commit()
    
    cmd = [
        'python',
        '/app/scripts/annotation.py',
        '--input', job.input_file_path,
        '--output', output_dir,
        '--reference', params.get('reference_dataset', 'default')
    ]
    
    process = subprocess.run(cmd, capture_output=True, text=True)
    
    if process.returncode != 0:
        raise Exception(f"Annotation failed: {process.stderr}")
    
    # Parse and return results
    return {"message": "Annotation completed", "output_dir": output_dir}

def run_de_analysis(job, params, output_dir, task, db):
    """Run differential expression analysis"""
    task.update_state(state='PROGRESS', meta={'progress': 30, 'step': 'Computing differential expression'})
    job.progress_percent = 30
    job.current_step = 'Computing differential expression'
    db.commit()
    
    cmd = [
        'Rscript',
        '/app/scripts/differential_expression.R',
        '--input', job.input_file_path,
        '--output', output_dir,
        '--group1', ','.join(params.get('group1', [])),
        '--group2', ','.join(params.get('group2', [])),
        '--method', params.get('test_method', 'wilcoxon')
    ]
    
    process = subprocess.run(cmd, capture_output=True, text=True)
    
    if process.returncode != 0:
        raise Exception(f"DE analysis failed: {process.stderr}")
    
    return {"message": "Differential expression analysis completed", "output_dir": output_dir}