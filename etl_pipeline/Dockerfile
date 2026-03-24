# Extend the official Airflow image with ETL-specific Python dependencies
FROM apache/airflow:2.9.3-python3.11

USER root

# System deps needed by some HuggingFace / tokenizer packages
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install CPU-only PyTorch first to avoid downloading multi-GB CUDA packages
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy and install remaining Python requirements (layer-cache friendly)
COPY requirements.txt /opt/airflow/requirements.txt
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt

# Copy pipeline source so it is available as Python packages inside the image.
# In development you can bind-mount these instead (see docker-compose.yaml).
COPY config/  /opt/airflow/config/
COPY tasks/   /opt/airflow/tasks/
COPY dags/    /opt/airflow/dags/
