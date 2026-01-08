# Repository Extraction Prerequisites

Before running the extraction script, ensure the following tools are installed:

## Required Tools

### 1. git-filter-repo

**Check installation:**
```bash
git-filter-repo --version
```

**Installation options:**

**Ubuntu/Debian:**
```bash
sudo apt-get install git-filter-repo
```

**macOS:**
```bash
brew install git-filter-repo
```

**Via pip (if package manager not available):**
```bash
pip3 install git-filter-repo
# Or with --user flag:
pip3 install --user git-filter-repo
export PATH="$HOME/.local/bin:$PATH"
```

### 2. GitHub CLI (gh) - Optional but Recommended

**Check installation:**
```bash
gh --version
```

**Installation options:**

**Ubuntu/Debian:**
```bash
sudo apt install gh
```

**macOS:**
```bash
brew install gh
```

**Authentication:**
```bash
gh auth login
# Follow prompts to authenticate via browser
```

## Verification

After installation, verify both tools:

```bash
# Check git-filter-repo
git-filter-repo --version
# Expected output: git-filter-repo X.X.X

# Check GitHub CLI (if installed)
gh --version
# Expected output: gh version X.X.X
```

## Next Steps

Once prerequisites are installed, proceed with:

1. Run the extraction script: `bash cerebro-red-v2/scripts/extract_repository.sh`
2. Follow the manual verification steps
3. Create GitHub repository
4. Push to GitHub
