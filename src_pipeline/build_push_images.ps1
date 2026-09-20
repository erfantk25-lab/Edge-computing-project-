<#
.SYNOPSIS
Builds and pushes SmartGrow Docker images to Azure Container Registry.

.DESCRIPTION
This script verifies local dependencies, authenticates to ACR, builds the Mosquitto
and Consumer images locally, tags them, and pushes them to the remote registry.
#>

$ErrorActionPreference = "Stop"
$AcrName = "smartgrowacr31365"
$RegistryUri = "$AcrName.azurecr.io"
$MosquittoImage = "$RegistryUri/smartgrow-mosquitto:latest"
$ConsumerImage = "$RegistryUri/smartgrow-consumer:latest"

Write-Host "=== SmartGrow Local Build Preflight ===" -ForegroundColor Cyan

# 1. Verify Docker is installed and running
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not installed or not in your PATH. Please install Docker Desktop."
    exit 1
}
try {
    $null = docker info
} catch {
    Write-Error "Docker daemon is not running. Please start Docker Desktop."
    exit 1
}
Write-Host "[PASS] Docker is running."

# 2. Verify Azure CLI is installed and logged in
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Error "Azure CLI ('az') is not installed. Please install it."
    exit 1
}
try {
    $null = az account show
} catch {
    Write-Error "You are not logged into Azure CLI. Run 'az login' first."
    exit 1
}
Write-Host "[PASS] Azure CLI is ready."

Write-Host "`n=== Logging into ACR ===" -ForegroundColor Cyan
az acr login --name $AcrName
Write-Host "Successfully logged into $AcrName"

Write-Host "`n=== Building Mosquitto Image ===" -ForegroundColor Cyan
docker build -t $MosquittoImage -f src_pipeline/dockerfiles/mosquitto.dockerfile .

Write-Host "`n=== Building Consumer Image ===" -ForegroundColor Cyan
docker build -t $ConsumerImage -f src_pipeline/dockerfiles/consumer.dockerfile .

Write-Host "`n=== Pushing Mosquitto Image to ACR ===" -ForegroundColor Cyan
docker push $MosquittoImage

Write-Host "`n=== Pushing Consumer Image to ACR ===" -ForegroundColor Cyan
docker push $ConsumerImage

Write-Host "`n=== Verifying Images in Local Docker ===" -ForegroundColor Cyan
docker images | Select-String "smartgrow"

Write-Host "`n[SUCCESS] Local build and push complete! You may now proceed with the Cloud Shell deployment." -ForegroundColor Green
