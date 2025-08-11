# Production Deployment Guide

## Overview
This guide covers deploying the Booru application to production with proper security measures and best practices.

## Prerequisites
- Docker and Docker Compose installed
- Domain name (for SSL certificates)
- Server with at least 2GB RAM and 20GB storage
- Basic knowledge of Linux server administration

## Security Checklist

### 1. Environment Variables
- [ ] Generate a new `DJANGO_SECRET_KEY`
- [ ] Set strong database passwords
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set `DEBUG=False`

### 2. Database Security
- [ ] Use strong PostgreSQL passwords
- [ ] Consider using external database service (AWS RDS, etc.)
- [ ] Enable database connection encryption

### 3. SSL/HTTPS
- [ ] Obtain SSL certificate (Let's Encrypt recommended)
- [ ] Configure nginx for HTTPS
- [ ] Enable HSTS headers
- [ ] Redirect HTTP to HTTPS

### 4. Server Security
- [ ] Configure firewall (UFW recommended)
- [ ] Set up fail2ban
- [ ] Regular security updates
- [ ] Use SSH keys instead of passwords

## Deployment Steps

### 1. Prepare Environment
```bash
# Copy production environment template
cp production.env .env

# Edit .env with your production values
nano .env
```

### 2. Generate Secret Key
```bash
# Generate a new secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Update .env File
```bash
# Example .env contents
DEBUG=False
DJANGO_SECRET_KEY=your-generated-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
DJANGO_DB_PASSWORD=your-strong-db-password
```

### 4. Deploy with Docker
```bash
# Build and start services
sudo docker compose -f docker-compose.yml up -d --build

# Check service status
sudo docker compose ps

# View logs
sudo docker compose logs -f web
```

### 5. Initial Setup
```bash
# Collect static files
sudo docker compose exec web python manage.py collectstatic --noinput

# Run migrations
sudo docker compose exec web python manage.py migrate

# Create superuser
sudo docker compose exec web python manage.py createsuperuser
```

### 6. SSL Configuration (Optional)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Test renewal
sudo certbot renew --dry-run
```

## Monitoring and Maintenance

### 1. Logs
- Application logs: `sudo docker compose logs web`
- Nginx logs: `sudo docker compose logs nginx`
- Database logs: `sudo docker compose logs db`

### 2. Backup Strategy
```bash
# Database backup
sudo docker compose exec db pg_dump -U jozen jozen > backup_$(date +%Y%m%d_%H%M%S).sql

# Media files backup
sudo tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/
```

### 3. Updates
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
sudo docker compose down
sudo docker compose up -d --build
```

## Performance Optimization

### 1. Gunicorn Workers
- Default: 3 workers
- Recommended: (2 x CPU cores) + 1
- Adjust in docker-compose.yml

### 2. Database Optimization
- Enable connection pooling
- Regular VACUUM and ANALYZE
- Monitor slow queries

### 3. Caching
- Consider Redis for caching
- Enable Django's cache framework
- Use CDN for static files

## Troubleshooting

### Common Issues
1. **Static files not loading**: Run `collectstatic`
2. **Database connection errors**: Check environment variables
3. **Permission denied**: Check file ownership and Docker permissions
4. **Memory issues**: Adjust Gunicorn workers and database settings

### Health Checks
```bash
# Check all services
sudo docker compose ps

# Test web service
curl -I http://localhost:8000

# Check database
sudo docker compose exec db psql -U jozen -d jozen -c "SELECT version();"
```

## Security Recommendations

1. **Regular Updates**: Keep Docker images and system packages updated
2. **Monitoring**: Set up application and server monitoring
3. **Backups**: Implement automated backup strategy
4. **Access Control**: Limit server access to necessary personnel only
5. **Audit Logs**: Monitor and review access logs regularly

## Support
For issues and questions:
- Check logs first: `sudo docker compose logs`
- Review this documentation
- Check Django and Docker documentation
- Consider professional support for critical deployments
