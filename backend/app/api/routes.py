import uuid
import structlog
from datetime import datetime
from fastapi import APIRouter, Request, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.app.models.job import Job
from backend.app.services.database import get_db
from backend.app.services.storage import StorageManager
from backend.app.core.config import settings

router = APIRouter()
logger = structlog.get_logger()
limiter = Limiter(key_func=get_remote_address)

@router.post("/upload")
@limiter.limit("10/minute")
async def upload_file(
    request: Request,
    file: UploadFile = File(...), 
    format_id: str = Form(""),
    db: Session = Depends(get_db)
):
    # Validation using StorageManager
    content = await file.read()
    StorageManager.validate_file(content, file.filename)

    job_id = str(uuid.uuid4())
    s3_key = f"uploads/{job_id}_{file.filename}"

    try:
        # Upload to S3
        StorageManager.upload_to_s3(content, s3_key)
        
        # Create Job record
        job = Job(
            id=job_id,
            filename=file.filename,
            s3_key=s3_key,
            status="pending",
            created_at=datetime.utcnow()
        )
        db.add(job)
        db.commit()

        # Trigger Celery Task
        from backend.worker import celery_app
        from structlog.contextvars import get_contextvars
        
        correlation_id = get_contextvars().get("correlation_id", str(uuid.uuid4()))
        celery_app.send_task("process_pdf_job", args=[job_id, s3_key, correlation_id])
        
        logger.info("job_created", job_id=job_id, filename=file.filename, correlation_id=correlation_id)
        return {"job_id": job_id, "status": "pending", "correlation_id": correlation_id}

    except Exception as e:
        logger.error("upload_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to process upload")

@router.get("/status/{job_id}")
async def get_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job.id,
        "status": job.status,
        "retry_count": job.retry_count,
        "module_status": job.module_status,
        "created_at": job.created_at,
        "processing_started_at": job.processing_started_at,
        "completed_at": job.completed_at,
        "statistics": job.statistics,
        "error": job.error_message
    }

@router.get("/download/{job_id}")
async def download_result(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job or not job.result_s3_key:
        raise HTTPException(status_code=404, detail="Result not found or job not finished")
    
    url = StorageManager.generate_presigned_url(job.result_s3_key)
    if not url:
        raise HTTPException(status_code=500, detail="Failed to generate download link")
    return {"download_url": url}

@router.get("/metrics/queue-depth")
async def get_queue_depth(db: Session = Depends(get_db)):
    pending_count = db.query(Job).filter(Job.status == "pending").count()
    processing_count = db.query(Job).filter(Job.status == "processing").count()
    return {
        "pending_jobs": pending_count,
        "processing_jobs": processing_count,
        "total_backlog": pending_count + processing_count
    }

@router.get("/health")
async def health():
    import time
    return {"status": "healthy", "timestamp": time.time()}
