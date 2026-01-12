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
# Apache License 2.0 (recommended for open source)
cat > LICENSE << 'EOF'
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (which shall not include Communications that are clearly marked or
      otherwise designated in writing by the copyright owner as "Not a Work").

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution".

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct or
      contributory patent infringement, then any patent licenses granted to
      You under this License for that Work shall terminate as of the date such
      litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You meet
      the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents of
          the NOTICE file are for informational purposes only and do not
          modify the License. You may add Your own attribution notices
          within Derivative Works that You distribute, alongside or as an
          addendum to the NOTICE text from the Work, provided that such
          additional attribution notices cannot be construed as modifying
          the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or for
      any such Derivative Works as a whole, provided Your use, reproduction,
      and distribution of the Work otherwise complies with the conditions
      stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

Copyright 2024-2026 Cerebro-Red v2 Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
EOF

git add LICENSE
git commit -m "Add Apache License 2.0"
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
