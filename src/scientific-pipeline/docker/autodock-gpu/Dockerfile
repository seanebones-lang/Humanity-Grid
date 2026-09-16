# AutoDock-GPU Container
# Base: NVIDIA CUDA 12.4 on Ubuntu 22.04

FROM nvidia/cuda:12.4-devel-ubuntu22.04 AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    python3-dev \
    python3-pip \
    libboost-all-dev \
    libfftw3-dev \
    libxml2-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --no-cache-dir numpy pandas polars pyarrow rdkit

# Build AutoDock-GPU from source
WORKDIR /opt
RUN git clone --branch develop --depth 1 https://github.com/ccsb-scripps/AutoDock-GPU.git
WORKDIR /opt/AutoDock-GPU
RUN mkdir build && cd build && \
    cmake -DCUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda .. && \
    make -j$(nproc)

# Build AutoDock-Vina as CPU fallback
WORKDIR /opt
RUN git clone --depth 1 https://github.com/ccsb-scripps/AutoDock-Vina.git
WORKDIR /opt/AutoDock-Vina/build
RUN cmake .. && make -j$(nproc)

# --- Runtime Stage ---
FROM nvidia/cuda:12.4-runtime-ubuntu22.04

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    libfftw3-3 \
    libxml2 \
    zlib1g \
    libboost-system1.74 \
    libboost-filesystem1.74 \
    libboost-thread1.74 \
    libboost-chrono1.74 \
    libboost-atomic1.74 \
    libboost-date-time1.74 \
    libboost-regex1.74 \
    libboost-serialization1.74 \
    && rm -rf /var/lib/apt/lists/*

# Copy binaries from builder
COPY --from=builder /opt/AutoDock-GPU/build/autodock_gpu_128wi /usr/local/bin/autodock_gpu
COPY --from=builder /opt/AutoDock-Vina/build/vina /usr/local/bin/vina

# Install Python packages
RUN pip3 install --no-cache-dir numpy pandas polars pyarrow rdkit

# Create app user
RUN useradd -m -u 1000 -s /bin/bash appuser
WORKDIR /app

# Copy entrypoint and runner scripts
COPY entrypoint.sh /app/entrypoint.sh
COPY run.py /app/run.py
COPY prepare_receptor.py /app/prepare_receptor.py
COPY prepare_ligands.py /app/prepare_ligands.py
RUN chmod +x /app/entrypoint.sh && chown -R appuser:appuser /app

USER appuser

# Default entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]