# Script to set Railway environment variables from .env file

Write-Host "Railway Environment Variables Setup" -ForegroundColor Cyan
Write-Host ""

# Check if Railway CLI is installed
railway --version 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Railway CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "   npm install -g @railway/cli" -ForegroundColor Yellow
    exit 1
}

# Check if logged in
railway whoami 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Not logged in to Railway. Please run:" -ForegroundColor Red
    Write-Host "   railway login --browserless" -ForegroundColor Yellow
    exit 1
}

# Check if project is linked
railway status 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] No Railway project linked. Please run:" -ForegroundColor Red
    Write-Host "   railway init" -ForegroundColor Yellow
    exit 1
}

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "[ERROR] No .env file found" -ForegroundColor Red
    Write-Host "   Please create a .env file with your environment variables" -ForegroundColor Yellow
    exit 1
}

Write-Host "Reading .env file..." -ForegroundColor Yellow

# Read .env file
$envVars = @{}
Get-Content ".env" | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#")) {
        $parts = $line.Split("=", 2)
        if ($parts.Length -eq 2) {
            $key = $parts[0].Trim()
            $value = $parts[1].Trim()
            if ($key -and $value) {
                $envVars[$key] = $value
            }
        }
    }
}

if ($envVars.Count -eq 0) {
    Write-Host "[ERROR] No environment variables found in .env file" -ForegroundColor Red
    exit 1
}

Write-Host "Found $($envVars.Count) environment variables" -ForegroundColor Green
Write-Host ""

# Handle Google credentials separately (base64 encoding)
if ($envVars.ContainsKey("GOOGLE_CREDENTIALS_PATH")) {
    $credsPath = $envVars["GOOGLE_CREDENTIALS_PATH"]
    if (Test-Path $credsPath) {
        Write-Host "Encoding Google credentials to base64..." -ForegroundColor Yellow
        $credsBytes = [IO.File]::ReadAllBytes($credsPath)
        $credsBase64 = [Convert]::ToBase64String($credsBytes)
        $envVars["GOOGLE_CREDENTIALS_BASE64"] = $credsBase64
        Write-Host "[OK] Google credentials encoded" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host "[WARN] Google credentials file not found at: $credsPath" -ForegroundColor Yellow
        Write-Host "   Skipping Google credentials setup" -ForegroundColor Yellow
        Write-Host ""
    }
}

# Set variables in Railway
Write-Host "Setting environment variables in Railway..." -ForegroundColor Yellow
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($key in $envVars.Keys) {
    $value = $envVars[$key]
    
    # Skip empty values
    if ([string]::IsNullOrWhiteSpace($value)) {
        Write-Host "[SKIP] Skipping $key - empty value" -ForegroundColor Gray
        continue
    }
    
    # Skip GOOGLE_CREDENTIALS_PATH if we have GOOGLE_CREDENTIALS_BASE64
    if ($key -eq "GOOGLE_CREDENTIALS_PATH" -and $envVars.ContainsKey("GOOGLE_CREDENTIALS_BASE64")) {
        Write-Host "[SKIP] Skipping $key - using base64 version instead" -ForegroundColor Gray
        continue
    }
    
    Write-Host -NoNewline "Setting $key... "
    
    # Use railway variables --set command with service flag
    $result = railway variables --set "$key=$value" --service divine-fascination 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK]" -ForegroundColor Green
        $successCount++
    } else {
        Write-Host "[FAILED]" -ForegroundColor Red
        Write-Host "   Error: $result" -ForegroundColor Red
        $failCount++
    }
}

Write-Host ""
Write-Host "[OK] Setup complete!" -ForegroundColor Green
Write-Host "   Successfully set: $successCount variables" -ForegroundColor Green
if ($failCount -gt 0) {
    Write-Host "   Failed: $failCount variables" -ForegroundColor Red
}
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "   1. Deploy: railway up" -ForegroundColor White
Write-Host "   2. View logs: railway logs" -ForegroundColor White
Write-Host "   3. Open dashboard: railway open" -ForegroundColor White
Write-Host ""
