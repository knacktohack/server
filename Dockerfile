# Set base image (host OS)
FROM --platform=linux/amd64 python:3.9-alpine
RUN apk update && \
    apk add --no-cache gfortran musl-dev g++ gcc libxslt-dev libxml2-dev libffi-dev openssl-dev libgcc libstdc++ 
# By default, listen on port 8000
EXPOSE 8000/tcp

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements2.txt .
RUN pip3 install -r requirements2.txt

COPY core ./core
COPY app.py .
COPY run.py .
COPY .env .env

# Install any dependencies

# Copy the content of the local src directory to the working directory

# Specify the command to run on container start
CMD [ "python", "./run.py" ]