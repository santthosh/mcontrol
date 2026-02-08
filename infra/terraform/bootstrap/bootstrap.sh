#!/bin/bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Mission Control Infrastructure Bootstrap ===${NC}"
echo

# Check prerequisites
command -v gcloud >/dev/null 2>&1 || { echo -e "${RED}Error: gcloud CLI is required but not installed.${NC}" >&2; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo -e "${RED}Error: terraform is required but not installed.${NC}" >&2; exit 1; }

# Get configuration
if [ -z "${PROJECT_ID:-}" ]; then
  read -p "Enter your GCP Project ID: " PROJECT_ID
fi

if [ -z "${REGION:-}" ]; then
  read -p "Enter GCP Region [us-central1]: " REGION
  REGION=${REGION:-us-central1}
fi

if [ -z "${GITHUB_REPO:-}" ]; then
  read -p "Enter GitHub repository (owner/repo): " GITHUB_REPO
fi

STATE_BUCKET="${STATE_BUCKET:-mcontrol-terraform-state}"

echo
echo -e "${YELLOW}Configuration:${NC}"
echo "  Project ID:    $PROJECT_ID"
echo "  Region:        $REGION"
echo "  GitHub Repo:   $GITHUB_REPO"
echo "  State Bucket:  $STATE_BUCKET"
echo

read -p "Continue with bootstrap? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 1
fi

# Set project
echo -e "${GREEN}Setting GCP project...${NC}"
gcloud config set project "$PROJECT_ID"

# Enable APIs
echo -e "${GREEN}Enabling required APIs...${NC}"
gcloud services enable \
  storage.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  cloudresourcemanager.googleapis.com

# Create state bucket
echo -e "${GREEN}Creating Terraform state bucket...${NC}"
if gsutil ls -b "gs://$STATE_BUCKET" >/dev/null 2>&1; then
  echo -e "${YELLOW}Bucket gs://$STATE_BUCKET already exists, skipping...${NC}"
else
  gsutil mb -p "$PROJECT_ID" -l "$REGION" -b on "gs://$STATE_BUCKET"
  gsutil versioning set on "gs://$STATE_BUCKET"
fi

# Create Workload Identity Pool
echo -e "${GREEN}Creating Workload Identity Pool...${NC}"
if gcloud iam workload-identity-pools describe github --project="$PROJECT_ID" --location="global" >/dev/null 2>&1; then
  echo -e "${YELLOW}Workload Identity Pool 'github' already exists, skipping...${NC}"
else
  gcloud iam workload-identity-pools create "github" \
    --project="$PROJECT_ID" \
    --location="global" \
    --display-name="GitHub Actions"
fi

# Create OIDC Provider
echo -e "${GREEN}Creating OIDC Provider...${NC}"
if gcloud iam workload-identity-pools providers describe github-actions --project="$PROJECT_ID" --location="global" --workload-identity-pool="github" >/dev/null 2>&1; then
  echo -e "${YELLOW}Provider 'github-actions' already exists, skipping...${NC}"
else
  gcloud iam workload-identity-pools providers create-oidc "github-actions" \
    --project="$PROJECT_ID" \
    --location="global" \
    --workload-identity-pool="github" \
    --display-name="GitHub Actions" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
    --issuer-uri="https://token.actions.githubusercontent.com"
fi

# Get Workload Identity Provider
echo
echo -e "${GREEN}=== Bootstrap Complete ===${NC}"
echo
echo -e "${YELLOW}Workload Identity Provider:${NC}"
gcloud iam workload-identity-pools providers describe github-actions \
  --project="$PROJECT_ID" \
  --location="global" \
  --workload-identity-pool="github" \
  --format="value(name)"

echo
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Create terraform.tfvars in each environment directory"
echo "2. Run 'terraform init && terraform apply' in environments/dev"
echo "3. Add GitHub secrets from the Terraform outputs"
echo
