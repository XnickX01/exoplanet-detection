FROM python:3.11-bullseye

# Install dependencies and Node.js v18
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Set working directory
WORKDIR /app

# Copy project files into the image
COPY . /app

# Ensure run_all.sh is executable
RUN chmod +x run_all.sh

# Expose ports used by your API and Angular dashboard (adjust as needed)
EXPOSE 4200 5000

# Run the startup script
CMD ["./run_all.sh"]