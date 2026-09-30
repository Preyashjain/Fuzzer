# Minimal, reproducible environment for the exercise.
# Build:  docker build -t fuzzing-exercise .
# Run:    docker run --rm fuzzing-exercise
FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /exercise
COPY target/ target/
COPY fuzzer/ fuzzer/
COPY checker/ checker/

RUN gcc -O0 -fno-stack-protector -o target/lookup target/lookup.c

# Default: run the fuzzer, then independently verify what it found.
CMD python3 fuzzer/fuzz.py --target target/lookup --iterations 2000 --seed 42 --out fuzzer/crashes \
    && python3 checker/verify.py --target target/lookup --crashes-dir fuzzer/crashes
