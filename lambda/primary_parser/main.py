import json
import logging
import urllib3
import os
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

http = urllib3.PoolManager()

def semantic_validation(data):
    """
    Checks the extracted data for missing critical elements
    to ensure we don't pass garbage to the user.
    """
    feedback = []
    
    # In case Grobid returned string/XML instead of neat JSON
    if not isinstance(data, dict):
        return ["Structure might be malformed or unparsed."]
        
    abstract = data.get('abstract', "")
    if len(abstract) < 50:
        feedback.append("Missing or incomplete abstract.")
        
    references = data.get('references', [])
    if not references:
        feedback.append("No references extracted. Section may be malformed.")
        
    return feedback

def lambda_handler(event, context):
    start_time = time.time()
    api_url = os.environ.get("API_WORKER_URL")
    job_id = event.get('job_id')
    
    logger.info(f"Primary Parser Started | job_id: {job_id}")

    try:
        response = http.request(
            'POST',
            f"{api_url}/processHeaderDocument",
            fields={
                'job_id': job_id,
                's3_key': event.get('s3_key')
            },
            timeout=30.0,
            retries=False
        )

        # Trigger Step Function fallback immediately if Grobid fails
        if response.status != 200:
            raise Exception(f"Grobid error: {response.status}")

        raw_data = response.data.decode('utf-8')
        
        try:
            grobid_data = json.loads(raw_data)
        except json.JSONDecodeError:
            grobid_data = {"raw_output": raw_data}
            
        # Semantic Validation
        feedback = semantic_validation(grobid_data)
        
        status = "partial_success" if feedback else "success"
            
        final_output = {
            "status": status,
            "modules": {
                "grobid": "success",
                "tables": "skipped",
                "equations": "skipped"
            },
            "data": grobid_data,
            "user_feedback": feedback
        }

        exec_time = time.time() - start_time
        logger.info(f"Primary Parsed Successfully | job_id: {job_id} | time: {exec_time:.2f}s | status: {status}")

        return {
            'statusCode': 200,
            'body': json.dumps(final_output),
            'job_id': job_id
        }

    except Exception as e:
        exec_time = time.time() - start_time
        logger.error(f"Primary Parser Failed | job_id: {job_id} | time: {exec_time:.2f}s | error: {str(e)}")
        # Raise exception so AWS Step Functions catches it and routes to Fallback Parser
        raise e
