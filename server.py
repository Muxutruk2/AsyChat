# server.py
from flask import Flask, request, jsonify
import requests
from database import init_db, store_message, get_messages
from encryption import *
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  
# Initialize the database
init_db()

# Paths to server's keys
SERVER_PRIVATE_KEY_PATH = './keys/server_private_key.pem'
SERVER_PUBLIC_KEY_PATH = './keys/server_public_key.pem'


def load_allowed_public_keys(directory):
    """Load allowed public keys from the specified directory."""
    allowed_keys = {}
    
    for filename in os.listdir(directory):
        if filename.endswith('.pem'):
            file_path = os.path.join(directory, filename)
            public_key = load_public_key_file(file_path)

            hash = get_public_key_hash(public_key)
            allowed_keys[filename] = hash  # Store key with filename as identifier

    return allowed_keys

allowed_keys_directory = './allowed_keys'
allowed_public_keys = load_allowed_public_keys(allowed_keys_directory)

def is_key_allowed(public_key):
    """Check if a public key is in the allowed keys."""
    print(f"searching {public_key} in: ")
    [print(f"\n\t{i}") for i in allowed_public_keys.values()]

    return public_key in allowed_public_keys.values()

@app.route('/public_key', methods=['GET'])
def public_key():
    # Serve the server's public key
    with open(SERVER_PUBLIC_KEY_PATH, 'r') as key_file:
        return jsonify({'public_key': key_file.read()}), 200

@app.route('/messages', methods=['GET'])
def get_encrypted_messages():
    # Request client's public key
    client_ip = request.remote_addr
    print(f"[ {client_ip} ] aksed for messages")
    client_public_key_url = f'http://{client_ip}:5000/public_key'
    
    response = requests.get(client_public_key_url)
    print(f"[ {client_ip} ] Recieved client's public key with status code: {response.status_code}")
    client_public_key_str = response.json().get('public_key')
    print(f"[ {client_ip} ] Recieved client's public key starts with {client_public_key_str[0:40]}")
    client_public_key_pem = load_public_key(client_public_key_str)
    client_public_key_hash = get_public_key_hash(client_public_key_pem)
    print(f"[ {client_ip} ] Recieved client's public key's hash is {client_public_key_hash}")
    client_public_key_pem = load_public_key(client_public_key_str)

    # Check if the client's public key is authorized
    if not is_key_allowed(client_public_key_hash):
        print(f"[ {client_ip} ] Unauthorized client.")
        return jsonify({"error": "Unauthorized public key"}), 403

    print(f"[ {client_ip} ] Client authorized.")

    # Encrypt messages with client's public key
    messages = get_messages()
    if len(messages) > 0:
        print(f"[ {client_ip} ] Sending {len(messages)} messages. First one: {messages[0]}")
    else:
        print(f"[ {client_ip} ] Sending 0 messages")
    encrypted_messages = [
        encrypt_message(f"{nickname}: {content}", client_public_key_pem).hex() 
        for nickname, content in messages
    ]

    return jsonify({"messages": encrypted_messages}), 200

@app.route('/send_message', methods=['POST'])
def receive_message():
    encrypted_message = bytes.fromhex(request.json.get('message'))
    nickname = request.json.get('nickname')

    print(f"User {nickname} sent encrypted message starting with {encrypted_message[0:20]}")

    # Get client's public key
    client_ip = request.remote_addr
    client_public_key_url = f'http://{client_ip}:5000/public_key'

    response = requests.get(client_public_key_url)
    client_public_key_str = response.json().get('public_key')
    client_public_key_pem = load_public_key(client_public_key_str)
    client_public_key_hash = get_public_key_hash(client_public_key_pem)

    # Check if the public key is authorized
    if not is_key_allowed(client_public_key_hash):
        return jsonify({"error": "Unauthorized public key"}), 403

    # Decrypt the message
    server_private_key = load_private_key_file(SERVER_PRIVATE_KEY_PATH)
    decrypted_message = decrypt_message(encrypted_message, server_private_key)

    # Store the decrypted message in the database
    store_message(nickname, decrypted_message)
    
    return jsonify({"status": "Message stored successfully"}), 200

if __name__ == '__main__':
    app.run(port=5001)

