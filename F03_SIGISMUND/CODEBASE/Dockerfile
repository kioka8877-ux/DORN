FROM node:20-bookworm-slim

# 1. Outils systeme
RUN apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      chromium \
      ffmpeg \
      wget \
      unzip \
      ca-certificates \
      fontconfig \
      fonts-liberation && \
    fc-cache -fv && \
    rm -rf /var/lib/apt/lists/*

# 2. node_modules pre-installes
WORKDIR /dorn-deps
COPY package.json package-lock.json* ./
RUN npm install && \
    echo "[DEPS] node_modules : $(du -sh node_modules | cut -f1)"

# 3. Variables d'environnement
ENV DORN_DEPS=/dorn-deps
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV CHROMIUM_PATH=/usr/bin/chromium

# 4. Sanity check
RUN node --version && \
    which chromium && \
    which ffmpeg && \
    ls /dorn-deps/node_modules | wc -l && echo "modules OK"
