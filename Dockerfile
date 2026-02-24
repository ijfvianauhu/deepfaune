# CPU image (no CUDA). Uses Debian slim for stability.
FROM python:3.10-slim

# Avoid interactive prompts and speed up Python
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

ARG USERID
ARG GROUPID

ENV APP_CONFIG_DIR=/config

# (opcional) si NO quieres ejecutar como root, crea usuario y dale permisos:
# RUN useradd -m appuser && chown -R appuser:appuser /config /app
# RUN groupadd -g ${GROUPID} appgroup && useradd -m -u ${USERID} -g ${GROUPID} appuser
# USER appuser

RUN mkdir -p /config
RUN mkdir -p /data

# System deps:
# - python3-tk: tkinter for PySimpleGUI GUI
# - libs often needed by PIL/opencv and ML tooling
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-tk \
    tk \
    tcl \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project
# (Assumes you build from the deepfaune source directory where deepfauneGUI.py lives)
COPY software /app
COPY requirements.txt /app

RUN curl -L \
    https://pbil.univ-lyon1.fr/software/download/deepfaune/v1.4/deepfaune-yolov8s_960.pt \
    -o /app/deepfaune-yolov8s_960.pt

RUN curl -L \
    https://pbil.univ-lyon1.fr/software/download/deepfaune/v1.4/md_v1000.0.0.pt \
    -o /app/md_v1000.0.0-sorrel.pt

RUN curl -L \
    https://pbil.univ-lyon1.fr/software/download/deepfaune/v1.4/md_v1000.0.0-redwood.pt \
    -o /app/md_v1000.0.0-redwood.pt

RUN curl -L \
    https://pbil.univ-lyon1.fr/software/download/deepfaune/v1.4/deepfaune-vit_large_patch14_dinov2.lvd142m.v4.pt \
    -o /app/deepfaune-vit_large_patch14_dinov2.lvd142m.v4.pt

RUN curl -L \
    https://pbil.univ-lyon1.fr/software/download/deepfaune/v1.4/deepfaune-vit_large_patch14_dinov2.lvd142m.v4-bird_head.pt \
    -o /app/deepfaune-vit_large_patch14_dinov2.lvd142m.v4-bird_head.pt

# Install Python deps
# If your project has requirements.txt, this will work.
# If it doesn't, tell me what file it uses and I adapt it.
RUN python -m pip install --upgrade pip setuptools wheel && \
    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Optional: if deepfaune is a package with pyproject.toml/setup.py, install it
RUN if [ -f pyproject.toml ] || [ -f setup.py ]; then pip install -e .; fi

# Default: run the GUI
CMD ["python", "./deepfauneGUI.py"]
