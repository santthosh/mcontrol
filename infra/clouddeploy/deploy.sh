#!/bin/bash
# Deploy Mission Control API to Cloud Run
#
# Prerequisites:
#   - gcloud CLI installed and authenticated
#   - Docker installed
#   - PROJECT_ID environment variable set
#
# Usage:
#   export PROJECT_ID=your-project-id
#   ./deploy.sh

set -euo pipefail

# Configuration
REGION="us-central1"
SERVICE_NAME="mcontrol-api"
REPO_NAME="mcontrol"

# Derived values
IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}:latest"

echo "Deploying Mission Control API to Cloud Run..."
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Image: ${IMAGE_URL}"

# Build and push Docker image
echo "Building Docker image..."
docker build -t "${IMAGE_URL}" ../../apps/api

echo "Pushing to Artifact Registry..."
docker push "${IMAGE_URL}"

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE_URL}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --set-env-vars "FIREBASE_PROJECT_ID=${PROJECT_ID}" \
  --set-secrets "DATABASE_URL=database-url:latest,REDIS_URL=redis-url:latest"

echo "Deployment complete!"
echo "Service URL: $(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')"
