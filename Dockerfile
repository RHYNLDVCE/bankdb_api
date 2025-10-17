# Dockerfile

# 1. Start with an official Python base image
# We choose a specific version for consistency.
FROM python:3.11-slim

# 2. Set environment variables
# This tells Python not to buffer output and not to write .pyc files.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# 3. Set the working directory inside the container
# All subsequent commands will run from here.
WORKDIR /app

# 4. Copy the dependency file and install dependencies
# We copy only the requirements file first to take advantage of Docker's caching.
# The dependencies will only be re-installed if this file changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your application's code into the container
COPY . .

# 6. Expose the port the app runs on
# This tells Docker which port to make available to the outside world.
EXPOSE 8500