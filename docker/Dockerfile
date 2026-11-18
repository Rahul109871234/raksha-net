FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends iproute2 iperf3 iputils-ping docker.io && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
# Optional real ML-KEM:  pip install liboqs-python  (requires liboqs built in image)
CMD ["python", "-m", "scripts.node_stub", "X"]
