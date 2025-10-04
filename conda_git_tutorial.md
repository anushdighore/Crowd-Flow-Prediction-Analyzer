# Conda Basics & Git Conflict Resolution Tutorial

## Part 1: Conda Basics

Conda is a powerful package and environment management system that helps you manage dependencies and create isolated environments for your projects.

### What is Conda?

Conda is:
- **Package Manager**: Installs and manages software packages
- **Environment Manager**: Creates isolated environments with different package versions
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Language Agnostic**: Not just for Python (supports R, Ruby, Lua, Scala, Java, etc.)

### Core Concepts

#### 1. Environments
- Isolated spaces where you can install specific versions of packages
- Prevents conflicts between different projects
- Each environment has its own Python interpreter and packages

#### 2. Channels
- Repositories where packages are stored
- Default channels: `defaults`, `conda-forge`, `bioconda`
- You can specify channels when installing packages

### Essential Commands

#### Environment Management

```bash
# Create a new environment
conda create --name myenv python=3.9

# Create with specific packages
conda create --name myenv python=3.9 numpy pandas matplotlib

# Activate environment
conda activate myenv

# Deactivate environment
conda deactivate

# List all environments
conda env list
conda info --envs

# Remove environment
conda env remove --name myenv
conda remove --name myenv --all
```

#### Package Management

```bash
# Install packages in current environment
conda install numpy
conda install numpy pandas matplotlib

# Install from specific channel
conda install -c conda-forge scikit-learn

# Install specific version
conda install python=3.8.5
conda install numpy=1.19.2

# Update packages
conda update numpy
conda update --all

# Remove packages
conda remove numpy

# List installed packages
conda list

# Search for packages
conda search numpy
```

#### Environment Information

```bash
# Show conda information
conda info

# Show current environment info
conda info --envs

# Show package info
conda info numpy
```

#### Export/Import Environments

```bash
# Export environment to YAML file
conda env export > environment.yml

# Create environment from YAML file
conda env create -f environment.yml

# Export package list only
conda list --export > requirements.txt

# Create from requirements file
conda create --name myenv --file requirements.txt
```

### Best Practices

#### 1. Use Environment Files
Create an `environment.yml` file for your projects:

```yaml
name: myproject
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.9
  - numpy
  - pandas
  - matplotlib
  - pip
  - pip:
    - some-pip-only-package
```

#### 2. Channel Priority
- Use `conda-forge` for most packages (more up-to-date)
- Specify channels explicitly for reproducibility

```bash
conda install -c conda-forge -c bioconda mypackage
```

#### 3. Environment Naming
- Use descriptive names: `web-scraping`, `ml-project`, `data-analysis`
- Include version numbers if needed: `pytorch-1.9`

#### 4. Keep Base Environment Clean
- Don't install packages in the base environment
- Create separate environments for each project

### Common Workflows

#### Starting a New Project
```bash
# 1. Create environment
conda create --name myproject python=3.9

# 2. Activate it
conda activate myproject

# 3. Install packages
conda install numpy pandas matplotlib jupyter

# 4. Export for sharing
conda env export > environment.yml
```

#### Working with Existing Project
```bash
# 1. Create from environment file
conda env create -f environment.yml

# 2. Activate
conda activate projectname

# 3. Start working!
```

#### Updating Your Environment
```bash
# Activate environment
conda activate myproject

# Update specific package
conda update numpy

# Update all packages
conda update --all

# Export updated environment
conda env export > environment.yml
```

### Troubleshooting Tips

#### 1. Solving Environment Issues
```bash
# Clean conda cache
conda clean --all

# Check for conflicts
conda update --all --dry-run

# Force reinstall
conda install --force-reinstall numpy
```

#### 2. Mixed pip and conda
- Install conda packages first
- Use pip only for packages not available in conda
- Include pip packages in environment.yml under `pip:` section

#### 3. Environment Not Found
```bash
# Refresh environment list
conda info --envs

# Check if conda is in PATH
conda --version
```

### Advanced Features

#### 1. Environment Variables
```bash
# Set environment variables
conda env config vars set MY_VAR=value

# List environment variables
conda env config vars list
```

#### 2. Creating Custom Channels
```bash
# Add custom channel
conda config --add channels mychannel

# Remove channel
conda config --remove channels mychannel
```

#### 3. Conda Configuration
```bash
# Show configuration
conda config --show

# Set default channels
conda config --add channels conda-forge
```

---

