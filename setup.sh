#!/bin/env bash

mkdir keys allowed_keys
touch chat_server.db

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python3 -m gen_keys
cp keys/client_public_key.pem allowed_keys

echo "Installation complete"


