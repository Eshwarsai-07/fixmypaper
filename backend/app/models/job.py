from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, default="pending")  # pending, processing, completed, failed, partial_success
    
    # Latency Metrics
    created_at = Column(DateTime, default=datetime.utcnow)
    processing_started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # File info
    filename = Column(String)
    s3_key = Column(String)
    result_s3_key = Column(String, nullable=True)

    # Job Metrics/Tracking
    retry_count = Column(Integer, default=0)
    module_status = Column(JSON, default={})
    error_message = Column(Text, nullable=True)

    # Results
    statistics = Column(JSON, default={})
