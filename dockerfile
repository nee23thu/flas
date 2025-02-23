# Use an official Python 3.10+ image as the base
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy only requirements file to leverage Docker's caching mechanism
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose the application port
EXPOSE 5000

# Define environment variables (Optional)
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Command to run the application
CMD ["flask", "run"]
