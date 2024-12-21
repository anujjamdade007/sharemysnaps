# Use the official Python image from Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install core dependencies.
RUN apt-get update && apt-get install -y libpq-dev build-essential

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /app/

# Set environment variables for Django
ENV PYTHONUNBUFFERED=1

# Expose the port that Django runs on (port 80)
EXPOSE 80

# Command to run the application (use port 80)
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
