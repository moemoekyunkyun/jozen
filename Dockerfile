FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Set environment variables for collectstatic
ENV DJANGO_SETTINGS_MODULE=jozen.settings
ENV DJANGO_SECRET_KEY=dummy-key-for-build
ENV DEBUG=False

# Collect static files
RUN python manage.py collectstatic --noinput --clear

EXPOSE 8000
CMD ["gunicorn", "jozen.wsgi:application", "--bind", "0.0.0.0:8000"]
