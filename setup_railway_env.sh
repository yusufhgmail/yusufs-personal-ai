#!/bin/bash
# Script to set Railway environment variables from .env file

echo "🔧 Railway Environment Variables Setup"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "   npm install -g @railway/cli"
    exit 1
fi

# Check if logged in
railway whoami &> /dev/null
if [ $? -ne 0 ]; then
    echo "❌ Not logged in to Railway. Please run:"
    echo "   railway login --browserless"
    exit 1
fi

# Check if project is linked
if [ ! -f ".railway" ] && [ ! -d ".railway" ]; then
    echo "❌ No Railway project linked. Please run:"
    echo "   railway init"
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "❌ No .env file found"
    echo "   Please create a .env file with your environment variables"
    exit 1
fi

echo "Reading .env file..."

# Read .env file and set variables
success_count=0
fail_count=0

while IFS='=' read -r key value || [ -n "$key" ]; do
    # Skip comments and empty lines
    if [[ "$key" =~ ^[[:space:]]*# ]] || [ -z "$key" ]; then
        continue
    fi
    
    # Remove leading/trailing whitespace
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs)
    
    # Skip if key or value is empty
    if [ -z "$key" ] || [ -z "$value" ]; then
        continue
    fi
    
    # Remove quotes if present
    value=$(echo "$value" | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
    
    echo -n "Setting $key... "
    
    # Set variable in Railway
    if railway variables set "$key=$value" &> /dev/null; then
        echo "✅"
        ((success_count++))
    else
        echo "❌"
        ((fail_count++))
    fi
done < .env

# Handle Google credentials separately (base64 encoding)
if [ -f "config/google_credentials.json" ]; then
    echo ""
    echo "Encoding Google credentials to base64..."
    
    if command -v base64 &> /dev/null; then
        creds_base64=$(base64 -i config/google_credentials.json)
        echo -n "Setting GOOGLE_CREDENTIALS_BASE64... "
        
        if railway variables set "GOOGLE_CREDENTIALS_BASE64=$creds_base64" &> /dev/null; then
            echo "✅"
            ((success_count++))
        else
            echo "❌"
            ((fail_count++))
        fi
    else
        echo "⚠️  base64 command not found. Skipping Google credentials encoding."
        echo "   You can encode it manually and set GOOGLE_CREDENTIALS_BASE64"
    fi
fi

echo ""
echo "✅ Setup complete!"
echo "   Successfully set: $success_count variables"
if [ $fail_count -gt 0 ]; then
    echo "   Failed: $fail_count variables"
fi
echo ""
echo "📋 Next steps:"
echo "   1. Deploy: railway up"
echo "   2. View logs: railway logs"
echo "   3. Open dashboard: railway open"
echo ""

