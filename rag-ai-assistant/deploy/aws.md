# AWS Deployment Guide

This app is container-ready and can be deployed several ways on AWS. The most straightforward production path is Amazon ECS Fargate with an Application Load Balancer.

## Recommended Architecture

- Amazon ECR for Docker image storage.
- Amazon ECS Fargate for running the Streamlit container.
- Application Load Balancer for public HTTPS access.
- AWS Secrets Manager or SSM Parameter Store for API keys.
- EFS volume if you want ChromaDB persistence across container restarts.

## 1. Build And Test Locally

```powershell
docker compose up --build
```

Visit `http://localhost:8501`.

## 2. Push Image To ECR

Replace the placeholders with your AWS account ID, region, and repository name.

```bash
aws ecr create-repository --repository-name rag-ai-assistant
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
docker build -t rag-ai-assistant .
docker tag rag-ai-assistant:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/rag-ai-assistant:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/rag-ai-assistant:latest
```

## 3. Create Secrets

Store only the provider key you need.

```bash
aws secretsmanager create-secret --name rag-ai-assistant/GOOGLE_API_KEY --secret-string "your_key"
aws secretsmanager create-secret --name rag-ai-assistant/OPENAI_API_KEY --secret-string "your_key"
```

## 4. ECS Task Definition

Container settings:

- Image: `ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/rag-ai-assistant:latest`
- Port mapping: `8501`
- CPU/Memory: start with `1 vCPU / 2 GB`
- Environment:
  - `LLM_PROVIDER=gemini` or `LLM_PROVIDER=openai`
  - `CHROMA_DB_DIR=/app/chroma_db`
  - `COLLECTION_NAME=rag_assistant`
- Secrets:
  - `GOOGLE_API_KEY` or `OPENAI_API_KEY`

For persistent vector storage, mount an EFS volume at `/app/chroma_db`.

## 5. ECS Service

- Launch type: Fargate
- Desired tasks: `1`
- Load balancer target port: `8501`
- Health check path: `/_stcore/health`

## Lower-Friction Alternatives

- AWS App Runner: easiest managed container deployment, but persistent local ChromaDB storage is limited.
- EC2: simplest for a student/demo deployment. Install Docker, clone the project, create `.env`, and run `docker compose up -d --build`.

## Production Improvements

- Add authentication before exposing company documents publicly.
- Use S3 for uploaded source documents.
- Use EFS, RDS, or a managed vector database if multiple replicas need shared retrieval data.
- Add CloudWatch logs and alarms.
- Add OCR for scanned PDFs.
