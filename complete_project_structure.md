# Single Cell RNA Analysis Platform - Complete Code

## Project Directory Structure

```
scrna-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── uploads.py
│   │   │   ├── jobs.py
│   │   │   └── billing.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   └── job.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   └── job.py
│   │   └── tasks/
│   │       ├── __init__.py
│   │       └── analysis.py
│   ├── alembic/
│   │   └── versions/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env
│   └── alembic.ini
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.tsx
│   │   │   ├── Navbar.tsx
│   │   │   └── UploadZone.tsx
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── UploadData.tsx
│   │   │   ├── JobList.tsx
│   │   │   ├── JobDetails.tsx
│   │   │   └── Billing.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   ├── index.tsx
│   │   └── index.css
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── Dockerfile
├── nginx/
│   ├── nginx.conf
│   └── ssl/
├── scripts/
│   ├── clustering.R
│   ├── annotation.py
│   └── differential_expression.R
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## File Contents

### Root Level Files

#### `docker-compose.yml`
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: scrna_postgres
    environment:
      POSTGRES_USER: scrna_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-change_me_in_production}
      POSTGRES_DB: scrna_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U scrna_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: scrna_redis
    ports:
      - "6379:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    container_name: scrna_backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
      - upload_data:/data/uploads
      - output_data:/data/outputs
      - ./scripts:/app/scripts
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://scrna_user:${POSTGRES_PASSWORD:-change_me_in_production}@postgres:5432/scrna_db
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY:-your-secret-key-change-in-production}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}
      - MAX_UPLOAD_SIZE=5368709120
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  celery_worker:
    build: ./backend
    container_name: scrna_celery_worker
    command: celery -A app.tasks.analysis worker --loglevel=info --concurrency=4
    volumes:
      - ./backend:/app
      - upload_data:/data/uploads
      - output_data:/data/outputs
      - ./scripts:/app/scripts
    environment:
      - DATABASE_URL=postgresql://scrna_user:${POSTGRES_PASSWORD:-change_me_in_production}@postgres:5432/scrna_db
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY:-your-secret-key-change-in-production}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  celery_beat:
    build: ./backend
    container_name: scrna_celery_beat
    command: celery -A app.tasks.analysis beat --loglevel=info
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgresql://scrna_user:${POSTGRES_PASSWORD:-change_me_in_production}@postgres:5432/scrna_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: scrna_frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    stdin_open: true
    tty: true
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: scrna_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
    profiles:
      - production

volumes:
  postgres_data:
  upload_data:
  output_data:
```

#### `.env.example`
```bash
# Database
POSTGRES_PASSWORD=your_secure_database_password

# Security
SECRET_KEY=generate-a-long-random-string-at-least-32-characters

# Stripe (get from https://stripe.com)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Application
MAX_UPLOAD_SIZE=5368709120
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

#### `README.md`
```markdown
# Single Cell RNA Analysis Platform

## Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in values
3. Run: `docker-compose up -d`
4. Access: http://localhost:3000

## Documentation

See docs/ folder for detailed setup instructions.
```

---

## Backend Files

### `backend/Dockerfile`
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    r-base \
    r-base-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    libpq-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install R packages
RUN R -e "install.packages(c('Seurat', 'dplyr', 'ggplot2', 'jsonlite', 'optparse'), repos='http://cran.rstudio.com/')"

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p /data/uploads /data/outputs

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `backend/requirements.txt`
```
# FastAPI and ASGI server
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.1.2

# Celery and Redis
celery==5.3.6
redis==5.0.1

# Payment processing
stripe==7.11.0

# File handling
aiofiles==23.2.1
python-magic==0.4.27

# Data validation
pydantic==2.5.3
pydantic-settings==2.1.0
email-validator==2.1.0

# Utilities
python-dotenv==1.0.0
pandas==2.1.4
numpy==1.26.3

# Monitoring
prometheus-client==0.19.0
```

### `backend/app/__init__.py`
```python
"""Single Cell RNA Analysis Platform"""
__version__ = "0.1.0"
```

### `backend/app/main.py`
```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os

app = FastAPI(
    title="Single Cell RNA Analysis Platform",
    description="API for single-cell RNA sequencing data analysis",
    version="0.1.0"
)

# CORS middleware
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

