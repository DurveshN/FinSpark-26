#!/usr/bin/env bash
# Resume step: create Container Apps env + app after the image is already in ACR.
# Assumes RG + ACR exist (from provision.sh). SQLite in-container (cheapest).
set -euo pipefail
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8

RG="rg-qtdhgnn"
LOCATION="centralindia"
ENVIRONMENT="cae-qtdhgnn"
APP="ca-qtdhgnn-backend"

ACR=$(az acr list -g "$RG" --query "[0].name" -o tsv)
ACR_SERVER=$(az acr show -n "$ACR" -g "$RG" --query loginServer -o tsv)
ACR_USER=$(az acr credential show -n "$ACR" --query username -o tsv)
ACR_PASS=$(az acr credential show -n "$ACR" --query 'passwords[0].value' -o tsv)

echo "==> Container Apps environment $ENVIRONMENT"
az containerapp env create -n "$ENVIRONMENT" -g "$RG" -l "$LOCATION" -o none

echo "==> Container App $APP"
az containerapp create -n "$APP" -g "$RG" --environment "$ENVIRONMENT" \
  --image "$ACR_SERVER/qtdhgnn-backend:latest" \
  --registry-server "$ACR_SERVER" --registry-username "$ACR_USER" --registry-password "$ACR_PASS" \
  --target-port 8000 --ingress external --min-replicas 1 --max-replicas 2 \
  --cpu 1.0 --memory 2.0Gi \
  --env-vars "DATABASE_URL=sqlite:////app/backend/qtdhgnn.db" "CORS_ORIGIN=*" -o none

FQDN=$(az containerapp show -n "$APP" -g "$RG" --query properties.configuration.ingress.fqdn -o tsv)
echo ""
echo "==> DONE. Backend: https://$FQDN"
echo "    Health: https://$FQDN/health"
echo "    WS:     wss://$FQDN/ws/stream"
echo "    Vercel env: VITE_API_BASE=https://$FQDN  VITE_WS_URL=wss://$FQDN/ws/stream"
