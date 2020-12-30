# Official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.8.5-slim

# Install ps command
RUN apt update \
 && apt install -y procps \
 && rm -rf /var/lib/apt/lists/*

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Production dependencies.
RUN pip install --upgrade pip && pip install -r requirements.txt

# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec python main.py --client=${LIGHTYEAR_CLIENT}
