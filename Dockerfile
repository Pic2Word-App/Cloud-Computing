# Use the official Python 3.11 image from Docker Hub
FROM python:3.11-slim

# Set the working directory to root
WORKDIR /

# Copy the requirements.txt file into the working directory
COPY requirements.txt /

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /

# Expose the port that the app will run on
EXPOSE 8080

# Command to run the application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

# Command to run the application using fastapi
# CMD ["fastapi", "run", "main.py"]
