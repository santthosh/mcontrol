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
  read -p "Enter GitHub repository (owner/repo, e.g., santthosh/mcontrol): " GITHUB_REPO
fi

# Strip https://github.com/ prefix if provided
GITHUB_REPO="${GITHUB_REPO#https://github.com/}"
GITHUB_REPO="${GITHUB_REPO%.git}"

# Extract owner from repo
GITHUB_OWNER="${GITHUB_REPO%%/*}"

STATE_BUCKET="${STATE_BUCKET:-mcontrol-terraform-state}"

echo
echo -e "${YELLOW}Configuration:${NC}"
echo "  Project ID:    $PROJECT_ID"
echo "  Region:        $REGION"
echo "  GitHub Repo:   $GITHUB_REPO"
echo "  GitHub Owner:  $GITHUB_OWNER"
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

# Enable APIs (idempotent - enabling already-enabled APIs is a no-op)
echo -e "${GREEN}Enabling required APIs...${NC}"
gcloud services enable \
  storage.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  cloudresourcemanager.googleapis.com \
  --quiet

# Create state bucket (idempotent)
echo -e "${GREEN}Creating Terraform state bucket...${NC}"
if gsutil ls -b "gs://$STATE_BUCKET" >/dev/null 2>&1; then
  echo -e "${YELLOW}  ✓ Bucket gs://$STATE_BUCKET already exists${NC}"
else
  gsutil mb -p "$PROJECT_ID" -l "$REGION" -b on "gs://$STATE_BUCKET"
  echo -e "${GREEN}  ✓ Created bucket gs://$STATE_BUCKET${NC}"
fi

# Enable versioning (idempotent)
gsutil versioning set on "gs://$STATE_BUCKET" 2>/dev/null || true
echo -e "${GREEN}  ✓ Versioning enabled${NC}"

# Create Workload Identity Pool (idempotent)
echo -e "${GREEN}Creating Workload Identity Pool...${NC}"
if gcloud iam workload-identity-pools describe github --project="$PROJECT_ID" --location="global" >/dev/null 2>&1; then
  echo -e "${YELLOW}  ✓ Workload Identity Pool 'github' already exists${NC}"
else
  gcloud iam workload-identity-pools create "github" \
    --project="$PROJECT_ID" \
    --location="global" \
    --display-name="GitHub Actions" \
    --quiet
  echo -e "${GREEN}  ✓ Created Workload Identity Pool 'github'${NC}"
fi

# Create or update OIDC Provider (idempotent)
echo -e "${GREEN}Configuring OIDC Provider...${NC}"
if gcloud iam workload-identity-pools providers describe github-actions \
    --project="$PROJECT_ID" \
    --location="global" \
    --workload-identity-pool="github" >/dev/null 2>&1; then
  echo -e "${YELLOW}  ✓ Provider 'github-actions' already exists, updating...${NC}"
  gcloud iam workload-identity-pools providers update-oidc "github-actions" \
    --project="$PROJECT_ID" \
    --location="global" \
    --workload-identity-pool="github" \
    --display-name="GitHub Actions" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
    --attribute-condition="assertion.repository_owner == '$GITHUB_OWNER'" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --quiet
  echo -e "${GREEN}  ✓ Updated OIDC Provider${NC}"
else
  gcloud iam workload-identity-pools providers create-oidc "github-actions" \
    --project="$PROJECT_ID" \
    --location="global" \
    --workload-identity-pool="github" \
    --display-name="GitHub Actions" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
    --attribute-condition="assertion.repository_owner == '$GITHUB_OWNER'" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --quiet
  echo -e "${GREEN}  ✓ Created OIDC Provider 'github-actions'${NC}"
fi

# Get Workload Identity Provider
echo
echo -e "${GREEN}=== Bootstrap Complete ===${NC}"
echo
echo -e "${YELLOW}Workload Identity Provider:${NC}"
WI_PROVIDER=$(gcloud iam workload-identity-pools providers describe github-actions \
  --project="$PROJECT_ID" \
  --location="global" \
  --workload-identity-pool="github" \
  --format="value(name)")
echo "  $WI_PROVIDER"

echo
echo -e "${YELLOW}Next steps:${NC}"
echo "1. cd ../environments/dev"
echo "2. cp terraform.tfvars.example terraform.tfvars"
echo "3. Edit terraform.tfvars with:"
echo "   project_id  = \"$PROJECT_ID\""
echo "   region      = \"$REGION\""
echo "   github_repo = \"$GITHUB_REPO\""
echo "4. terraform init"
echo "5. terraform apply"
echo "6. Add GitHub secrets from terraform output"
echo
