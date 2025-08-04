# Use a multi-stage build for efficiency
# Stage 1: Build Rust scheduler
FROM rust:1.65 AS rust-builder

WORKDIR /app/backend/rust
COPY backend/rust/ .
RUN cargo build --release

# Stage 2: Build React frontend
FROM node:16 AS node-builder

WORKDIR /app/frontend
COPY frontend/ .
RUN npm install && npm run build

# Stage 3: Final image with Python and runtime
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Rust (needed for PyO3 runtime linking)
ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Set working directory
WORKDIR /app

# Copy Python backend
COPY backend/python /app/backend/python
COPY backend/python/requirements.txt /app/backend/python/

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/backend/python/requirements.txt

# Copy Rust scheduler binary from rust-builder stage
COPY --from=rust-builder /app/backend/rust/target/release/libpyo3_runtime.so /app/backend/python/pyo3_runtime.so

# Copy React build from node-builder stage
COPY --from=node-builder /app/frontend/build /app/frontend/build

# Install serve to host React frontend
RUN npm install -g serve

# Expose ports for FastAPI backend (8000) and React frontend (3000)
EXPOSE 8000 3000

# Start FastAPI and React frontend
CMD ["sh", "-c", "cd /app/frontend && serve -s build -l 3000 & cd /app/backend/python && uvicorn main:app --host 0.0.0.0 --port 8000"]
