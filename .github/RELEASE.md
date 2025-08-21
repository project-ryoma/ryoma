# GitHub Actions Workflows

This repository contains automated workflows for building, testing, and publishing Ryoma AI packages.

## Workflows

### 1. Build and Publish (`build-and-publish.yml`)

**Triggers:**
- Push to `main` branch
- Push to `release/*` branches  
- Tags starting with `v*`
- Pull requests to `main`

**Jobs:**
- **Test**: Runs tests across Python 3.9, 3.10, 3.11
  - Linting with ruff
  - Type checking with mypy
  - Unit tests with pytest
  - Coverage reporting

- **Build**: Creates distribution packages
  - Builds both `ryoma_ai` and `ryoma_lab` packages
  - Validates packages with twine
  - Uploads build artifacts

- **Publish Test**: Publishes to Test PyPI (on main/release branches)
- **Publish Prod**: Publishes to PyPI (on version tags)

### 2. Release Management (`release.yml`)

**Trigger:** Manual workflow dispatch

**Inputs:**
- **Package**: Choose which package to release (`ryoma_ai`, `ryoma_lab`, or `both`)
- **Version Type**: Choose version bump type (`patch`, `minor`, `major`)  
- **Pre-release**: Optional pre-release identifier (`alpha`, `beta`, `rc`)

**Process:**
1. Bumps version in pyproject.toml files
2. Creates release branch
3. Generates changelog
4. Creates GitHub release
5. Triggers build and publish workflow

## Setup Requirements

### Repository Secrets

The following secrets need to be configured in the GitHub repository:

#### For PyPI Publishing
- `PYPI_API_TOKEN`: PyPI API token for production releases
- `TEST_PYPI_API_TOKEN`: Test PyPI API token for testing

#### GitHub Token
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions

### Environment Setup

1. **Test PyPI Environment**
   - Name: `test-pypi`
   - Required for publishing to Test PyPI

2. **PyPI Environment**  
   - Name: `pypi`
   - Required for publishing to production PyPI
   - Should require manual approval for security

## Usage

### Manual Release Process

1. Go to the Actions tab in GitHub
2. Select "Release Management" workflow
3. Click "Run workflow"
4. Choose:
   - Package to release
   - Version bump type
   - Optional pre-release identifier
5. Click "Run workflow"

This will:
- Create a release branch with version bumps
- Generate a GitHub release
- Trigger the build and publish workflow

### Automatic Builds

- **Pull Requests**: Run tests only
- **Main Branch**: Run tests + publish to Test PyPI
- **Release Branches**: Run tests + publish to Test PyPI  
- **Version Tags**: Run tests + publish to production PyPI

## Package Configuration

Both packages use:
- **Build System**: Hatchling
- **Python Versions**: 3.9, 3.10, 3.11
- **Testing**: pytest with coverage
- **Linting**: ruff
- **Type Checking**: mypy

### Dependencies

- `ryoma_ai`: Core AI agent functionality
- `ryoma_lab`: Web interface (depends on ryoma_ai)

## Troubleshooting

### Common Issues

1. **Failed PyPI Upload**
   - Check API tokens are correctly configured
   - Verify package names are available
   - Ensure version numbers are incremented

2. **Test Failures**
   - Review test logs in the Actions tab
   - Ensure all dependencies are properly specified
   - Check for import errors or missing files

3. **Build Failures**
   - Verify pyproject.toml syntax
   - Check that all required files are included
   - Ensure build dependencies are available

### Manual Package Building

To build packages locally:

```bash
# Build ryoma_ai
cd packages/ryoma_ai
python -m build

# Build ryoma_lab  
cd packages/ryoma_lab
python -m build
```

### Manual Publishing

To publish manually:

```bash
# Install twine
pip install twine

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Security Considerations

- API tokens are stored as repository secrets
- Production publishing requires environment approval
- Pre-release packages are clearly marked
- All uploads are validated before publishing

## Monitoring

- Check Actions tab for workflow status
- Monitor PyPI/Test PyPI for successful uploads
- Review release notes for accuracy
- Verify installation commands work correctly