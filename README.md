# Booru - Anime Character Gallery

A Django-based web application for managing and displaying anime character galleries with image uploads, tagging, and user management.

[![Django CI/CD](https://github.com/moemoekyunkyun/Jozen/workflows/Django%20CI%2FCD/badge.svg)](https://github.com/moemoekyunkyun/Jozen/actions/workflows/django.yml)
[![Docker Build](https://github.com/moemoekyunkyun/Jozen/workflows/Docker%20Build%20and%20Test/badge.svg)](https://github.com/moemoekyunkyun/Jozen/actions/workflows/docker.yml)
[![Code Coverage](https://codecov.io/gh/moemoekyunkyun/Jozen/branch/main/graph/badge.svg)](https://codecov.io/gh/moemoekyunkyun/Jozen)

## Features

- **Character Management**: Create, edit, and organize anime characters with detailed profiles
- **Image Gallery**: Upload, tag, and categorize images with approval workflow
- **User System**: User registration, authentication, and profile management
- **Admin Panel**: Comprehensive admin interface for content moderation
- **REST API**: Full API support for external integrations
- **Responsive Design**: Modern, mobile-friendly interface

## Tech Stack

- **Backend**: Django 5.1, Python 3.13
- **Database**: PostgreSQL (production), SQLite (development)
- **Web Server**: Nginx + Gunicorn
- **Containerization**: Docker & Docker Compose
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Authentication**: Django's built-in auth system

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)

### Development Setup
```bash
# Clone the repository
git clone [<your-repo-url>](https://github.com/moemoekyunkyun/jozen)
cd booru

# Start services
docker compose up -d

# Create superuser
docker compose exec web python manage.py createsuperuser

# Access the application
open http://localhost:8000
```

### Production Deployment
See [PRODUCTION.md](PRODUCTION.md) for detailed production deployment instructions.

## CI/CD Pipeline

This project uses GitHub Actions for automated testing, building, and deployment:

### Automated Workflows
- **Django CI/CD**: Runs tests, linting, security checks, and coverage reporting
- **Docker Build**: Builds and tests Docker containers, publishes to GitHub Container Registry
- **Security Scanning**: Automated vulnerability scanning with Trivy and Bandit

### Code Quality
- **Testing**: pytest with Django integration and coverage reporting
- **Linting**: Black (formatting), isort (imports), Flake8 (style)
- **Security**: Bandit (security linting), Safety (dependency security)
- **Coverage**: Minimum 60% test coverage required

For detailed workflow information, see [.github/workflows/README.md](.github/workflows/README.md).

## Project Structure

```
booru/
├── jozen/                 # Django project settings
├── onnanoko/             # Main application
├── templates/            # HTML templates
├── static/               # Static files (CSS, JS, images)
├── media/                # User-uploaded content
├── docker-compose.yml    # Docker services configuration
├── Dockerfile            # Web service container
├── nginx.conf           # Nginx configuration
├── requirements.txt      # Python dependencies
├── requirements-dev.txt  # Development dependencies
├── pytest.ini          # Test configuration
├── .pre-commit-config.yaml # Code quality hooks
└── .github/workflows/   # GitHub Actions workflows
```

## Environment Variables

Create a `.env` file based on `production.env`:

```bash
# Django Settings
DEBUG=False
DJANGO_SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com,localhost
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,http://localhost

# Database
DJANGO_DB_HOST=db
DJANGO_DB_NAME=jozen
DJANGO_DB_USER=jozen
DJANGO_DB_PASSWORD=your-password
```

## API Endpoints

- `GET /api/characters/` - List characters
- `GET /api/images/` - List images
- `GET /api/tags/` - List tags
- `GET /api/series/` - List series
- `GET /api/groups/` - List groups

## Development

### Running Tests
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=onnanoko --cov=jozen
```

### Code Quality
```bash
# Format code
black .
isort .

# Check style
flake8 .

# Security checks
bandit -r .
safety check
```

### Pre-commit Hooks
```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Ensure code quality checks pass
6. Submit a pull request

## Security

- CSRF protection enabled
- XSS protection headers
- HSTS support
- Secure cookie settings (when SSL enabled)
- User permission system
- Automated security scanning in CI/CD

## License

GPL V2

## Support

For issues and questions:
- Check the logs: `docker compose logs`
- Review [PRODUCTION.md](PRODUCTION.md)
- Check [CI/CD documentation](.github/workflows/README.md)
- Open an issue on GitHub

## Roadmap

- [ ] Image optimization and thumbnails
- [ ] Advanced search and filtering
- [ ] User collections and favorites
- [ ] API rate limiting
- [ ] Image CDN integration
