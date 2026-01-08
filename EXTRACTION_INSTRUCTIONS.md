# CEREBRO-RED v2 Repository Extraction Instructions

This document provides step-by-step instructions for extracting the cerebro-red-v2 subdirectory into a standalone GitHub repository.

## Prerequisites

See [EXTRACTION_PREREQUISITES.md](./EXTRACTION_PREREQUISITES.md) for installation instructions.

**Required:**
- git-filter-repo
- git 2.22+

**Optional but Recommended:**
- GitHub CLI (gh)

## Step 1: Install Prerequisites

```bash
# Install git-filter-repo
sudo apt-get install git-filter-repo  # Ubuntu/Debian
# OR
brew install git-filter-repo  # macOS

# Verify installation
git-filter-repo --version
```

## Step 2: Run Extraction Script

```bash
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit
bash cerebro-red-v2/scripts/extract_repository.sh
```

The script will:
1. Create a fresh clone in `/tmp/cerebro-red-v2-extraction`
2. Extract the `cerebro-red-v2/` subdirectory with full history
3. Remove path prefix (cerebro-red-v2/ becomes root)
4. Remove third-party directories from history
5. Clean commit messages
6. Validate the extraction

## Step 3: Manual Verification

After the script completes, verify the extraction:

```bash
cd /tmp/cerebro-red-v2-extraction

# Verify directory structure
ls -la
# Expected: backend/, frontend/, docker/, docs/, scripts/, README.md, etc.

# Verify third-party directories are gone
ls -la | grep -E "(llamator|PyRIT|Model-Inversion-Attack-ToolBox|L1B3RT4S)"
# Expected: No output

# Check commit history
git log --oneline --all
# Review commits to ensure they're relevant to cerebro-red-v2

# Check commit count
git rev-list --all --count

# Verify authors
git log --format='%an' | sort -u

# Check for hexstrike-ai-kit references in commit messages
git log --all --grep="hexstrike-ai-kit" --oneline
# Expected: No results (or replaced with cerebro-red-v2)

# Verify git status
git status
# Expected: "nothing to commit, working tree clean"
```

## Step 4: Create GitHub Repository

### Option A: Using GitHub CLI (Recommended)

```bash
# Authenticate if not already done
gh auth login

# Create public repository
gh repo create Leviticus-Triage/cerebro-red-v2 \
  --public \
  --description "CEREBRO-RED v2: Advanced Red Team Research Platform with PAIR Algorithm and LLM-as-a-Judge Evaluation" \
  --homepage "https://github.com/Leviticus-Triage/cerebro-red-v2"

# Verify repository was created
gh repo view Leviticus-Triage/cerebro-red-v2
```

### Option B: Manual Creation

1. Go to https://github.com/organizations/Leviticus-Triage/repositories/new
2. Repository name: `cerebro-red-v2`
3. Description: "CEREBRO-RED v2: Advanced Red Team Research Platform with PAIR Algorithm and LLM-as-a-Judge Evaluation"
4. Visibility: Public
5. **Do NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 5: Configure Remote and Push

```bash
cd /tmp/cerebro-red-v2-extraction

# Add GitHub remote
git remote add origin git@github.com:Leviticus-Triage/cerebro-red-v2.git

# Verify remote
git remote -v

# Check current branch name
git branch --show-current
# If it's not 'main', rename it:
git branch -M main

# Push with full history
git push -u origin main --force

# Verify push was successful
git log origin/main --oneline | head -10
```

## Step 6: Post-Push Verification

### Via GitHub CLI

```bash
# View repository details
gh repo view Leviticus-Triage/cerebro-red-v2

# Check commits
gh api repos/Leviticus-Triage/cerebro-red-v2/commits | jq '.[].commit.message' | head -20

# Clone and verify
cd /tmp
git clone git@github.com:Leviticus-Triage/cerebro-red-v2.git cerebro-red-v2-verify
cd cerebro-red-v2-verify

# Verify structure
ls -la
# Expected: backend/, frontend/, docker/, docs/, scripts/

# Verify no third-party directories
ls -la | grep -E "(llamator|PyRIT|Model-Inversion-Attack-ToolBox|L1B3RT4S)"
# Expected: No output

# Verify commit history
git log --oneline --all
```

### Via Web Browser

1. Navigate to https://github.com/Leviticus-Triage/cerebro-red-v2
2. Verify repository structure in file browser
3. Check commits tab for full history
4. Verify no third-party directories exist
5. Review commit messages for cleanliness

## Step 7: Complete Validation Report

Fill out [EXTRACTION_VALIDATION_REPORT.md](./EXTRACTION_VALIDATION_REPORT.md) with the results.

## Step 8: Tag Initial Release (Optional)

```bash
cd /tmp/cerebro-red-v2-extraction
git tag -a v2.0.0-extracted -m "Initial extraction from hexstrike-ai-kit"
git push origin v2.0.0-extracted
```

## Troubleshooting

### git-filter-repo not found
```bash
# Install via package manager
sudo apt-get install git-filter-repo  # Ubuntu/Debian
brew install git-filter-repo           # macOS
```

### GitHub CLI authentication fails
```bash
# Re-authenticate
gh auth logout
gh auth login
# Follow prompts to authenticate via browser
```

### Remote already exists
```bash
# Remove existing remote
git remote remove origin
# Add new remote
git remote add origin git@github.com:Leviticus-Triage/cerebro-red-v2.git
```

### Push rejected
```bash
# Force push (safe because this is a new repository)
git push -u origin main --force
```

### Third-party directories still exist after extraction
```bash
# Re-run the filter-repo command with correct paths
cd /tmp/cerebro-red-v2-extraction
git filter-repo --path llamator/ --path PyRIT/ --path Model-Inversion-Attack-ToolBox/ --path L1B3RT4S/ --invert-paths --force
```

## Success Criteria

The extraction is complete when:

1. ✅ Fresh clone created in `/tmp/cerebro-red-v2-extraction`
2. ✅ Subdirectory extracted with full commit history
3. ✅ Path prefix removed (cerebro-red-v2/ → /)
4. ✅ Third-party directories removed from history
5. ✅ Commit messages cleaned (hexstrike-ai-kit → cerebro-red-v2)
6. ✅ Working tree is clean
7. ✅ GitHub repository created at `github.com/Leviticus-Triage/cerebro-red-v2`
8. ✅ Full history pushed to GitHub
9. ✅ Repository structure verified
10. ✅ No third-party directories exist in the new repository
