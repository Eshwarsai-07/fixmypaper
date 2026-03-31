import os
import boto3
import uuid
import fitz # PyMuPDF
from botocore.exceptions import NoCredentialsError
from fastapi import HTTPException
from backend.app.core.config import settings

S3_BUCKET = settings.S3_BUCKET_NAME
S3_REGION = settings.AWS_REGION

s3_client = boto3.client('s3', region_name=S3_REGION)

class StorageManager:
    @staticmethod
    def validate_file(file_content: bytes, filename: str):
        # 1. Type Check (PDF only)
        if not filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # 2. Size Check (Max 20MB)
        if len(file_content) > 20 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 20MB limit")
        
        # 3. Page Count Check (Max 20 pages) - PyMuPDF
        try:
            doc = fitz.open(stream=file_content, filetype="pdf")
            page_count = len(doc)
            doc.close()
            if page_count > 20:
                raise HTTPException(status_code=400, detail=f"File exceeds 20-page limit (found {page_count})")
        except Exception as e:
             raise HTTPException(status_code=400, detail=f"Invalid PDF file: {str(e)}")

    @staticmethod
    def upload_to_s3(file_content: bytes, s3_key: str):
        try:
            s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=file_content)
            return s3_key
        except NoCredentialsError:
            raise HTTPException(status_code=500, detail="AWS credentials not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"S3 Upload failed: {str(e)}")

    @staticmethod
    def generate_presigned_url(s3_key: str, expiration=3600):
        try:
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            return None

    @staticmethod
    def download_from_s3(s3_key: str, local_path: str):
        try:
            s3_client.download_file(S3_BUCKET, s3_key, local_path)
            return True
        except Exception as e:
            return False