## Part 2: How to Resolve Git Merge Conflicts

Merge conflicts occur when Git cannot automatically merge changes from different branches. Here's how to resolve them:

### Understanding Conflict Markers

When conflicts occur, Git adds special markers to the conflicted files:

```
<<<<<<< HEAD
Your local changes
=======
Remote/incoming changes
>>>>>>> branch-name
```

- `<<<<<<< HEAD`: Start of your local changes
- `=======`: Separator between versions  
- `>>>>>>> branch-name`: End of incoming changes

### Step-by-Step Resolution Process

#### 1. Check Conflict Status
```bash
# See which files have conflicts
git status

# See detailed conflict information
git diff
```

#### 2. Choose Your Resolution Strategy

##### Option A: Accept All Remote Changes (Fast)
```bash
# Abort current merge and reset to remote
git merge --abort
git reset --hard origin/main

# Or use checkout strategy
git checkout --theirs .
```

##### Option B: Accept All Local Changes
```bash
# Keep your local version for all conflicts
git checkout --ours .
git add .
git commit -m "Resolve conflicts keeping local changes"
```

##### Option C: Manual Resolution (Most Control)
```bash
# Open each conflicted file and edit manually
# Remove conflict markers and choose/combine changes
# Then stage and commit:
git add filename.py
git commit -m "Resolve merge conflict in filename.py"
```

### Common Conflict Scenarios

#### 1. Simple Content Conflict

**Before (in file):**
```
<<<<<<< HEAD
print("Hello from local")
=======
print("Hello from remote")
>>>>>>> origin/main
```

**After (choose one):**
```python
print("Hello from local")  # Keep local
# OR
print("Hello from remote") # Keep remote
# OR
print("Hello from both")   # Combine/modify
```

#### 2. Import/Dependency Conflicts

**Before:**
```
<<<<<<< HEAD
from models.vmamba_tmtb import load_model
=======
from models.vmamba_official import load_model
>>>>>>> origin/main
```

**Resolution:** Choose the correct import path based on your project structure.

### Using VS Code for Conflict Resolution

VS Code provides a great interface for resolving conflicts:
- Click "Accept Current Change" (your version)
- Click "Accept Incoming Change" (remote version)
- Click "Accept Both Changes" (combine both)
- Click "Compare Changes" to see differences side-by-side

### Advanced Conflict Resolution Tools

#### Using Git Mergetool
```bash
# Configure a merge tool (one-time setup)
git config --global merge.tool vimdiff
# or
git config --global merge.tool vscode

# Launch merge tool for conflicts
git mergetool

# After resolving, commit
git commit -m "Resolve merge conflicts"
```

#### Cherry-pick Specific Changes
```bash
# If you want specific commits from remote
git cherry-pick commit-hash

# Resolve any conflicts, then
git add .
git cherry-pick --continue
```

### Prevention Strategies

#### 1. Regular Pulls
```bash
# Pull frequently to minimize conflicts
git pull origin main

# Or use rebase to keep history clean
git pull --rebase origin main
```

#### 2. Feature Branches
```bash
# Work on feature branches
git checkout -b feature/my-feature
# Make changes, then merge carefully
git checkout main
git pull origin main
git merge feature/my-feature
```

#### 3. Communication
- Coordinate with team members on file changes
- Use smaller, frequent commits
- Avoid force-pushing to shared branches

### Emergency Conflict Recovery

#### If You Mess Up During Resolution
```bash
# Abort merge and start over
git merge --abort

# Or reset to last known good state
git reset --hard HEAD~1

# Check reflog to find lost commits
git reflog
git reset --hard HEAD@{n}
```

#### Recover Lost Work
```bash
# Find lost commits
git reflog

# Recover specific commit
git cherry-pick lost-commit-hash

# Or create new branch from lost commit
git branch recover-branch lost-commit-hash
```

### Pro Tips

> **💡 Pro Tips:**
> - When in doubt, make a backup branch: `git branch backup-before-merge`
> - Use `git status` frequently to understand what's happening
> - Practice conflict resolution on test repositories first
> - Learn your editor's merge conflict tools - they make life easier!

> **⚠️ Warning:** `git reset --hard` permanently deletes uncommitted changes. Use with caution!

> **🚨 Danger Zone:** `git push --force` can overwrite others' work. Use `--force-with-lease` instead.

---

This covers the essential conda basics and comprehensive Git conflict resolution strategies. Start with creating environments and installing packages, then gradually explore the more advanced features as needed!