@app.get("/")
async def root():
    return {
        "message": "Single Cell RNA Analysis Platform API",
        "version": "0.1.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Import and include routers
from app.api import auth, users, uploads, jobs, billing

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["File Uploads"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Analysis Jobs"])
app.include_router(billing.router, prefix="/api/billing", tags=["Billing"])

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    from app.core.database import engine
    from app.models.user import Base
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### `backend/app/core/database.py`
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://scrna_user:password@localhost:5432/scrna_db"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### `backend/app/core/security.py`
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os

from app.core.database import get_db
from app.models.user import User

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user
```

### `backend/app/core/config.py`
```python
import os
from typing import List

class Settings:
    """Application settings"""
    
    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Single Cell RNA Analysis Platform"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://scrna_user:password@localhost:5432/scrna_db")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # File Storage
    UPLOAD_DIR: str = "/data/uploads"
    OUTPUT_DIR: str = "/data/outputs"
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", 5 * 1024 * 1024 * 1024))  # 5GB
    
    # Stripe
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    
    # Subscription Limits
    SUBSCRIPTION_LIMITS = {
        "free": {
            "storage_gb": 10,
            "cpu_hours_monthly": 10,
            "concurrent_jobs": 1,
            "max_file_size_gb": 1
        },
        "basic": {
            "storage_gb": 100,
            "cpu_hours_monthly": 100,
            "concurrent_jobs": 3,
            "max_file_size_gb": 5
        },
        "pro": {
            "storage_gb": 500,
            "cpu_hours_monthly": 500,
            "concurrent_jobs": 10,
            "max_file_size_gb": 10
        },
        "enterprise": {
            "storage_gb": 5000,
            "cpu_hours_monthly": 5000,
            "concurrent_jobs": 50,
            "max_file_size_gb": 50
        }
    }

settings = Settings()
```

### `backend/app/models/__init__.py`
```python
from app.models.user import User, SubscriptionTier
from app.models.job import AnalysisJob, JobStatus, Payment

__all__ = ["User", "SubscriptionTier", "AnalysisJob", "JobStatus", "Payment"]
```

### `backend/app/models/user.py`
```python
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base

class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

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
    compute_hours_used_this_month = Column(Float, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jobs = relationship("AnalysisJob", back_populates="user", cascade="all, delete-orphan")
```

### `backend/app/models/job.py`
```python
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Job details
    job_name = Column(String, nullable=False)
    job_type = Column(String, nullable=False)  # clustering, annotation, differential_expression
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, index=True)
    
    # File paths
    input_file_path = Column(String, nullable=False)
    output_directory = Column(String, nullable=True)
    
    # Parameters (stored as JSON string)
    parameters = Column(Text, nullable=True)
    
    # Resource usage
    cpu_hours = Column(Float, default=0)
    memory_peak_gb = Column(Float, default=0)
    
    # Timing
    submitted_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Results
    result_summary = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Progress tracking
    progress_percent = Column(Integer, default=0)
    current_step = Column(String, nullable=True)
    
    # Celery task ID
    celery_task_id = Column(String, nullable=True)
    
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
```

### `backend/app/api/__init__.py`
```python
"""API routers"""
```

### `backend/app/api/auth.py`
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_HOURS
)
from app.models.user import User

router = APIRouter()

# Schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str | None = None

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str | None
    subscription_tier: str
    is_active: bool
    storage_used_mb: float
    compute_hours_used: float
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password)
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    
    # Find user
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/logout")
async def logout():
    """Logout (client should delete token)"""
    return {"message": "Successfully logged out"}
```

### `backend/app/api/users.py`
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.job import AnalysisJob, JobStatus

router = APIRouter()

@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user statistics"""
    
    # Count jobs by status
    total_jobs = db.query(func.count(AnalysisJob.id)).filter(
        AnalysisJob.user_id == current_user.id
    ).scalar()
    
    running_jobs = db.query(func.count(AnalysisJob.id)).filter(
        AnalysisJob.user_id == current_user.id,
        AnalysisJob.status == JobStatus.RUNNING
    ).scalar()
    
    completed_jobs = db.query(func.count(AnalysisJob.id)).filter(
        AnalysisJob.user_id == current_user.id,
        AnalysisJob.status == JobStatus.COMPLETED
    ).scalar()
    
    failed_jobs = db.query(func.count(AnalysisJob.id)).filter(
        AnalysisJob.user_id == current_user.id,
        AnalysisJob.status == JobStatus.FAILED
    ).scalar()
    
    return {
        "total_jobs": total_jobs or 0,
        "running_jobs": running_jobs or 0,
        "completed_jobs": completed_jobs or 0,
        "failed_jobs": failed_jobs or 0,
        "storage_used_mb": current_user.storage_used_mb,
        "compute_hours_used": current_user.compute_hours_used
    }
```

### `backend/app/api/uploads.py`
```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
import os
import shutil
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User

router = APIRouter()

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a count matrix file"""
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE / (1024**3):.2f} GB"
        )
    
    # Check user quota
    limits = settings.SUBSCRIPTION_LIMITS[current_user.subscription_tier]
    storage_used_gb = current_user.storage_used_mb / 1024
    
    if storage_used_gb + (file_size / (1024**3)) > limits["storage_gb"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Storage quota exceeded. Your plan allows {limits['storage_gb']} GB"
        )
    
    # Create user upload directory
    user_upload_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id))
    os.makedirs(user_upload_dir, exist_ok=True)
    
    # Save file
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(user_upload_dir, filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    