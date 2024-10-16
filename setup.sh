#!/bin/env bash

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

mkdir client/keys server/keys server/allowed_keys

python3 -m gen_keys
cp keys/client_public_key.pem allowed_keys

echo "Installation complete"


