FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Install Playwright browsers
RUN playwright install chromium

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_HEADLESS=true

# Default command
CMD ["python", "weasel.py"]
