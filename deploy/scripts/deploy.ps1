Param(
  [int] $Attempts = 20,
  [int] $SleepSeconds = 3
)

Write-Host "[deploy] Starting production deployment (PowerShell)..."

$ScriptRoot = $PSScriptRoot
$ProjectRoot = (Resolve-Path "$ScriptRoot\..\..\").Path
$ComposeFile = Join-Path $ProjectRoot "deploy\docker-compose.production.yml"
$EnvFile = Join-Path $ProjectRoot "deploy\.env.production"

if (-not (Test-Path $ComposeFile)) {
  Write-Error "[deploy] Compose file not found: $ComposeFile"
  exit 1
}

if (-not (Test-Path $EnvFile)) {
  Write-Error "[deploy] Missing env file: $EnvFile"
  Write-Host "[deploy] Copy from .env.production.example and set secure values."
  exit 1
}

Write-Host "[deploy] Bringing up stack with build..."
docker compose -f $ComposeFile --env-file $EnvFile up -d --build
if ($LASTEXITCODE -ne 0) {
  Write-Error "[deploy] docker compose up failed. Ensure Docker Desktop is running."
  exit $LASTEXITCODE
}

Write-Host "[deploy] Applying migrations..."
docker compose -f $ComposeFile --env-file $EnvFile exec web python manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[deploy] Collecting static files..."
docker compose -f $ComposeFile --env-file $EnvFile exec web python manage.py collectstatic --noinput
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ("[deploy] Waiting for application health (max ~{0}s)..." -f ($Attempts * $SleepSeconds))
for ($i = 1; $i -le $Attempts; $i++) {
  try {
    $resp = Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 -Uri "http://localhost/health/check/"
    if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 300) {
      Write-Host "[deploy] App is healthy."
      break
    }
  } catch {
    # ignore and retry
  }
  Write-Host ("[deploy] Attempt {0}/{1} - not healthy yet; retrying in {2}s..." -f $i, $Attempts, $SleepSeconds)
  Start-Sleep -Seconds $SleepSeconds
  if ($i -eq $Attempts) {
    Write-Error "[deploy] Health check failed. Inspect logs: docker compose -f `"$ComposeFile`" logs web nginx"
    exit 1
  }
}

Write-Host "[deploy] Deployment complete. GraphQL: http://localhost/graphql/"