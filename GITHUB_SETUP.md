# GitHub Repository Setup Guide

This guide will help you set up a GitHub repository for the CEREBRO-RED v2 project.

## Prerequisites

- Git installed on your system
- GitHub account
- SSH key configured (optional but recommended)

## Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Fill in the repository details:
   - **Repository name**: `cerebro-red-v2` (or your preferred name)
   - **Description**: "Autonomous Local LLM Red Teaming Suite - Research-grade framework for automated vulnerability discovery"
   - **Visibility**: Choose Public or Private
   - **Initialize**: Do NOT initialize with README, .gitignore, or license (we already have these)
5. Click "Create repository"

## Step 2: Initialize Git Repository (if not already done)

If the project is not yet a git repository:

```bash
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2
git init
```

## Step 3: Create .gitignore

Ensure you have a comprehensive `.gitignore` file:

```bash
# Create or update .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
pip-log.txt
pip-delete-this-directory.txt
.pytest_cache/
.coverage
htmlcov/
*.egg-info/
dist/
build/

# Environment variables
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Database
*.db
*.sqlite
*.sqlite3
data/*.db

# Logs
*.log
logs/
*.log.*

# Frontend
frontend/node_modules/
frontend/dist/
frontend/.vite/
frontend/.env.local
frontend/.env.production.local

# Docker
docker-compose.override.yml

# Data files (keep structure, ignore content)
data/experiments/*
data/logs/*
data/audit/*
!data/.gitkeep

# Temporary files
*.tmp
*.temp
.cache/

# OS
Thumbs.db
.DS_Store

# Test outputs
.pytest_cache/
.coverage
htmlcov/
test-results/
playwright-report/
EOF
```

## Step 4: Add Remote Repository

```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/cerebro-red-v2.git

# Or if using SSH:
# git remote add origin git@github.com:YOUR_USERNAME/cerebro-red-v2.git
```

## Step 5: Stage and Commit Files

```bash
# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: CEREBRO-RED v2 - Autonomous LLM Red Teaming Suite

- Complete backend implementation with FastAPI
- React frontend with real-time monitoring
- 44 attack strategies implemented
- PAIR algorithm implementation
- LLM-as-a-Judge evaluation
- Comprehensive documentation
- Docker containerization
- Template management system
- Vulnerability tracking and reporting"
```

## Step 6: Push to GitHub

```bash
# Push to main branch
git branch -M main
git push -u origin main
```

If you encounter authentication issues:

- **HTTPS**: You'll be prompted for username and password (use a Personal Access Token, not your password)
- **SSH**: Ensure your SSH key is added to GitHub

## Step 7: Create Personal Access Token (if using HTTPS)

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name: "CEREBRO-RED v2"
4. Select scopes: `repo` (full control of private repositories)
5. Click "Generate token"
6. Copy the token and use it as your password when pushing

## Step 8: Add Repository Topics

On GitHub, go to your repository → Settings → Topics and add:

- `llm-security`
- `red-teaming`
- `adversarial-testing`
- `prompt-injection`
- `jailbreak-detection`
- `fastapi`
- `react`
- `cybersecurity`
- `research`

## Step 9: Create GitHub Actions Workflow (Optional)

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run linter
        run: |
          cd frontend
          npm run lint
      - name: Build
        run: |
          cd frontend
          npm run build
```

## Step 10: Add Repository Description and Website

1. Go to repository Settings → General
2. Add description: "Autonomous Local LLM Red Teaming Suite - Research-grade framework for automated vulnerability discovery in LLMs"
3. Add website (if you have a portfolio): Your portfolio URL
4. Add topics (see Step 8)

## Step 11: Create Release (Optional)

1. Go to repository → Releases → "Create a new release"
2. Tag version: `v1.0.0`
3. Release title: "CEREBRO-RED v2.0.0 - Initial Release"
4. Description: Copy from CHANGELOG.md
5. Click "Publish release"

## Step 12: Add License

If you haven't already, add a LICENSE file:

```bash
# MIT License (recommended for open source)
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

git add LICENSE
git commit -m "Add MIT License"
git push
```

## Step 13: Create CONTRIBUTING.md (Optional)

```bash
cat > CONTRIBUTING.md << 'EOF'
# Contributing to CEREBRO-RED v2

Thank you for your interest in contributing!

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## Code Style

- Backend: Follow PEP 8, use type hints
- Frontend: Use TypeScript, follow React best practices
- Write tests for new features
- Update documentation

## Reporting Issues

Please use the GitHub issue tracker to report bugs or suggest features.
EOF

git add CONTRIBUTING.md
git commit -m "Add contributing guidelines"
git push
```

## Verification

After setup, verify everything is working:

```bash
# Check remote
git remote -v

# Check status
git status

# View commit history
git log --oneline

# Test pull
git pull origin main
```

## Next Steps

1. **Add README badges**: Add badges to README.md for build status, license, etc.
2. **Create issues**: Create initial issues for known bugs or planned features
3. **Set up branch protection**: In repository settings, protect the main branch
4. **Add collaborators**: If working with a team, add collaborators in Settings → Collaborators

## Troubleshooting

### Authentication Issues

If you get authentication errors:

```bash
# For HTTPS, update remote URL with token
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/cerebro-red-v2.git

# For SSH, ensure key is added to GitHub
ssh -T git@github.com
```

### Large Files

If you have large files that shouldn't be in git:

```bash
# Remove from git but keep locally
git rm --cached large-file.db

# Add to .gitignore
echo "large-file.db" >> .gitignore

# Commit
git commit -m "Remove large file from repository"
```

### Update Remote URL

If you need to change the remote URL:

```bash
git remote set-url origin NEW_URL
```

## Security Notes

- **Never commit**: `.env` files, API keys, passwords, or sensitive data
- **Use secrets**: For CI/CD, use GitHub Secrets for sensitive values
- **Review changes**: Always review what you're committing with `git status` and `git diff`

## Resources

- [GitHub Docs](https://docs.github.com/)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
