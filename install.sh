#!/bin/bash

set -e

python3 -m venv .venv
source .venv/bin/activate
cargo build --release --bin up-server --manifest-path libs/aries/Cargo.toml
cp libs/aries/target/release/up-server libs/aries/planning/unified/plugin/up_aries/bin/up-aries_linux_amd64
pip install -r requirements/prod.txt
