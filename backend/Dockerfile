FROM nvidia/cuda:12.2.0-cudnn8-runtime-ubuntu22.04

# System packages
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv git ffmpeg wget && \
    rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Copy app
COPY app/ /app/

# Python deps
RUN pip3 install --no-cache-dir -r requirements.txt

# Clone Practical-RIFE and fetch models
RUN git clone --depth=1 https://github.com/hzwer/Practical-RIFE.git /opt/rife && \
    pip3 install --no-cache-dir -r /opt/rife/requirements.txt && \
    mkdir -p /opt/rife/models && \
    python3 - <<'PY'
import os,urllib.request
# Fetch a commonly used model weights pack (RIFE v4.6). URLs may change; update if needed.
# Mirror 1
url = 'https://github.com/hzwer/Practical-RIFE/releases/download/v4.6.0/RIFE_trained_model_v4.6.zip'
out = '/opt/rife/models/rife46.zip'
os.makedirs('/opt/rife/models', exist_ok=True)
try:
    urllib.request.urlretrieve(url, out)
except Exception as e:
    print('WARNING: could not download pre-trained weights automatically:', e)
PY

# Unzip if present
RUN set -eux; \
    if [ -f /opt/rife/models/rife46.zip ]; then \
      apt-get update && apt-get install -y unzip && rm -rf /var/lib/apt/lists/*; \
      unzip -o /opt/rife/models/rife46.zip -d /opt/rife/; \
    fi

ENV TORCH_USE_CUDA_DSA=1
ENV STORAGE=/data
RUN mkdir -p ${STORAGE}

EXPOSE 8000
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]