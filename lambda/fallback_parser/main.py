import os
import json
import boto3
import fitz  # PyMuPDF
from datetime import datetime

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
JOBS_TABLE_NAME = os.environ.get('DYNAMODB_TABLE')
JOBS_TABLE = dynamodb.Table(JOBS_TABLE_NAME)

def lambda_handler(event, context):
    job_id = event.get('job_id')
    user_id = event.get('user_id')
    s3_key = event.get('s3_key')
    
    local_input = f"/tmp/{job_id}_fallback_in.pdf"
    local_output = f"/tmp/{job_id}_fallback_out.pdf"
    result_key = f"results/{job_id}_fallback.pdf"

    try:
        # 1. Download from S3
        s3_client.download_file(S3_BUCKET, s3_key, local_input)
        
        # 2. Simple Parse / Cleanup with PyMuPDF
        doc = fitz.open(local_input)
        # Perform lightweight fixes (e.g., standardizing fonts, basic OCR or metadata cleaning)
        doc.save(local_output)
        doc.close()
        
        # 3. Upload Result
        with open(local_output, 'rb') as f:
            s3_client.put_object(Bucket=S3_BUCKET, Key=result_key, Body=f.read())
            
        # 4. Update DynamoDB Status
        JOBS_TABLE.update_item(
            Key={"job_id": job_id, "user_id": user_id},
            UpdateExpression="SET #s = :s, completed_at = :now, result_s3_key = :r, fallback_used = :f",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={
                ":s": "completed",
                ":now": datetime.utcnow().isoformat(),
                ":r": result_key,
                ":f": True
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'completed', 'fallback': True})
        }

    except Exception as e:
        JOBS_TABLE.update_item(
            Key={"job_id": job_id, "user_id": user_id},
            UpdateExpression="SET #s = :s, #err = :e",
            ExpressionAttributeNames={"#s": "status", "#err": "error"},
            ExpressionAttributeValues={":s": "failed", ":e": f"Fallback failed: {str(e)}"}
        )
        return {
            'statusCode': 500,
            'body': json.dumps({'status': 'failed', 'error': str(e)})
        }
    finally:
        # Cleanup
        for path in [local_input, local_output]:
            if os.path.exists(path):
                os.remove(path)
