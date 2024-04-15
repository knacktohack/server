# Set base image (host OS)
FROM --platform=linux/amd64 python:3.11-alpine
RUN apk add --no-cache --update \
    python3 python3-dev gcc \
    gfortran musl-dev g++ \
    libffi-dev openssl-dev \
    libxml2 libxml2-dev \
    libxslt libxslt-dev \
    libjpeg-turbo-dev zlib-dev \
    linux-headers
# By default, listen on port 8000
EXPOSE 8000/tcp

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements2.txt .
# RUN pip install --upgrade pip
# RUN pip install --upgrade cython
RUN pip install  --no-cache-dir -r requirements2.txt

COPY core ./core
COPY app.py .
COPY run.py .
COPY .env .env

# Install any dependencies

# Copy the content of the local src directory to the working directory

# Specify the command to run on container start
CMD [ "python", "./run.py" ]