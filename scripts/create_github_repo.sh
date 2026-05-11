#!/usr/bin/env bash
# Usage: ./scripts/create_github_repo.sh <repo-name> [private]
# Requires Git and GitHub CLI (gh) authenticated
set -e
REPO_NAME=${1:-drive-search-agent}
PRIVATE=${2:-false}

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found. Install from https://cli.github.com/"
  exit 1
fi

# create repo
if [ "$PRIVATE" = "true" ]; then
  gh repo create "$REPO_NAME" --private --confirm
else
  gh repo create "$REPO_NAME" --public --confirm
fi

# push local repo
git init || true
git add .
git commit -m "Initial commit" || true
git branch -M main || true
# set origin to created repo
REMOTE_URL=$(gh repo view --json sshUrl -q .sshUrl 2>/dev/null || gh repo view --json httpUrl -q .httpUrl)
if [ -z "$REMOTE_URL" ]; then
  REMOTE_URL=$(gh repo view "$REPO_NAME" --json sshUrl -q .sshUrl)
fi

git remote add origin "$REMOTE_URL" || true
git push -u origin main

echo "Repository created and pushed: $REMOTE_URL"
