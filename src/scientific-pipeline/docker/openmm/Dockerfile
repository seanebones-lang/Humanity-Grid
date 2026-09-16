# OpenMM Container
# Base: NVIDIA CUDA 12.4 on Ubuntu 22.04

FROM nvidia/cuda:12.4-devel-ubuntu22.04 AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    python3-dev \
    python3-pip \
    libfftw3-dev \
    libxml2-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install OpenMM from source with CUDA support
WORKDIR /opt
RUN git clone --branch 8.0.0 --depth 1 https://github.com/openmm/openmm.git
WORKDIR /opt/openmm
RUN mkdir build && cd build && \
    cmake -DOPENMM_BUILD_CUDA_LIB=ON -DCUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda .. && \
    make -j$(nproc) && \
    make install

# --- Runtime Stage ---
FROM nvidia/cuda:12.4-runtime-ubuntu22.04

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    libfftw3-3 \
    libxml2 \
    zlib1g \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

# Copy OpenMM libraries from builder
COPY --from=builder /usr/local/lib/libOpenMM* /usr/local/lib/
COPY --from=builder /usr/local/include/openmm /usr/local/include/openmm
COPY --from=builder /usr/local/lib/python3.10/dist-packages/openmm /usr/local/lib/python3.10/dist-packages/openmm

# Install Python packages
RUN pip3 install --no-cache-dir \
    numpy \
    pandas \
    polars \
    pyarrow \
    openmm==8.0.0 \
    openmmtools \
    pdbfixer \
    mdtraj \
    mdanalysis \
    rdkit

# Create app user
RUN useradd -m -u 1000 -s /bin/bash appuser
WORKDIR /app

# Copy entrypoint and runner scripts
COPY entrypoint.sh /app/entrypoint.sh
COPY run.py /app/run.py
COPY setup_system.py /app/setup_system.py
COPY analyze.py /app/analyze.py
RUN chmod +x /app/entrypoint.sh && chown -R appuser:appuser /app

USER appuser

ENTRYPOINT ["/app/entrypoint.sh"]