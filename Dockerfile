# Install distutils for the default python3 (needed for pip build environments)
RUN apt-get update && apt-get install -y python3-distutils
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

# Set environment variables
## Trigger rebuild: dummy comment
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda


# Install system dependencies and Python 3.12
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y \
        python3.12 \
        python3.12-venv \
        python3.12-dev \
        python3-pip \
        git \
        wget \
        build-essential \
        libsndfile1 \
        ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set Python 3.12 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1

# Install distutils for Python 3.12 (required for pip)
RUN apt-get update && apt-get install -y curl

# Install pip for Python 3.12 using get-pip.py (since distutils is not available for 3.12)
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Set working directory
WORKDIR /app

# Clone and install magenta-realtime
RUN git clone https://github.com/magenta/magenta-realtime.git && \
    cd magenta-realtime && \
    pip install -e .[gpu] && \
    pip install tf2jax==0.3.8 huggingface_hub

# Install TensorFlow with text support
RUN pip uninstall -y tensorflow tensorflow-cpu tensorflow-text && \
    pip install tf-nightly==2.20.0.dev20250619 tensorflow-text-nightly==2.20.0.dev20250316

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Create cache directory for models
RUN mkdir -p /app/cache
ENV MAGENTA_RT_CACHE=/app/cache

# Expose port
EXPOSE 7860

# Run the application
CMD ["python", "main.py"]