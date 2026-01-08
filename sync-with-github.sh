#!/bin/bash
# Script to sync local cerebro-red-v2 repository with GitHub
# Handles the case where remote has commits that local doesn't have

set -euo pipefail

echo "=== Syncing cerebro-red-v2 with GitHub ==="
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# Ensure we're on main branch
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "Switching to main branch..."
    git checkout main
fi

# Check remote
echo ""
echo "Remote configuration:"
git remote -v

# Fetch latest changes from remote
echo ""
echo "Fetching latest changes from origin..."
git fetch origin

# Check what commits are different
echo ""
echo "=== Comparing local and remote ==="
LOCAL_COMMITS=$(git log origin/main..HEAD --oneline | wc -l)
REMOTE_COMMITS=$(git log HEAD..origin/main --oneline | wc -l)

echo "Local commits not on remote: $LOCAL_COMMITS"
echo "Remote commits not in local: $REMOTE_COMMITS"

if [ "$REMOTE_COMMITS" -gt 0 ]; then
    echo ""
    echo "Remote has commits that local doesn't have:"
    git log HEAD..origin/main --oneline | head -5
    
    echo ""
    echo "Options:"
    echo "1. Pull and merge (recommended if you want to keep both histories)"
    echo "2. Pull with rebase (if you want linear history)"
    echo "3. Force push (⚠️ DANGEROUS - will overwrite remote)"
    echo ""
    read -p "Choose option (1/2/3): " choice
    
    case $choice in
        1)
            echo "Pulling and merging..."
            git pull origin main --no-rebase
            ;;
        2)
            echo "Pulling with rebase..."
            git pull origin main --rebase
            ;;
        3)
            echo "⚠️ WARNING: Force pushing will overwrite remote commits!"
            read -p "Are you sure? (yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                git push -f origin main
                echo "✓ Force pushed"
                exit 0
            else
                echo "Cancelled"
                exit 1
            fi
            ;;
        *)
            echo "Invalid choice"
            exit 1
            ;;
    esac
fi

if [ "$LOCAL_COMMITS" -gt 0 ]; then
    echo ""
    echo "Local has commits that remote doesn't have:"
    git log origin/main..HEAD --oneline | head -5
    
    echo ""
    echo "Pushing local commits..."
    git push -u origin main
else
    echo ""
    echo "✓ Local and remote are in sync"
fi

echo ""
echo "=== Final Status ==="
git status --short
echo ""
echo "✓ Sync complete!"
