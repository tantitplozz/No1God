FROM python:3.11-slim-buster

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libfontconfig1 \
    libgconf-2-4 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm-dev \
    libgbm-dev \
    libgtk-3-0 \
    libnspr4 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxkbcommon0 \
    libxshmfence-dev \
    libxext-dev \
    libxrandr-dev \
    libxrender-dev \
    libxtst-dev \
    libappindicator3-1 \
    libdbus-glib-1-2 \
    libgdk-pixbuf2.0-0 \
    libnotify4 \
    libpangocairo-1.0-0 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxcb-present0 \
    libxcb-sync1 \
    libxcursor-dev \
    libxi-dev \
    libxinerama-dev \
    libxmu-dev \
    libxxf86vm-dev \
    fonts-liberation \
    xdg-utils \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium

# Copy the rest of the application code
COPY agent /app/agent
COPY data /app/data
COPY logs /app/logs

# Create necessary directories if they don't exist
RUN mkdir -p /app/data/traces /app/data/vault /app/logs

# Set environment variables for Playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright/

CMD ["python", "./agent/main.py"]


