# Branch Protection Setup Guide

This guide explains how to secure the release process and prevent unauthorized releases.

## Required Branch Protection Rules

### 1. Protect `main` branch

Go to **Settings > Branches > Add rule** and configure:

- **Branch name pattern**: `main`
- ✅ **Require a pull request before merging**
  - ✅ Require approvals: 1
  - ✅ Dismiss stale reviews when new commits are pushed
- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - Add required checks: `test (3.9)`, `test (3.10)`, `test (3.11)`, `build`
- ✅ **Restrict pushes that create files**
- ✅ **Restrict who can push to matching branches**
  - Add repository administrators and specific collaborators only

### 2. Protect `release/*` branches

Go to **Settings > Branches > Add rule** and configure:

- **Branch name pattern**: `release/*`
- ✅ **Require a pull request before merging**
  - ✅ Require approvals: 1 (from repository administrators)
- ✅ **Restrict pushes that create files**
- ✅ **Restrict who can push to matching branches**
  - **IMPORTANT**: Only add repository administrators/owners
  - This prevents random people from creating release branches

## Environment Protection

### 1. PyPI Environment

Go to **Settings > Environments > pypi** and configure:

- ✅ **Required reviewers**: Add repository administrators
- ✅ **Deployment branches**: Selected branches only
  - Add: `main` (for testing)
  - **DO NOT add `release/*`** - we use tags instead

## Release Process Security

### How it works:

1. **Only administrators** can create release branches (protected by branch rules)
2. **Release workflow** creates version bumps and tags
3. **Publishing only happens on tags** (not branches)
4. **Tags are created automatically** by the release workflow
5. **Environment protection** requires manual approval for PyPI publishing

### Safe Release Steps:

1. **Create Release** (Admin only):
   - Go to Actions → "Release Management" 
   - Run workflow with desired package and version
   - This creates a release branch and tag

2. **Automatic Publishing**:
   - Tag creation triggers build and publish workflow
   - PyPI environment requires approval before publishing
   - Only admins can approve the deployment

3. **Cleanup**:
   - After successful release, delete the release branch
   - Keep the tag for version history

## Additional Security Measures

### 1. Repository Settings

- **Settings > General > Features**:
  - ✅ Disable "Allow merge commits" (use squash/rebase only)
  - ✅ Enable "Automatically delete head branches"

### 2. Required Permissions

- **Write access**: Developers (can create PRs)
- **Admin access**: Release managers only (can create releases)
- **PyPI deployment**: Admins only (manual approval required)

### 3. Secrets Management

Ensure these secrets are properly configured:
- `PYPI_API_TOKEN`: Production PyPI token
- `GITHUB_TOKEN`: Automatically provided

## Troubleshooting

### "User cannot create release branches"
- Check if user has admin permissions
- Verify branch protection rules are correctly configured

### "Publishing failed"
- Check if tag was created properly
- Verify PyPI environment approval was granted
- Check if version already exists on PyPI (use `skip-existing: true`)

### "Workflow not triggered"
- Ensure tag follows pattern `v*` (e.g., `v1.0.0`)
- Check if workflow file syntax is correct
- Verify repository has Actions enabled