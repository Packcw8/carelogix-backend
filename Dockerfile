FROM python:3.11-slim

# Install LibreOffice and system dependencies
RUN apt-get update && apt-get install -y libreoffice curl && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy your code
COPY . /app

# Install Python packages
RUN pip install --upgrade pip && pip install -r requirements.txt

# Run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
