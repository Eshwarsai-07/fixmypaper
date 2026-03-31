import os
from datetime import datetime
import structlog
from celery import Celery
from celery.exceptions import SoftTimeLimitExceeded

from backend.app.core.config import settings
from backend.app.services.database import SessionLocal
from backend.app.models.job import Job
from backend.app.services.storage import StorageManager
from backend.app.services.pdf_processor import PDFErrorDetector

from backend.app.core.logging_config import setup_logging

setup_logging()
logger = structlog.get_logger()

def create_celery_app():
    return Celery(
        "fixmypaper",
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL
    )

celery_app = create_celery_app()

@celery_app.task(name="process_pdf_job", bind=True, max_retries=3, time_limit=300, soft_time_limit=290)
def process_pdf_job(self, job_id: str, s3_key: str, correlation_id: str = None):
    structlog.contextvars.clear_contextvars()
    if correlation_id:
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        logger.error("job_not_found", job_id=job_id)
        return

    logger.info("job_processing_started", job_id=job_id, status="processing")
    job.status = "processing"
    job.processing_started_at = datetime.utcnow()
    db.commit()

    local_input = f"/tmp/{job_id}_input.pdf"
    local_output = f"/tmp/{job_id}_output.pdf"

    try:
        # 1. Download from S3
        StorageManager.download_from_s3(s3_key, local_input)
        
        # 2. Process PDF
        processor = PDFErrorDetector()
        errors, output_path, stats, extracted_data, ref_analysis = processor.detect_errors(
            input_path=local_input,
            output_path=local_output,
            job_id=job_id
        )

        # 3. Upload Result to S3
        result_key = f"results/{job_id}.pdf"
        with open(local_output, "rb") as f:
            StorageManager.upload_to_s3(f.read(), result_key)

        # 4. Update Database
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.result_s3_key = result_key
        job.statistics = stats
        
        if "module_status" in extracted_data:
            job.module_status = extracted_data["module_status"]
            
        if any(status == "failed" for status in job.module_status.values()):
            job.status = "partial_success"

        db.commit()
        
        # Calculate duration for structured logging
        duration = (job.completed_at - job.processing_started_at).total_seconds()
        logger.info("job_completed", 
                    job_id=job_id, 
                    status=job.status, 
                    processing_time=round(duration, 2))

    except SoftTimeLimitExceeded:
        logger.error("job_timeout_soft", job_id=job_id, status="failed")
        job.status = "failed"
        job.error_message = "Execution exceeded 300-second time limit."
        db.commit()
        logger.critical("job_sent_to_dlq_timeout", job_id=job_id, status="failed")

    except Exception as exc:
        logger.error("job_failed", job_id=job_id, error=str(exc))
        job.retry_count += 1
        db.commit()
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

    finally:
        db.close()
        # Cleanup
        for path in [local_input, local_output]:
            if os.path.exists(path):
                os.remove(path)
