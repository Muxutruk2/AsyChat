# server.py
from flask import Flask, request, jsonify
import requests
from database import init_db, store_message, get_messages
from encryption import *
import os
import sys
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  
# Initialize the database
init_db()

if len(sys.argv) == 1:
    app.logger.setLevel(30) # Warning
elif sys.argv[1] == '-v':
    app.logger.setLevel(20) # Info
elif sys.argv[1] == '-vv':
    app.logger.setLevel(10) # Debug

# Paths to server's keys
SERVER_PRIVATE_KEY_PATH = 'server/keys/server_private_key.pem'
SERVER_PUBLIC_KEY_PATH = 'server/keys/server_public_key.pem'

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

allowed_keys_directory = 'server/allowed_keys'
allowed_public_keys = load_allowed_public_keys(allowed_keys_directory)

def is_key_allowed(public_key):
    """Check if a public key is in the allowed keys."""
    formatted_allowed_keys =  '\n\t'.join([i.hex() for i in allowed_public_keys.values()])
    app.logger.debug(f"searching {public_key.hex()} in: {formatted_allowed_keys}")

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
    app.logger.debug(f"[ {client_ip} ] aksed for messages")
    client_public_key_url = f'http://{client_ip}:5000/public_key'
    
    response = requests.get(client_public_key_url)
    app.logger.debug(f"[ {client_ip} ] Recieved client's public key with status code: {response.status_code}")
    client_public_key_str = response.json().get('public_key')
    app.logger.debug(f"[ {client_ip} ] Recieved client's public key starts with {client_public_key_str[0:40]}")
    client_public_key_pem = load_public_key(client_public_key_str)
    client_public_key_hash = get_public_key_hash(client_public_key_pem)
    app.logger.debug(f"[ {client_ip} ] Recieved client's public key's hash is {client_public_key_hash.hex()}")
    client_public_key_pem = load_public_key(client_public_key_str)

    # Check if the client's public key is authorized
    if not is_key_allowed(client_public_key_hash):
        app.logger.debug(f"[ {client_ip} ] Unauthorized client.")
        return jsonify({"error": "Unauthorized public key"}), 403

    app.logger.debug(f"[ {client_ip} ] Client authorized.")

    # Encrypt messages with client's public key
    messages = get_messages()
    if len(messages) > 0:
        app.logger.debug(f"[ {client_ip} ] Sending {len(messages)} messages. Last one: {messages[-1]}")
    else:
        app.logger.debug(f"[ {client_ip} ] Sending 0 messages")
    encrypted_messages = [
        encrypt_message(f"{nickname}: {content}", client_public_key_pem).hex() 
        for nickname, content in messages
    ]

    return jsonify({"messages": encrypted_messages}), 200

@app.route('/send_message', methods=['POST'])
def receive_message():
    if request.json is None:
        return jsonify({"error": "Could not parse json from request"}), 400

    encrypted_message = bytes.fromhex(request.json.get('message'))
    nickname = request.json.get('nickname')

    if encrypted_message is None or nickname is None:
        return jsonify({"error": "Nickname or message is empty or not possible to decrypt"})

    app.logger.debug(f"User {nickname} sent encrypted message starting with {encrypted_message[0:20]}")

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
    app.run(host="0.0.0.0", port=5001)

