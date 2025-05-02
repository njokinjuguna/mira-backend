# Use a slim Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Run the FastAPI app (adjusted for your app inside mira/api/main.py)
CMD ["uvicorn", "mira.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
