# Booru - Anime Character Gallery

A Django-based web application for managing and displaying anime character galleries with image uploads, tagging, and user management.

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
└── requirements.txt      # Python dependencies
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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Security

- CSRF protection enabled
- XSS protection headers
- HSTS support
- Secure cookie settings (when SSL enabled)
- User permission system

## License

GPL V2

## Support

For issues and questions:
- Check the logs: `docker compose logs`
- Review [PRODUCTION.md](PRODUCTION.md)
- Open an issue on GitHub

## Roadmap

- [ ] Image optimization and thumbnails
- [ ] Advanced search and filtering
- [ ] User collections and favorites
- [ ] API rate limiting
- [ ] Image CDN integration
