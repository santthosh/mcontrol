# Terraform Bootstrap

This directory contains instructions for the one-time setup required before using Terraform.

## Prerequisites

- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed
- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.5 installed
- A GCP project with billing enabled
- Owner or Editor role on the GCP project

## Bootstrap Steps

### 1. Set Environment Variables

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
export GITHUB_REPO="owner/mcontrol"  # e.g., santthosh/mcontrol

# Authenticate with GCP
gcloud auth login
gcloud config set project $PROJECT_ID
```

### 2. Enable Required APIs

```bash
gcloud services enable \
  storage.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  cloudresourcemanager.googleapis.com
```

### 3. Create Terraform State Bucket

```bash
# Create the bucket for Terraform state
gsutil mb -p $PROJECT_ID -l $REGION -b on gs://mcontrol-terraform-state

# Enable versioning for state file protection
gsutil versioning set on gs://mcontrol-terraform-state
```

### 4. Create Workload Identity Pool for GitHub Actions

```bash
# Create Workload Identity Pool
gcloud iam workload-identity-pools create "github" \
  --project=$PROJECT_ID \
  --location="global" \
  --display-name="GitHub Actions"

# Create OIDC Provider for GitHub
# Replace YOUR_GITHUB_ORG with your GitHub username or organization
gcloud iam workload-identity-pools providers create-oidc "github-actions" \
  --project=$PROJECT_ID \
  --location="global" \
  --workload-identity-pool="github" \
  --display-name="GitHub Actions" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
  --attribute-condition="assertion.repository_owner == 'YOUR_GITHUB_ORG'" \
  --issuer-uri="https://token.actions.githubusercontent.com"
```

### 5. Verify Bootstrap

```bash
# Verify the bucket exists
gsutil ls gs://mcontrol-terraform-state

# Verify the Workload Identity Pool
gcloud iam workload-identity-pools describe github \
  --project=$PROJECT_ID \
  --location="global"

# Get the Workload Identity Provider resource name (you'll need this for GitHub secrets)
gcloud iam workload-identity-pools providers describe github-actions \
  --project=$PROJECT_ID \
  --location="global" \
  --workload-identity-pool="github" \
  --format="value(name)"
```

## Next Steps

1. **Create terraform.tfvars for each environment:**

   ```bash
   cd ../environments/dev
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values
   ```

2. **Initialize and apply Terraform for dev environment:**

   ```bash
   cd ../environments/dev
   terraform init
   terraform plan
   terraform apply
   ```

3. **Add GitHub Secrets (after Terraform apply):**

   Get the values from Terraform outputs:
   ```bash
   terraform output
   ```

   Add these secrets to GitHub (Settings → Secrets and variables → Actions):

   | Secret Name | Value |
   |-------------|-------|
   | `GCP_PROJECT_ID` | Your GCP project ID |
   | `GCP_REGION` | `us-central1` |
   | `GCP_WORKLOAD_IDENTITY_PROVIDER` | Output from `workload_identity_provider` |
   | `GCP_SERVICE_ACCOUNT_DEV` | Output from `github_actions_service_account` |

4. **Repeat for staging and prod environments**

## Troubleshooting

### "Permission denied" errors

Make sure you have the Owner or Editor role on the project:
```bash
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:$(gcloud config get-value account)"
```

### State bucket already exists

If the bucket name is taken, choose a different name and update the `backend "gcs"` block in all environment main.tf files.

### Workload Identity errors

Verify the GitHub repository attribute matches exactly:
```bash
gcloud iam workload-identity-pools providers describe github-actions \
  --project=$PROJECT_ID \
  --location="global" \
  --workload-identity-pool="github"
```
