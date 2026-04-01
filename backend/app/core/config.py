import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FixMyPaper"
    
    # AWS Region
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")

    # AWS Cognito
    COGNITO_USER_POOL_ID: str = os.getenv("COGNITO_USER_POOL_ID")
    COGNITO_CLIENT_ID: str = os.getenv("COGNITO_CLIENT_ID")
    
    # AWS S3
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME")
    
    # AWS DynamoDB
    DYNAMODB_TABLE: str = os.getenv("DYNAMODB_TABLE", "fixmypaper-jobs")

    # AWS Step Functions
    STEP_FUNCTIONS_ARN: str = os.getenv("STEP_FUNCTIONS_ARN")

    # AWS SQS
    SQS_QUEUE_URL: str = os.getenv("SQS_QUEUE_URL")
    
    # AI Services
    GROBID_URL: str = os.getenv("GROBID_URL", "http://localhost:8070")

settings = Settings()
