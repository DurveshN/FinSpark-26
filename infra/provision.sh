#!/usr/bin/env bash
# Provision ALL Azure resources for QTD-HGNN in ONE resource group.
# Idempotent-ish: safe to re-run; creation is skipped if a resource exists.
# REVIEW COST before running — creates billable resources (Container App env,
# ACR Basic, optional PostgreSQL Flexible Server B1ms).
#
# Usage:  bash infra/provision.sh
# Prereqs: `az login` done; edit the vars below.
set -euo pipefail

# ---- edit these ----
RG="rg-qtdhgnn"                     # single resource group
LOCATION="centralindia"            # India region (data residency)
ACR="acrqtdhgnn$RANDOM"            # must be globally unique, lowercase
ENVIRONMENT="cae-qtdhgnn"          # Container Apps environment
APP="ca-qtdhgnn-backend"           # Container App
IMAGE_TAG="latest"
USE_POSTGRES="false"               # "true" to create managed Postgres (extra cost)
PG_SERVER="pg-qtdhgnn-$RANDOM"
PG_ADMIN="qtdadmin"
# --------------------

echo "==> Resource group $RG in $LOCATION"
az group create -n "$RG" -l "$LOCATION" -o none

echo "==> ACR $ACR (Basic)"
az acr create -n "$ACR" -g "$RG" --sku Basic --admin-enabled true -o none

echo "==> Build image in ACR"
az acr build --registry "$ACR" --image "qtdhgnn-backend:$IMAGE_TAG" --file backend/Dockerfile .

DB_URL="sqlite:////app/backend/qtdhgnn.db"
if [ "$USE_POSTGRES" = "true" ]; then
  PG_PASS="$(openssl rand -base64 18)"
  echo "==> PostgreSQL Flexible Server $PG_SERVER (Burstable B1ms)"
  az postgres flexible-server create -g "$RG" -n "$PG_SERVER" -l "$LOCATION" \
    --tier Burstable --sku-name Standard_B1ms --version 16 \
    --admin-user "$PG_ADMIN" --admin-password "$PG_PASS" \
    --public-access 0.0.0.0 --yes -o none
  az postgres flexible-server db create -g "$RG" -s "$PG_SERVER" -d qtdhgnn -o none
  DB_URL="postgresql+psycopg://$PG_ADMIN:$PG_PASS@$PG_SERVER.postgres.database.azure.com/qtdhgnn?sslmode=require"
  echo "    (save this DB password securely: $PG_PASS)"
fi

echo "==> Container Apps environment $ENVIRONMENT"
az containerapp env create -n "$ENVIRONMENT" -g "$RG" -l "$LOCATION" -o none

ACR_SERVER=$(az acr show -n "$ACR" -g "$RG" --query loginServer -o tsv)
ACR_USER=$(az acr credential show -n "$ACR" --query username -o tsv)
ACR_PASS=$(az acr credential show -n "$ACR" --query 'passwords[0].value' -o tsv)

echo "==> Container App $APP"
az containerapp create -n "$APP" -g "$RG" --environment "$ENVIRONMENT" \
  --image "$ACR_SERVER/qtdhgnn-backend:$IMAGE_TAG" \
  --registry-server "$ACR_SERVER" --registry-username "$ACR_USER" --registry-password "$ACR_PASS" \
  --target-port 8000 --ingress external --min-replicas 1 --max-replicas 2 \
  --env-vars "DATABASE_URL=$DB_URL" "CORS_ORIGIN=*" -o none

FQDN=$(az containerapp show -n "$APP" -g "$RG" --query properties.configuration.ingress.fqdn -o tsv)
echo ""
echo "==> DONE. Backend URL: https://$FQDN"
echo "    Health:  https://$FQDN/health"
echo "    WS:      wss://$FQDN/ws/stream"
echo "    Set frontend Vercel env: VITE_API_BASE=https://$FQDN  VITE_WS_URL=wss://$FQDN/ws/stream"
echo "    ACR=$ACR  APP=$APP  RG=$RG  (use these for GitHub Actions secrets)"
