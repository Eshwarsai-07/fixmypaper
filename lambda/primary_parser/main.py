import json
import logging
import urllib3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

http = urllib3.PoolManager()

def lambda_handler(event, context):
    """
    Primary Parser Proxy: Forwards Step Function requests to the Grobid service on EKS.
    This Lambda acts as a bridge to resolve internal .local DNS and provides extra retry logic.
    """
    api_url = os.environ.get("API_WORKER_URL")
    
    logger.info(f"Received event: {json.dumps(event)}")
    logger.info(f"Targeting Grobid at: {api_url}")

    try:
        # Forward the request to Grobid
        # Expecting event to contain job_id and s3_key
        response = http.request(
            'POST',
            f"{api_url}/processHeaderDocument",
            fields={
                'job_id': event.get('job_id'),
                's3_key': event.get('s3_key')
            },
            timeout=30.0,
            retries=False
        )

        logger.info(f"Grobid response status: {response.status}")
        
        if response.status == 200:
            return {
                'statusCode': 200,
                'body': response.data.decode('utf-8'),
                'job_id': event.get('job_id')
            }
        else:
            raise Exception(f"Grobid returned error status: {response.status}")

    except Exception as e:
        logger.error(f"Error calling Grobid: {str(e)}")
        raise e
