# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automated testing, building, and deployment of the Booru application.

## Workflows

### 1. Django CI/CD (`django.yml`)

**Triggers**: Push to `main`/`develop` branches, Pull Requests

**What it does**:
- Runs Python 3.11 with PostgreSQL 15
- Installs dependencies and caches them
- Runs code quality checks (Black, isort, Flake8)
- Performs security scans (Bandit, Safety)
- Runs Django tests with coverage reporting
- Collects static files
- Tests Docker container builds
- Scans for vulnerabilities with Trivy

**Tools used**:
- **Code Quality**: Black (formatting), isort (imports), Flake8 (linting)
- **Security**: Bandit (security linting), Safety (dependency security)
- **Testing**: pytest, pytest-django, pytest-cov
- **Coverage**: Codecov integration

### 2. Docker Build and Test (`docker.yml`)

**Triggers**: Push to `main` branch, Pull Requests, Tags

**What it does**:
- Builds Docker images for multiple platforms (amd64, arm64)
- Tests Docker container functionality
- Pushes images to GitHub Container Registry (on main branch)
- Runs security scans on built images
- Tests docker-compose setup

**Features**:
- Multi-platform builds
- Automated testing of containers
- Security vulnerability scanning
- GitHub Container Registry integration

## Local Development Setup

### Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run Tests Locally

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=onnanoko --cov=jozen

# Run specific test file
pytest onnanoko/tests.py

# Run with verbose output
pytest -v
```

### Code Quality Tools

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Check code style with Flake8
flake8 .

# Security checks with Bandit
bandit -r .

# Check dependencies with Safety
safety check
```

### Pre-commit Hooks

Install pre-commit hooks to automatically check code quality before commits:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hook scripts
pre-commit install

# Run against all files
pre-commit run --all-files
```

## Configuration Files

### pytest.ini
- Django settings configuration
- Coverage reporting settings
- Test discovery patterns
- Warning filters

### .pre-commit-config.yaml
- Automated code quality checks
- Integration with Black, isort, Flake8
- Security scanning with Bandit
- Django-specific checks

## Coverage Requirements

The workflow requires at least 60% test coverage. To check coverage locally:

```bash
pytest --cov=onnanoko --cov=jozen --cov-report=html
open htmlcov/index.html
```

## Security Scanning

### Bandit
Scans Python code for common security issues:
- SQL injection
- Hardcoded passwords
- Insecure random number generation
- Shell injection

### Safety
Checks Python dependencies for known security vulnerabilities:
- CVE database integration
- Automated vulnerability detection
- JSON report generation

### Trivy
Container image vulnerability scanner:
- OS package vulnerabilities
- Language-specific security issues
- GitHub Security tab integration

## Troubleshooting

### Common Issues

1. **Tests failing locally but passing in CI**
   - Check database configuration
   - Ensure all dependencies are installed
   - Verify environment variables

2. **Coverage below threshold**
   - Add more test cases
   - Check for untested code paths
   - Review coverage reports

3. **Docker build failures**
   - Check Dockerfile syntax
   - Verify build context
   - Check for missing files

### Debugging Workflows

- Check workflow logs in GitHub Actions tab
- Review test output and error messages
- Verify environment setup and dependencies
- Check for configuration file issues

## Best Practices

1. **Write tests for new features**
2. **Maintain code coverage above 60%**
3. **Fix security issues before merging**
4. **Use pre-commit hooks locally**
5. **Review workflow logs regularly**
6. **Keep dependencies updated**

## Adding New Workflows

To add new workflows:

1. Create a new `.yml` file in `.github/workflows/`
2. Define triggers, jobs, and steps
3. Test locally if possible
4. Commit and push to trigger the workflow
5. Monitor execution and results

## Support

For workflow issues:
- Check GitHub Actions documentation
- Review workflow logs for errors
- Verify configuration and dependencies
- Consider workflow syntax validation tools
