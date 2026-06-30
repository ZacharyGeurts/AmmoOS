# Grok16 reproducible bootstrap (Linux x86_64)
FROM ubuntu:24.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    git cmake python3 ca-certificates ccache \
    libgmp-dev libmpfr-dev libmpc-dev flex bison texinfo gawk \
    zlib1g-dev libzstd-dev make && rm -rf /var/lib/apt/lists/*

WORKDIR /grok16
COPY . .

ENV G16_PREFIX=/grok16 \
    GROK16_ROOT=/grok16 \
    GROK16_USE_CCACHE=1 \
    G16_FAST_REBUILD=1

RUN ./scripts/grok16-binutils.sh bootstrap && \
    ./scripts/grok16-toolchain.sh bootstrap && \
    ./scripts/grok16-toolchain.sh verify && \
    ./scripts/grok16-binutils.sh verify && \
    ./scripts/grok16-toolchain.sh field-bench