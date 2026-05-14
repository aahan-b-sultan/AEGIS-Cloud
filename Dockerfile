# 1. Base Image: Official Python 3.10
FROM python:3.10-slim

# 2. Set Environment Variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set Work Directory
WORKDIR /app

# 4. Install System Dependencies (Added 'unzip')
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 5. Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the Application Code (This copies the .zip, but ignores the folder thanks to .gitignore)
COPY . .

# 7. Hugging Face Permission Fix
RUN useradd -m -u 1000 user
RUN chown -R user:user /app
USER user

# 8. Expose the Hugging Face Port
EXPOSE 7860

# 9. Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]