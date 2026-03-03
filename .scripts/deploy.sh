#!/bin/bash
set -e

# Change to the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Check if .env file exists and load variables
if [ -f .env ]; then
  echo "Loading environment variables from .env"
  while IFS='=' read -r key value; do
    if [[ -n "$key" && "$key" != \#* ]]; then
      # Remove optional surrounding quotes from the value
      value="${value%\"}"
      value="${value#\"}"
      value="${value%\'}"
      value="${value#\'}"
      export "$key=$value"
    fi
  done < .env
else
  echo "Warning: .env file not found. Falling back to environment variables."
fi

# Ensure required variables are set
if [ -z "$GCP_PROJECT_ID" ]; then
  echo "Error: GCP_PROJECT_ID is not set in .env or environment"
  exit 1
fi

if [ -z "$GEMINI_DATA_STORE_ID" ]; then
  echo "Error: GEMINI_DATA_STORE_ID is not set in .env or environment"
  exit 1
fi

# Determine region (Cloud Run requires a specific region, default to us-central1 if global or not set)
RUN_REGION="${GCP_REGION:-us-central1}"
if [ "$RUN_REGION" = "global" ]; then
  RUN_REGION="us-central1"
fi

SERVICE_NAME="gemini-ent-embedding"

echo "=================================================="
echo "Deploying to Google Cloud Run"
echo "=================================================="
echo "Service: $SERVICE_NAME"
echo "Project: $GCP_PROJECT_ID"
echo "Region:  $RUN_REGION"
echo "Data Store ID: $GEMINI_DATA_STORE_ID"
echo "USE_IAP_AUTH: ${USE_IAP_AUTH:-false}"
echo "=================================================="

AUTH_FLAG="--allow-unauthenticated"
if [ "${USE_IAP_AUTH,,}" = "true" ]; then
  echo "Note: USE_IAP_AUTH=true. Ensure your Cloud Load Balancer and IAP are configured."
fi

# Deploy to Cloud Run using source code
# Cloud Buildpacks will detect Python and install requirements.txt
gcloud run deploy "$SERVICE_NAME" --source . --project "$GCP_PROJECT_ID" --region "$RUN_REGION" $AUTH_FLAG --set-env-vars="GCP_PROJECT_ID=$GCP_PROJECT_ID,GCP_REGION=$GCP_REGION,GEMINI_DATA_STORE_ID=$GEMINI_DATA_STORE_ID,USE_IAP_AUTH=${USE_IAP_AUTH:-false}"

echo "Deployment complete!"
