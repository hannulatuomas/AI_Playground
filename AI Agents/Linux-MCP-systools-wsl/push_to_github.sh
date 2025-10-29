#!/bin/bash
# Push to GitHub - Linux-MCP-systools-wsl

echo "=============================================="
echo "Push to GitHub Repository"
echo "=============================================="
echo ""

REPO_NAME="Linux-MCP-systools-wsl"

echo "This script will help you push the code to GitHub."
echo "Repository name: $REPO_NAME"
echo ""

# Check if remote already exists
if git remote get-url origin &> /dev/null; then
    echo "✓ Remote 'origin' already configured"
    git remote -v
else
    echo "Instructions:"
    echo ""
    echo "1. Go to GitHub.com and create a new PRIVATE repository named: $REPO_NAME"
    echo "   URL: https://github.com/new"
    echo ""
    echo "2. After creating the repo, run ONE of these commands:"
    echo ""
    echo "   Option A - HTTPS (easier, will ask for credentials):"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/$REPO_NAME.git"
    echo ""
    echo "   Option B - SSH (requires SSH key setup):"
    echo "   git remote add origin git@github.com:YOUR_USERNAME/$REPO_NAME.git"
    echo ""
    echo "3. Then run: git push -u origin master"
    echo ""
    echo "   Or if you want to use 'main' as branch name:"
    echo "   git branch -M main"
    echo "   git push -u origin main"
fi

echo ""
echo "=============================================="
echo "Current Status:"
echo "=============================================="
git status
echo ""
echo "Recent commits:"
git log --oneline -5
