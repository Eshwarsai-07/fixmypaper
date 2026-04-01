import uuid
import json
import structlog
import hashlib
import boto3
from datetime import datetime
from fastapi import APIRouter, Request, File, UploadFile, Form, HTTPException, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.services.storage import StorageManager
from app.core.config import settings
from app.core.auth import cognito_auth

router = APIRouter()
logger = structlog.get_logger()
limiter = Limiter(key_func=get_remote_address)

# AWS Clients
dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
sfn_client = boto3.client('stepfunctions', region_name=settings.AWS_REGION)
sqs_client = boto3.client('sqs', region_name=settings.AWS_REGION)

JOBS_TABLE = dynamodb.Table(settings.DYNAMODB_TABLE)
SFN_ARN = settings.STEP_FUNCTIONS_ARN
SQS_URL = settings.SQS_QUEUE_URL

@router.post("/upload")
@limiter.limit("10/minute")
async def upload_file(
    request: Request,
    file: UploadFile = File(...), 
    token: dict = Depends(cognito_auth.verify_token)
):
    user_id = token['sub']
    # 1. Backpressure Check
    try:
        sqs_attr = sqs_client.get_queue_attributes(
            QueueUrl=SQS_URL,
            AttributeNames=['ApproximateNumberOfMessagesVisible']
        )
        msg_count = int(sqs_attr['Attributes']['ApproximateNumberOfMessagesVisible'])
        if msg_count > 1000: # Threshold from Staff review
            logger.warning("backpressure_throttling", msg_count=msg_count)
            raise HTTPException(status_code=503, detail="System under high load, please try again later")
    except Exception as e:
        logger.error("backpressure_check_failed", error=str(e))

    # 2. Upload to S3
    content = await file.read()
    StorageManager.validate_file(content, file.filename)
    
    job_id = str(uuid.uuid4())
    s3_key = f"uploads/{job_id}_{file.filename}"
    
    try:
        StorageManager.upload_to_s3(content, s3_key)
        etag = StorageManager.get_file_etag(s3_key)
        
        # 3. Idempotency Check
        idempotency_key = hashlib.sha256(f"{etag}:{user_id}".encode()).hexdigest()
        
        # Check DynamoDB for existing hash
        resp = JOBS_TABLE.query(
            IndexName='IdempotencyIndex',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('idempotency_key').eq(idempotency_key)
        )
        
        if resp['Items']:
            existing = resp['Items'][0]
            if existing['status'] in ['processing', 'completed']:
                logger.info("idempotency_skip", job_id=existing['job_id'], user_id=user_id)
                return {"job_id": existing['job_id'], "status": existing['status'], "idempotent": True}

        # 4. Initialize Job & Start Orchestration
        JOBS_TABLE.put_item(Item={
            "job_id": job_id,
            "user_id": user_id,
            "idempotency_key": idempotency_key,
            "status": "pending",
            "filename": file.filename,
            "s3_key": s3_key,
            "created_at": datetime.utcnow().isoformat()
        })

        sfn_client.start_execution(
            stateMachineArn=SFN_ARN,
            input=json.dumps({
                "job_id": job_id,
                "user_id": user_id,
                "s3_key": s3_key,
                "idempotency_key": idempotency_key
            })
        )

        logger.info("job_orchestrated", job_id=job_id, user_id=user_id)
        return {"job_id": job_id, "status": "pending"}

    except Exception as e:
        logger.error("upload_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to process upload: {str(e)}")

@router.get("/status/{job_id}")
async def get_status(job_id: str, token: dict = Depends(cognito_auth.verify_token)):
    user_id = token['sub']
    resp = JOBS_TABLE.get_item(Key={"job_id": job_id, "user_id": user_id})
    item = resp.get('Item')
    if not item:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return item

@router.get("/download/{job_id}")
async def download_result(job_id: str, token: dict = Depends(cognito_auth.verify_token)):
    user_id = token['sub']
    resp = JOBS_TABLE.get_item(Key={"job_id": job_id, "user_id": user_id})
    item = resp.get('Item')
    if not item or not item.get('result_s3_key'):
        raise HTTPException(status_code=404, detail="Result not found or job not finished")
    
    url = StorageManager.generate_presigned_url(item['result_s3_key'])
    if not url:
        raise HTTPException(status_code=500, detail="Failed to generate download link")
    return {"download_url": url}

@router.get("/metrics/queue-depth")
async def get_queue_depth(token: dict = Depends(cognito_auth.verify_token)):
    try:
        sqs_attr = sqs_client.get_queue_attributes(
            QueueUrl=SQS_URL,
            AttributeNames=['ApproximateNumberOfMessagesVisible', 'ApproximateNumberOfMessagesNotVisible']
        )
        return {
            "pending_jobs": int(sqs_attr['Attributes']['ApproximateNumberOfMessagesVisible']),
            "processing_jobs": int(sqs_attr['Attributes']['ApproximateNumberOfMessagesNotVisible'])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch queue metrics")

@router.get("/health")
async def health():
    import time
    return {"status": "healthy", "timestamp": time.time()}
