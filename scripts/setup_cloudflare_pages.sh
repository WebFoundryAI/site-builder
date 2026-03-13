#!/bin/bash
# Setup Cloudflare Pages project for a new site

set -e

CF_PROJECT=$1
DOMAIN=$2

if [ -z "$CF_PROJECT" ] || [ -z "$DOMAIN" ]; then
    echo "ERROR: Usage: $0 <cf_project> <domain>" >&2
    exit 1
fi

if [ -z "$CLOUDFLARE_API_TOKEN" ] || [ -z "$CLOUDFLARE_ACCOUNT_ID" ]; then
    echo "ERROR: CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID environment variables required" >&2
    exit 1
fi

echo "Setting up Cloudflare Pages project: $CF_PROJECT for domain: $DOMAIN" >&2

# Create Pages project via API
API_URL="https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/pages/projects"

PROJECT_DATA=$(cat <<EOF
{
  "name": "$CF_PROJECT",
  "production_branch": "main",
  "build_config": {
    "build_command": "bun run build",
    "destination_dir": "dist",
    "root_dir": ""
  },
  "compatibility_date": "2025-01-01",
  "env_vars": {
    "NODE_ENV": {
      "value": "production"
    }
  }
}
EOF
)

RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PROJECT_DATA" \
  "$API_URL")

# Check for errors
if echo "$RESPONSE" | grep -q '"success":false'; then
    ERROR_MSG=$(echo "$RESPONSE" | grep -o '"message":"[^"]*' | head -1 | cut -d'"' -f4)
    if [[ "$ERROR_MSG" == *"already exists"* ]]; then
        echo "✓ Pages project already exists: $CF_PROJECT" >&2
    else
        echo "ERROR: Failed to create Pages project: $ERROR_MSG" >&2
        exit 1
    fi
else
    echo "✓ Created Cloudflare Pages project: $CF_PROJECT" >&2
fi

# Add custom domain
DOMAIN_API="$API_URL/$CF_PROJECT/domains"
DOMAIN_DATA="{\"domain\": \"$DOMAIN\"}"

DOMAIN_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$DOMAIN_DATA" \
  "$DOMAIN_API")

if echo "$DOMAIN_RESPONSE" | grep -q '"success":true'; then
    echo "✓ Added custom domain: $DOMAIN" >&2
elif echo "$DOMAIN_RESPONSE" | grep -q "already exists"; then
    echo "✓ Custom domain already configured: $DOMAIN" >&2
else
    echo "WARNING: Could not add custom domain (may already be configured): $DOMAIN" >&2
fi

echo "✓ Cloudflare Pages setup complete" >&2
