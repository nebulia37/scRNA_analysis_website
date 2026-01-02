from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import os

app = FastAPI(title="Single Cell RNA Analysis Platform")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

@app.get("/")
async def root():
    return {"message": "Single Cell RNA Analysis Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Import routers
from app.api import auth, users, uploads, jobs, billing

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["Uploads"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Analysis Jobs"])
app.include_router(billing.router, prefix="/api/billing", tags=["Billing"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)