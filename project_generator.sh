#!/bin/bash

# Single Cell RNA Analysis Platform - Project Generator
# This script creates the complete project structure with all files

set -e

PROJECT_NAME="scrna-platform"
echo "🚀 Creating $PROJECT_NAME..."

# Create main directory
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p backend/app/{api,core,models,schemas,tasks}
mkdir -p backend/alembic/versions
mkdir -p frontend/src/{components,contexts,pages,services}
mkdir -p frontend/public
mkdir -p nginx/ssl
mkdir -p scripts
mkdir -p data/{uploads,outputs}

# Initialize Python __init__.py files
touch backend/app/__init__.py
touch backend/app/api/__init__.py
touch backend/app/core/__init__.py
touch backend/app/models/__init__.py
touch backend/app/schemas/__init__.py
touch backend/app/tasks/__init__.py

echo "✅ Directory structure created"

echo "
📝 Next steps:

1. Copy all the code from the artifacts (blue boxes on the right) into the appropriate files:
   
   BACKEND FILES:
   - backend/Dockerfile
   - backend/requirements.txt
   - backend/app/main.py
   - backend/app/core/database.py
   - backend/app/core/security.py
   - backend/app/core/config.py
   - backend/app/models/user.py
   - backend/app/models/job.py
   - backend/app/api/auth.py
   - backend/app/api/users.py
   - backend/app/api/uploads.py
   - backend/app/api/jobs.py
   - backend/app/api/billing.py
   - backend/app/tasks/analysis.py

   FRONTEND FILES:
   - frontend/Dockerfile
   - frontend/package.json
   - frontend/src/App.tsx
   - frontend/src/index.tsx
   - frontend/src/contexts/AuthContext.tsx
   - frontend/src/pages/Dashboard.tsx
   - frontend/src/pages/Login.tsx
   - frontend/src/pages/Register.tsx
   - frontend/src/pages/UploadData.tsx
   - frontend/src/pages/JobList.tsx
   - frontend/src/pages/JobDetails.tsx
   - frontend/src/components/Layout.tsx

   ROOT FILES:
   - docker-compose.yml
   - .env (copy from .env.example)
   - nginx/nginx.conf

2. Create .env file:
   cp .env.example .env
   # Edit .env with your settings

3. Start the platform:
   docker-compose up -d

4. Access:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

Project structure created at: $(pwd)
"

# Create a simple .env.example
cat > .env.example << 'EOF'
# Database
POSTGRES_PASSWORD=your_secure_database_password

# Security
SECRET_KEY=generate-a-long-random-string-at-least-32-characters

# Stripe
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Application
MAX_UPLOAD_SIZE=5368709120
ALLOWED_ORIGINS=http://localhost:3000
EOF

# Create README
cat > README.md << 'EOF'
# Single Cell RNA Analysis Platform

## Features
- User authentication and authorization
- File upload for count matrices
- Job queue system for analysis
- Clustering, cell type annotation, differential expression
- Subscription tiers with usage quotas
- Payment integration (Stripe)

## Quick Start

1. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

2. Start services:
```bash
docker-compose up -d
```

3. Access the platform:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

## Documentation

See the artifacts in the Claude conversation for complete code for each file.

## Your Analysis Scripts

Place your R/Python analysis scripts in the `scripts/` directory:
- scripts/clustering.R
- scripts/annotation.py
- scripts/differential_expression.R

Make sure they accept command-line arguments as shown in the examples.
EOF

echo "✅ Project structure created successfully!"
echo "📍 Location: $(pwd)"
