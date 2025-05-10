# Use a slim Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory inside the container
WORKDIR /app

# Install system dependencies for psycopg2/PostgreSQL, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend files into container
COPY . .

# Run database migrations
RUN python manage.py migrate || echo "Migration failed (likely due to missing DB during build)"

# Collect static files (skip errors if no static config)
RUN python manage.py collectstatic --noinput || true

# Expose port for Railway
EXPOSE 8000

# Start the Django app using Gunicorn
CMD ["gunicorn", "chatbot_project.wsgi:application", "--bind", "0.0.0.0:8000"]
