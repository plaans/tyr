FROM ubuntu:jammy
ENV DEBIAN_FRONTEND="noninteractive" TZ="Europe/Paris"

# Install util packages
RUN apt update && apt upgrade -y
RUN apt install -y \
    build-essential \
    curl \
    git \
    wget

# Install Git-LFS
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash
RUN apt update
RUN apt install git-lfs

# Install Python from 3.8 to 3.12
RUN apt install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt update
RUN apt install -y \
    python3.8 \
    python3.8-venv \
    python3.8-dev \
    python3.9 \
    python3.9-venv \
    python3.9-dev \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3.12 \
    python3.12-venv \
    python3.12-dev

# Install Rust
RUN curl https://sh.rustup.rs | sh -s -- --no-modify-path -y
ENV PATH="${PATH}:/root/.cargo/bin"
RUN rustup update

# Install Just
RUN cargo install just

WORKDIR /root/workspace
