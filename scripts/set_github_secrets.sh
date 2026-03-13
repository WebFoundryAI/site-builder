#!/bin/bash
# Set GitHub repository secrets for a new site

set -e

REPO_NAME=$1
CF_API_TOKEN=$2
CF_ACCOUNT_ID=$3

if [ -z "$REPO_NAME" ] || [ -z "$CF_API_TOKEN" ] || [ -z "$CF_ACCOUNT_ID" ]; then
    echo "ERROR: Usage: $0 <repo_name> <cf_api_token> <cf_account_id>" >&2
    exit 1
fi

REPO="WebFoundryAI/$REPO_NAME"

echo "Setting GitHub secrets for: $REPO" >&2

# Set Cloudflare API token
gh secret set CLOUDFLARE_API_TOKEN \
  --repo "$REPO" \
  --body "$CF_API_TOKEN" 2>/dev/null && echo "✓ Set CLOUDFLARE_API_TOKEN" >&2 || echo "⚠ Failed to set CLOUDFLARE_API_TOKEN" >&2

# Set Cloudflare Account ID
gh secret set CLOUDFLARE_ACCOUNT_ID \
  --repo "$REPO" \
  --body "$CF_ACCOUNT_ID" 2>/dev/null && echo "✓ Set CLOUDFLARE_ACCOUNT_ID" >&2 || echo "⚠ Failed to set CLOUDFLARE_ACCOUNT_ID" >&2

# Set GitHub token (for gh actions)
# Uses the current GitHub token from environment
if [ -n "$GITHUB_TOKEN" ]; then
    gh secret set GITHUB_TOKEN \
      --repo "$REPO" \
      --body "$GITHUB_TOKEN" 2>/dev/null && echo "✓ Set GITHUB_TOKEN" >&2 || echo "⚠ Failed to set GITHUB_TOKEN" >&2
fi

echo "✓ GitHub secrets setup complete" >&2
