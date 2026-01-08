# Railway Deployment Script
# This script automates the Railway deployment process

Write-Host "🚂 Railway Deployment Script" -ForegroundColor Cyan
Write-Host ""

# Check if Railway CLI is installed
Write-Host "Checking Railway CLI..." -ForegroundColor Yellow
$railwayVersion = railway --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Railway CLI not found. Installing..." -ForegroundColor Red
    npm install -g @railway/cli
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install Railway CLI" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ Railway CLI is installed" -ForegroundColor Green
Write-Host ""

# Check if user is logged in
Write-Host "Checking Railway login status..." -ForegroundColor Yellow
railway whoami 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  You need to log in to Railway" -ForegroundColor Yellow
    Write-Host "   Run: railway login" -ForegroundColor Yellow
    Write-Host "   This will open a browser for authentication" -ForegroundColor Yellow
    Write-Host ""
    $login = Read-Host "Do you want to login now? (y/n)"
    if ($login -eq "y" -or $login -eq "Y") {
        railway login
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Login failed" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "Please login first with: railway login" -ForegroundColor Yellow
        exit 1
    }
} else {
    $user = railway whoami 2>&1
    Write-Host "✅ Logged in as: $user" -ForegroundColor Green
}
Write-Host ""

# Check if project is already linked
Write-Host "Checking for existing Railway project..." -ForegroundColor Yellow
if (Test-Path ".railway") {
    Write-Host "✅ Railway project already linked" -ForegroundColor Green
    $useExisting = Read-Host "Use existing project? (y/n)"
    if ($useExisting -ne "y" -and $useExisting -ne "Y") {
        Remove-Item -Recurse -Force .railway
        Write-Host "Removed existing link" -ForegroundColor Yellow
    }
}

if (-not (Test-Path ".railway")) {
    Write-Host "Creating new Railway project..." -ForegroundColor Yellow
    railway init
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create Railway project" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Railway project created" -ForegroundColor Green
}
Write-Host ""

# Check for .env file
Write-Host "Checking for environment variables..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ Found .env file" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Set environment variables in Railway:" -ForegroundColor White
    Write-Host "      Run: .\setup_railway_env.ps1" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   2. Or manually set them in Railway dashboard:" -ForegroundColor White
    Write-Host "      https://railway.app/dashboard" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "⚠️  No .env file found" -ForegroundColor Yellow
    Write-Host "   You'll need to set environment variables manually in Railway" -ForegroundColor Yellow
    Write-Host ""
}

# Deploy
Write-Host "🚀 Ready to deploy!" -ForegroundColor Cyan
Write-Host ""
$deploy = Read-Host "Deploy now? (y/n)"
if ($deploy -eq "y" -or $deploy -eq "Y") {
    Write-Host ""
    Write-Host "Deploying to Railway..." -ForegroundColor Yellow
    railway up
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Deployment complete!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📊 View your deployment:" -ForegroundColor Cyan
        Write-Host "   railway logs    - View logs" -ForegroundColor White
        Write-Host "   railway open    - Open in browser" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "❌ Deployment failed. Check the logs above." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "To deploy later, run: railway up" -ForegroundColor Yellow
}

