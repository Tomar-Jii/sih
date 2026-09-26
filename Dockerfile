FROM python:3.10
WORKDIR /app

# Install OpenCV dependencies for Linux
RUN apt-get update && apt-get install -y libgl1

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY . .

# Expose port 7860 (Hugging Face default)
EXPOSE 7860

# Command to run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
