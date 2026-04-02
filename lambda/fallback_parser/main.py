import os
import json
import boto3
import fitz  # PyMuPDF
import re
import time
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
JOBS_TABLE_NAME = os.environ.get('DYNAMODB_TABLE')
JOBS_TABLE = dynamodb.Table(JOBS_TABLE_NAME) if JOBS_TABLE_NAME else None

def extract_text_pymupdf(local_pdf_path):
    """
    Acts as the final safety net if Grobid crashes.
    Strips raw text from the document and structures it heuristically.
    """
    doc = fitz.open(local_pdf_path)
    full_text = ""
    
    # Process up to 15 pages to keep fallback lightweight
    for i in range(min(15, len(doc))): 
        full_text += doc[i].get_text("text") + "\n"
    doc.close()
    
    abstract = ""
    # Regex heuristic to find the abstract block before the Introduction starts
    match = re.search(r'(?i)abstract[\s\r\n]+(.*?)(?=\n\s*(?:introduction|1\.|background|\n\n))', full_text, re.DOTALL)
    if match:
        abstract = match.group(1).strip()
        
    return {
        "abstract": abstract,
        "body": full_text
    }

def lambda_handler(event, context):
    start_time = time.time()
    
    job_id = event.get('job_id', 'unknown_job')
    user_id = event.get('user_id', 'unknown_user')
    s3_key = event.get('s3_key')
    
    logger.info(f"Fallback Parser Started | job_id: {job_id}")

    local_input = f"/tmp/{job_id}_fallback_in.pdf"
    
    # Adhere strictly to the Partial Success Dictionary Pattern
    final_output = {
        "status": "partial_success",
        "modules": {
            "grobid": "failed",
            "pymupdf": "success"
        },
        "data": {},
        "user_feedback": ["Structure extraction failed. Using fallback plain text extraction."]
    }

    try:
        # 1. Download Corrupted/Failed PDF
        if s3_key and S3_BUCKET:
            s3_client.download_file(S3_BUCKET, s3_key, local_input)
        else:
            raise Exception("Missing S3 Key or Bucket")
        
        # 2. Extract Data using PyMuPDF (fitz)
        extracted_data = extract_text_pymupdf(local_input)
        final_output["data"] = extracted_data
        
        # 3. Semantic Validation of the fallback
        if not extracted_data.get("abstract"):
             final_output["user_feedback"].append("Missing or incomplete abstract detected.")
             
        # 4. Update DynamoDB Status Resiliently
        if JOBS_TABLE:
            JOBS_TABLE.update_item(
                Key={"job_id": job_id, "user_id": user_id},
                UpdateExpression="SET #s = :s, completed_at = :now, fallback_used = :f, result_data = :rd",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={
                    ":s": "partial_success",
                    ":now": datetime.utcnow().isoformat(),
                    ":f": True,
                    ":rd": json.dumps(final_output)
                }
            )
        
        exec_time = time.time() - start_time
        logger.info(f"Fallback Parser Completed | job_id: {job_id} | time: {exec_time:.2f}s")
        
        return {
            'statusCode': 200,
            'body': json.dumps(final_output)
        }

    except Exception as e:
        exec_time = time.time() - start_time
        logger.error(f"Fallback Parser Fatal Error | job_id: {job_id} | time: {exec_time:.2f}s | error: {str(e)}")
        
        # Total unrecoverable failure
        if JOBS_TABLE:
            JOBS_TABLE.update_item(
                Key={"job_id": job_id, "user_id": user_id},
                UpdateExpression="SET #s = :s, #err = :e",
                ExpressionAttributeNames={"#s": "status", "#err": "error"},
                ExpressionAttributeValues={":s": "failed", ":e": f"All parsers failed: {str(e)}"}
            )
        return {
            'statusCode': 500,
            'body': json.dumps({"status": "failed", "error": str(e)})
        }
    finally:
        if os.path.exists(local_input):
            os.remove(local_input)
