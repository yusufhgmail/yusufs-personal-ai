#!/bin/bash
# Railway Deployment Script
# This script automates the Railway deployment process

echo "🚂 Railway Deployment Script"
echo ""

# Check if Railway CLI is installed
echo "Checking Railway CLI..."
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Railway CLI"
        exit 1
    fi
fi
echo "✅ Railway CLI is installed"
echo ""

# Check if user is logged in
echo "Checking Railway login status..."
railway whoami &> /dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  You need to log in to Railway"
    echo "   Run: railway login --browserless"
    echo ""
    read -p "Do you want to login now? (y/n) " login
    if [ "$login" = "y" ] || [ "$login" = "Y" ]; then
        railway login --browserless
        if [ $? -ne 0 ]; then
            echo "❌ Login failed"
            exit 1
        fi
    else
        echo "Please login first with: railway login --browserless"
        exit 1
    fi
else
    user=$(railway whoami 2>&1)
    echo "✅ Logged in as: $user"
fi
echo ""

# Check if project is already linked
echo "Checking for existing Railway project..."
if [ -f ".railway" ] || [ -d ".railway" ]; then
    echo "✅ Railway project already linked"
    read -p "Use existing project? (y/n) " use_existing
    if [ "$use_existing" != "y" ] && [ "$use_existing" != "Y" ]; then
        rm -rf .railway
        echo "Removed existing link"
    fi
fi

if [ ! -f ".railway" ] && [ ! -d ".railway" ]; then
    echo "Creating new Railway project..."
    railway init
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create Railway project"
        exit 1
    fi
    echo "✅ Railway project created"
fi
echo ""

# Check for .env file
echo "Checking for environment variables..."
if [ -f ".env" ]; then
    echo "✅ Found .env file"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Set environment variables in Railway:"
    echo "      Run: ./setup_railway_env.sh"
    echo ""
    echo "   2. Or manually set them in Railway dashboard:"
    echo "      https://railway.app/dashboard"
    echo ""
else
    echo "⚠️  No .env file found"
    echo "   You'll need to set environment variables manually in Railway"
    echo ""
fi

# Deploy
echo "🚀 Ready to deploy!"
echo ""
read -p "Deploy now? (y/n) " deploy
if [ "$deploy" = "y" ] || [ "$deploy" = "Y" ]; then
    echo ""
    echo "Deploying to Railway..."
    railway up
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Deployment complete!"
        echo ""
        echo "📊 View your deployment:"
        echo "   railway logs    - View logs"
        echo "   railway open    - Open in browser"
        echo ""
    else
        echo "❌ Deployment failed. Check the logs above."
        exit 1
    fi
else
    echo ""
    echo "To deploy later, run: railway up"
fi

