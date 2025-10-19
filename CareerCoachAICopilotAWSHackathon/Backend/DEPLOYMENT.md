#  Career Coach AI Copilot - ECS Deployment Guide

##  Overview

This guide covers deploying the Career Coach AI Copilot API to AWS ECS (Elastic Container Service) using Docker containers.

### 🗄️ Database Strategy
- **Shared Database**: All environments (Local, Development, Production) use the same DynamoDB tables
- **Local**: Docker DynamoDB (`http://localhost:8001`)
- **AWS**: Shared DynamoDB tables (`Users`, `career-coach-data`) in `us-east-1`

## 🛠️ Prerequisites

1. **AWS CLI** installed and configured
   ```bash
   aws configure
   ```

2. **Docker** installed and running
   ```bash
   docker --version
   docker-compose --version
   ```

3. **Python 3.11** (for local development)

4. **ECS Cluster** created in AWS Console

##  Quick Deployment

### 1. Build and Push Docker Image
```bash
# Build the Docker image
docker build -t career-coach-backend .

# Tag for ECR
docker tag career-coach-backend:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/career-coach-backend:latest

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Push to ECR
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/career-coach-backend:latest
```

### 2. Deploy to ECS
```bash
# Update ECS service with new image
aws ecs update-service --cluster career-coach-cluster --service career-coach-backend-service --force-new-deployment
```

## 📁 File Structure

```
Backend/
├── Dockerfile             # ECS container definition
├── .dockerignore          # Docker ignore file
├── docker-compose.yml     # Local development
├── env-template.txt       # Environment configuration template
├── requirements.txt       # Python dependencies (mangum removed)
└── DEPLOYMENT.md          # This file
```

## 🌍 Environment Configuration

### Local Development
- **Database**: Docker DynamoDB (`http://localhost:8001`)
- **Backend**: FastAPI server (`http://localhost:8000`)
- **CORS**: `localhost:3000`, `localhost:5173`

### Development (AWS ECS)
- **Database**: AWS DynamoDB (shared tables)
- **Backend**: ECS Fargate containers
- **Load Balancer**: Application Load Balancer
- **CORS**: Dev domain + localhost for testing

### Production (AWS ECS)
- **Database**: AWS DynamoDB (shared tables)
- **Backend**: ECS Fargate containers
- **Load Balancer**: Application Load Balancer with SSL
- **CORS**: Production domain only
- **Auto Scaling**: 2-10 containers based on load

## 🐳 Local Development

### Start Local Services
```bash
# Start DynamoDB and Backend
docker-compose up -d

# Check services
docker-compose ps

# View logs
docker-compose logs -f backend
```

### Initialize Database
```bash
# Run initialization script
python scripts/init_registration_table.py
```

### Test API
```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

## ☁️ ECS Deployment

### 1. ECR Repository Setup
```bash
# Create ECR repository
aws ecr create-repository --repository-name career-coach-backend --region us-east-1
```

### 2. ECS Task Definition

#### Create Task Definition (JSON)
```json
{
  "family": "career-coach-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::123456789:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/career-coach-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        },
        {
          "name": "AWS_REGION",
          "value": "us-east-2"
        },
        {
          "name": "DYNAMODB_TABLE_NAME",
          "value": "Users"
        },
        {
          "name": "DYNAMODB_DATA_TABLE_NAME",
          "value": "career-coach-data"
        },
        {
          "name": "BEDROCK_MODEL_ID",
          "value": "arn:aws:bedrock:us-east-2:689960076039:inference-profile/global.anthropic.claude-sonnet-4-5-20250929-v1:0"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/career-coach-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
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

### 3. ECS Service Configuration
```bash
# Create ECS service
aws ecs create-service \
  --cluster career-coach-cluster \
  --service-name career-coach-backend-service \
  --task-definition career-coach-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-12345],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789:targetgroup/career-coach-tg/12345,containerName=backend,containerPort=8000"
```

## 🔧 Configuration Parameters

### ECS Task Definition
- **CPU**: 512 (0.5 vCPU)
- **Memory**: 1024 MB
- **Desired Count**: 2 (for high availability)
- **Launch Type**: FARGATE

### Auto Scaling
- **Min Capacity**: 2
- **Max Capacity**: 10
- **Target CPU**: 70%
- **Target Memory**: 80%

### Load Balancer
- **Type**: Application Load Balancer
- **Health Check**: `/health` endpoint
- **SSL Certificate**: Required for production

## 🧪 Testing Deployment

### Health Check
```bash
curl https://your-alb-dns-name/api/v1/auth/health
```

### API Documentation
Visit: `https://your-alb-dns-name/docs`

## 🔍 Monitoring

### CloudWatch Logs
- **Log Group**: `/ecs/career-coach-backend`
- **Stream**: `ecs/backend/{task-id}`

### CloudWatch Alarms (Production)
- **Error Rate**: > 5 errors in 5 minutes
- **CPU Usage**: > 80% for 5 minutes
- **Memory Usage**: > 80% for 5 minutes

## 🗄️ Database Tables

Both environments use the same DynamoDB tables:

1. **Users** (`us-east-1`)
   - Partition Key: `email`
   - Sort Key: `recordId` = "PROFILE#LATEST"

2. **career-coach-data** (`us-east-1`)
   - Partition Key: `id`
   - Sort Key: `u_id`

## 🔒 Security

### IAM Permissions
- DynamoDB read/write access to shared tables
- Bedrock AI model invocation
- CloudWatch logs
- ECR image pull

### CORS Configuration
- **Development**: Permissive (includes localhost)
- **Production**: Restricted to production domain only

## 🚨 Troubleshooting

### Common Issues

1. **Container Won't Start**
   ```bash
   # Check ECS service events
   aws ecs describe-services --cluster career-coach-cluster --services career-coach-backend-service
   
   # Check task logs
   aws logs get-log-events --log-group-name /ecs/career-coach-backend --log-stream-name ecs/backend/task-id
   ```

2. **Health Check Failures**
   ```bash
   # Check container health
   aws ecs describe-tasks --cluster career-coach-cluster --tasks task-id
   ```

3. **Database Connection Issues**
   ```bash
   # Test from container
   aws ecs execute-command \
     --cluster career-coach-cluster \
     --task task-id \
     --container backend \
     --interactive \
     --command "/bin/bash"
   ```

### Useful Commands

```bash
# Check ECS service status
aws ecs describe-services --cluster career-coach-cluster --services career-coach-backend-service

# View recent logs
aws logs tail /ecs/career-coach-backend --follow

# Update service
aws ecs update-service --cluster career-coach-cluster --service career-coach-backend-service --force-new-deployment

# Scale service
aws ecs update-service --cluster career-coach-cluster --service career-coach-backend-service --desired-count 3
```

## 📞 Support

For deployment issues:
1. Check CloudWatch logs
2. Verify ECS service events
3. Test container connectivity
4. Review IAM permissions
5. Check AWS service status
6. Use ECS exec for debugging