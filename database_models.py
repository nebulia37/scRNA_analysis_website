from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Subscription info
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    subscription_expires = Column(DateTime, nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    
    # Usage tracking
    storage_used_mb = Column(Float, default=0)
    compute_hours_used = Column(Float, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jobs = relationship("AnalysisJob", back_populates="user", cascade="all, delete-orphan")

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Job details
    job_name = Column(String, nullable=False)
    job_type = Column(String, nullable=False)  # clustering, annotation, differential_expression, etc.
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    
    # File paths
    input_file_path = Column(String, nullable=False)
    output_directory = Column(String, nullable=True)
    
    # Parameters (stored as JSON string)
    parameters = Column(Text, nullable=True)
    
    # Resource usage
    cpu_hours = Column(Float, default=0)
    memory_peak_gb = Column(Float, default=0)
    
    # Timing
    submitted_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Results
    result_summary = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Progress tracking
    progress_percent = Column(Integer, default=0)
    current_step = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="jobs")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    amount = Column(Float, nullable=False)
    currency = Column(String, default="usd")
    
    stripe_payment_intent_id = Column(String, unique=True)
    stripe_invoice_id = Column(String, nullable=True)
    
    status = Column(String, nullable=False)  # succeeded, pending, failed
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)