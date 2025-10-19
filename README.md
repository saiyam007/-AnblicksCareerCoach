# -AnblicksCareerCoach
AnblicksCareerCoach  is an intelligent platform powered by AWS Bedrock and LLM Agents. It personalizes career paths, generates smart questions, and builds structured learning roadmaps with location-based salary insights. A stage-based journey guides users from profile creation to skill mastery.


# Backend API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg)](https://python.org/)
[![AWS](https://img.shields.io/badge/AWS-Bedrock%20%7C%20DynamoDB-FF9900.svg)](https://aws.amazon.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://docker.com/)
[![ECS](https://img.shields.io/badge/AWS-ECS%20Fargate-FF9900.svg)](https://aws.amazon.com/ecs/)

## 🚀 Overview

Career Coach AI CoPilot is a production-ready FastAPI backend that provides AI-powered career guidance through personalized assessments, roadmap generation, and skill evaluation. Built with AWS Bedrock for AI capabilities and DynamoDB for data persistence, it offers a complete career coaching experience.

## ✨ Key Features

### 🎯 Core Functionality
- **AI-Powered Career Assessment**: Generate personalized career questions based on user profile
- **Intelligent Roadmap Generation**: Create detailed learning paths with 3-5 career options
- **Comprehensive Skill Evaluation**: Assess user skills with detailed scoring and recommendations
- **User Journey Management**: Track progress through 7 distinct journey stages
- **Google OAuth Integration**: Secure authentication with Google Sign-In

### 🔧 Technical Features
- **Production-Ready Architecture**: Built with FastAPI, containerized with Docker
- **AWS Integration**: Bedrock AI, DynamoDB, ECS Fargate deployment
- **Intelligent Caching**: 95-98% cost reduction through smart content caching
- **Scalable Design**: Auto-scaling ECS services with load balancing
- **Comprehensive Monitoring**: CloudWatch integration with health checks

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Load Balancer │    │   ECS Cluster   │
│   (React/Vue)   │◄──►│   (ALB + SSL)   │◄──►│   (Fargate)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────┐              │
                       │   AWS Bedrock   │◄─────────────┘
                       │   (Claude AI)   │
                       └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   DynamoDB      │
                       │   (Shared DB)   │
                       └─────────────────┘
```

## 📋 Prerequisites

### Development Environment
- **Python 3.11+**
- **Docker & Docker Compose**
- **AWS CLI** (configured with appropriate credentials)
- **Git**

### AWS Services Required
- **DynamoDB**: Tables for user data and career roadmaps
- **Bedrock**: Claude Sonnet 4.5 model for AI generation
- **ECS**: Fargate cluster for container deployment
- **ECR**: Container registry for Docker images
- **Application Load Balancer**: For production traffic routing
- **CloudWatch**: Logging and monitoring

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd Backend

# Copy environment template
cp env-template.txt .env

# Edit .env with your configuration
nano .env
```

### 2. Local Development
```bash
# Start local services (DynamoDB + Backend)
docker-compose up -d

# Verify services
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs
```

### 3. Production Deployment
```bash
# Build and push Docker image
docker build -t career-coach-backend .
docker tag career-coach-backend:latest <ecr-repo-uri>:latest
docker push <ecr-repo-uri>:latest

# Deploy to ECS
aws ecs update-service --cluster career-coach-cluster \
  --service career-coach-backend-service --force-new-deployment
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Deployment environment | `production` |
| `AWS_REGION` | AWS region for services | `us-east-1` |
| `DYNAMODB_TABLE_NAME` | Main users table | `Users` |
| `DYNAMODB_DATA_TABLE_NAME` | Career data table | `career-coach-data` |
| `BEDROCK_MODEL_ID` | Bedrock model ARN | `arn:aws:bedrock:...` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | `your-client-id` |
| `SECRET_KEY` | JWT secret key | `your-secret-key` |

### Database Schema

#### Users Table
```json
{
  "email": "user@example.com",
  "recordId": "PROFILE#LATEST",
  "journey_stage": "ROADMAP_GENERATED",
  "profile_data": { /* user profile */ },
  "created_at": "2025-01-01T00:00:00Z"
}
```

#### Career Coach Data Table
```json
{
  "id": "roadmap-uuid",
  "u_id": "user@example.com",
  "status": "DETAILED_ROADMAP_COMPLETED",
  "questions": "[{ /* generated questions */ }]",
  "roadmap": "{ /* career paths */ }",
  "detailedRoadmap": "{ /* detailed roadmap */ }"
}
```

## 📚 API Documentation

### Authentication Flow
```bash
# 1. Google OAuth Login
POST /v1/auth/google
{
  "id_token": "google-jwt-token"
}

# Response: Access token + user data
```

### User Journey Flow
```bash
# 2. Complete Profile
POST /v1/ai/users/complete-profile
Authorization: Bearer <access_token>
{
  "careerGoal": "AI Engineer",
  "currentEducationLevel": "Master degree",
  "fieldOfStudy": "Computer Science"
}

# 3. Generate Career Questions
POST /v1/ai/profile/questions
Authorization: Bearer <access_token>

# 4. Submit Answers & Get Career Paths
POST /v1/ai/profile/roadmap
Authorization: Bearer <access_token>
[{"id": "q1", "answer": "Yes"}, ...]

# 5. Generate Detailed Roadmap
POST /v1/ai/profile/detailed-roadmap
Authorization: Bearer <access_token>
{
  "selectedCareerPath": { /* selected path object */ }
}
```

### Assessment System
```bash
# Generate Assessment Questions
POST /v1/assessment/generate-questions
{
  "career_goal": "AI Engineer",
  "skill": "Machine Learning",
  "experience": "2 years"
}

# Evaluate Assessment
POST /v1/assessment/evaluate
{
  "responses": [{"id": 1, "user_answer": "A"}, ...]
}
```

### User State Management
```bash
# Check Current Journey State
GET /v1/users/me/state
Authorization: Bearer <access_token>
```

## 🔄 User Journey Stages

| Stage | Description | Next Action |
|-------|-------------|-------------|
| `AUTHENTICATED` | User logged in | Complete profile |
| `BASIC_REGISTERED` | Profile completed | Generate questions |
| `PROFILE_COMPLETED` | Questions answered | Select career path |
| `CAREER_PATHS_GENERATED` | Paths available | Generate detailed roadmap |
| `ROADMAP_GENERATED` | Detailed roadmap ready | Start learning journey |
| `ROADMAP_ACTIVE` | Journey in progress | Continue learning |
| `JOURNEY_COMPLETED` | Journey finished | Explore new skills |

## ⚡ Performance & Caching

### Caching Strategy
- **Questions Endpoint**: ✅ Cached (10x faster on repeat calls)
- **Career Paths**: ✅ Cached (16x faster on repeat calls)
- **Detailed Roadmap**: ❌ Always fresh (latest AI capabilities)

### Performance Metrics
- **Questions Generation**: 3-5 seconds (first), 200-500ms (cached)
- **Career Paths**: 5-8 seconds (first), 200-500ms (cached)
- **Detailed Roadmap**: 30-45 seconds (always fresh)
- **Cost Savings**: 95-98% reduction for cached endpoints

## 🐳 Docker Deployment

### Local Development
```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Production Build
```bash
# Build optimized image
docker build -t career-coach-backend:prod .

# Run with production settings
docker run -d \
  --name career-coach-backend \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  career-coach-backend:prod
```

## ☁️ AWS ECS Deployment

### Task Definition
```json
{
  "family": "career-coach-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "account.dkr.ecr.region.amazonaws.com/career-coach-backend:latest",
      "portMappings": [{"containerPort": 8000}],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "AWS_REGION", "value": "us-east-1"}
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

### Auto Scaling Configuration
```bash
# Create auto scaling target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/career-coach-cluster/career-coach-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/career-coach-cluster/career-coach-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name career-coach-backend-cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    }
  }'
```

## 🔒 Security

### Authentication & Authorization
- **JWT Tokens**: Secure token-based authentication
- **Google OAuth**: Industry-standard OAuth 2.0 integration
- **Role-Based Access**: User role management
- **Token Expiration**: Configurable token lifetimes

### Production Security Checklist
- [ ] Strong JWT secret keys (256-bit)
- [ ] HTTPS enforcement in production
- [ ] CORS properly configured for production domains
- [ ] Environment variables secured (no hardcoded secrets)
- [ ] Regular security updates for dependencies
- [ ] AWS IAM roles with least privilege access
- [ ] CloudWatch monitoring for security events

### CORS Configuration
```python
# Development
CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5173"]

# Production
CORS_ORIGINS = ["https://yourdomain.com"]
```

## 📊 Monitoring & Observability

### CloudWatch Integration
- **Log Groups**: `/ecs/career-coach-backend`
- **Metrics**: CPU, Memory, Request count, Error rate
- **Alarms**: Automated alerting for critical issues

### Health Checks
```bash
# Application health
curl https://your-domain.com/health

# Detailed health with dependencies
curl https://your-domain.com/health/detailed
```

### Key Metrics to Monitor
- **Response Time**: P95 < 5 seconds
- **Error Rate**: < 1%
- **CPU Utilization**: < 80%
- **Memory Usage**: < 80%
- **DynamoDB Read/Write**: Monitor throttling
- **Bedrock API Calls**: Track usage and costs

### Logging Strategy
```python
# Structured JSON logging
{
  "timestamp": "2025-01-01T12:00:00Z",
  "level": "INFO",
  "service": "career-coach-backend",
  "request_id": "uuid",
  "user_id": "user@example.com",
  "endpoint": "/v1/ai/profile/questions",
  "duration_ms": 2500,
  "status_code": 200
}
```

## 🧪 Testing

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Authentication test
curl -X POST http://localhost:8000/v1/auth/google \
  -H "Content-Type: application/json" \
  -d '{"id_token": "your-google-token"}'

# API documentation
open http://localhost:8000/docs
```

### Load Testing
```bash
# Install artillery
npm install -g artillery

# Run load test
artillery quick --count 100 --num 10 http://localhost:8000/health
```

## 🔧 Development

```
## 🏗️ Project Architecture

```
├── Backend
│   ├── examples/                    # Example docs & references
│   ├── logs/                        # Log files
│   ├── scripts/                     # Deployment or utility scripts
│   ├── src/
│   │   ├── api/
│   │   │   ├── agents/             # AI/LLM agent integrations
│   │   │   ├── core/               # Core app logic & configs
│   │   │   ├── models/             # ORM / DB models
│   │   │   ├── routes/             # FastAPI routes
│   │   │   ├── schemas/            # Pydantic request/response schemas
│   │   │   ├── services/           # Business logic layer
│   │   │   ├── utils/              # Helpers, error handlers, logging
│   │   ├── main.py                 # Application entrypoint
│   │   └── __init__.py
│   ├── .dockerignore
│   ├── .gitignore
│   ├── API_DOCUMENTATION.md
│   ├── ASSESSMENT_API_GUIDE.md
│   ├── DEPLOYMENT.md
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── env-template.txt
│   └── requirements.txt
│
├── Frontend
│   ├── public/
│   │   └── assets/
│   ├── src/
│   │   ├── common/
│   │   │   ├── services/           # API services
│   │   │   ├── constant.ts
│   │   │   ├── http.ts
│   │   │   ├── urls.ts
│   │   │   └── util.ts
│   │   ├── components/
│   │   │   ├── figma/             # UI assets or components from Figma
│   │   │   └── ui/                # Reusable UI components
│   │   ├── hooks/
│   │   │   └── useLoading.tsx
│   │   ├── styles/
│   │   │   └── globals.css
│   │   ├── App.tsx
│   │   ├── index.css
│   │   └── main.tsx
│   ├── buildspec.yml
│   ├── dockerfile
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── README.md
│   └── vite.config.ts
│
├── imagedefinitions-fe.json        # Frontend image definition for deployment
├── imagedefinitions.json           # Backend image definition for deployment
└── project_structure.txt

```


## 🧠 Core Features

### 1. 🔐 **User Journey & Stage Flow**

| Stage                    | Description                                                    | Actions Available                                               |
|---------------------------|-----------------------------------------------------------------|------------------------------------------------------------------|
| `AUTHENTICATED`           | User just logged in                                            | Complete registration                                           |
| `BASIC_REGISTERED`        | Basic profile created                                          | Generate questions, update registration                          |
| `PROFILE_COMPLETED`       | Profile ready                                                  | Answer questions, regenerate questions                           |
| `CAREER_PATHS_GENERATED`  | Career paths created                                           | Select career path                                              |
| `CAREER_PATH_SELECTED`    | Career path stored in DB                                       | View detailed roadmap                                           |
| `ROADMAP_GENERATED`       | Full roadmap generated                                        | Start journey, view roadmap                                     |
| `ROADMAP_ACTIVE`          | User actively learning                                       | Track progress, pause journey                                   |
| `JOURNEY_PAUSED`          | User paused their journey                                    | Resume journey                                                  |
| `JOURNEY_COMPLETED`       | Journey done                                                 | View certificate, start new journey                             |

---

### 2. 🧭 **AI Workflow**

```
1. /v1/ai/profile/questions              → Generate career questions
2. /v1/ai/profile/roadmap                → Generate 3 career paths
3. /v1/ai/profile/selected-career-path   → Save chosen path + stage update
4. /v1/ai/profile/detailed-roadmap       → Generate full roadmap
```

**LLM Powered Components**
- Uses AWS Bedrock (Anthropic Claude) via Bedrock Runtime
- Uses Bedrock Agent Runtime for detailed roadmap
- Token optimization (lower cost, high determinism)
- Location-aware salary estimation

---

## 🧰 Tech Stack

| Component                | Technology                                   |
|---------------------------|-----------------------------------------------|
| **Backend Framework**     | [FastAPI](https://fastapi.tiangolo.com/)     |
| **Language**              | Python 3.11+                                 |
| **LLM Provider**          | [AWS Bedrock](https://aws.amazon.com/bedrock/) |
| **LLM Model**             | Anthropic Claude Sonnet / Bedrock Agent     |
| **Auth**                  | JWT + FastAPI dependencies                  |
| **Database**              | DynamoDB / Postgres (for journey state)     |
| **Logging**               | Custom logging via `errorHandler.py`        |

---

## ⚡ Getting Started

### 1. 🧭 Prerequisites

- Python 3.11+
- AWS account with Bedrock access
- Valid IAM credentials
- DynamoDB or PostgreSQL (depending on your setup)

### 2. 📦 Clone the Repo

```bash
git clone https://github.com/saiyam007/-AnblicksCareerCoach/tree/main
cd CareerCoachAICopilotAWSHackathon
```

### 3. 🧪 Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

### 4. 📥 Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. 🧰 Environment Variables

Create a `.env` file (based on `.env-template.txt`):

```
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-2
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
BEDROCK_AGENT_ID=FDZUGFEXL2
BEDROCK_AGENT_ALIAS_ID=YE8F8TRXUI
```

---

## 🧪 Running the Server
go to  base folder 

D:\CareerCoachAICopilotAWSHackathon\CareerCoachAICopilotAWSHackathon\Backend


```bash
uvicorn app.main:app --reload
```

➡️ The API will be available at:  
👉 `http://127.0.0.1:8000`

➡️ For Swagger: 
👉 `http://127.0.0.1:8000/docs`


```

### Adding New Features
1. **Create Route**: Add endpoint in `api/routes/`
2. **Add Service**: Implement business logic in `api/services/`
3. **Define Schema**: Create Pydantic models in `api/models/`
4. **Update Tests**: Add test cases in `tests/`
5. **Update Documentation**: Update API docs and README

### Code Quality
```bash
# Format code
black src/

# Type checking
mypy src/

# Linting
flake8 src/

# Run tests
pytest tests/
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check ECS service events
aws ecs describe-services --cluster career-coach-cluster \
  --services career-coach-backend-service

# Check container logs
aws logs get-log-events --log-group-name /ecs/career-coach-backend \
  --log-stream-name ecs/backend/task-id
```

#### 2. Database Connection Issues
```bash
# Test DynamoDB connectivity
aws dynamodb describe-table --table-name Users --region us-east-1

# Check IAM permissions
aws iam get-role --role-name ecsTaskRole
```

#### 3. AI Generation Failures
```bash
# Check Bedrock model access
aws bedrock list-foundation-models --region us-east-2

# Verify model ID
aws bedrock get-model --model-id claude-3-sonnet-20240229-v1:0
```

#### 4. Authentication Issues
```bash
# Verify Google OAuth configuration
curl -X POST https://oauth2.googleapis.com/token \
  -d "client_id=YOUR_CLIENT_ID&client_secret=YOUR_SECRET"

# Check JWT token validity
python -c "import jwt; jwt.decode('your-token', verify=False)"
```

### Debug Mode
```bash
# Enable debug logging
export DEBUG=True
export LOG_LEVEL=DEBUG

# Run with debug mode
docker run -e DEBUG=True -e LOG_LEVEL=DEBUG career-coach-backend
```

## 📈 Scaling Considerations

### Horizontal Scaling
- **ECS Auto Scaling**: 2-10 containers based on load
- **Load Balancer**: Distribute traffic across instances
- **DynamoDB**: Auto-scaling read/write capacity
- **Bedrock**: Rate limiting and quota management

### Performance Optimization
- **Caching**: Redis for session data (optional)
- **Connection Pooling**: Reuse database connections
- **Async Processing**: Background tasks for heavy operations
- **CDN**: Static content delivery

### Cost Optimization
- **Spot Instances**: Use spot instances for non-critical workloads
- **Reserved Capacity**: DynamoDB reserved capacity for predictable workloads
- **Bedrock Optimization**: Cache AI responses, batch requests
- **Monitoring**: Regular cost analysis and optimization

## 🤝 Contributing

### Development Workflow
1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** Pull Request

### Code Standards
- Follow PEP 8 Python style guide
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PR

## 📞 Support

### Getting Help
- **Documentation**: Check this README and API docs
- **Issues**: Create GitHub issues for bugs and feature requests
- **Monitoring**: Check CloudWatch logs for runtime issues
- **AWS Support**: For infrastructure-related problems

### Emergency Contacts
- **Production Issues**: Check CloudWatch alarms first
- **Database Issues**: Verify DynamoDB service status
- **AI Service Issues**: Check Bedrock service health
- **Deployment Issues**: Review ECS service events

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** - Modern, fast web framework for building APIs
- **AWS Bedrock** - AI foundation model service
- **AWS DynamoDB** - NoSQL database service
- **Google OAuth** - Secure authentication service

---

# Frontend 

**Built with ❤️ for career development and AI-powered guidance**

🚀 React + Vite + TypeScript Project

This project is built using React, Vite, and TypeScript — providing a fast, modern frontend development environment.

📦 Prerequisites

Make sure you have the following installed:

Node.js
(version 20 or higher recommended)

npm
or yarn
or pnpm

⚙️ Setup Instructions

1. Clone the Repository
   cd <project-folder>

2. Install Dependencies
   npm install

or

yarn install

🧩 Environment Variables

Create a .env file in the root directory of your project and add the following variables:

# Backend API URL

VITE_API_URL=https://api.example.com

# Google OAuth Client ID

VITE_GOOGLE_CLIENT_ID=your-google-client-id-here


🏃‍♂️ Run the Development Server

To start the app in development mode:

npm run dev

or

yarn dev

This will start the Vite dev server (default at http://localhost:5173
).

🏗️ Build for Production

To create a production build:

npm run build

or

yarn build

The built files will be located in the dist/ folder.

🧰 Scripts Summary
Command Description
npm run dev Run the app in development mode
npm run build Build the app for production


