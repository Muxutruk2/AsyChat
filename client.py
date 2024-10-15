# client.py
from flask import Flask, render_template, request, jsonify, redirect
import requests
from encryption import *
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  

# Paths to client's keys
CLIENT_PRIVATE_KEY_PATH = './keys/client_private_key.pem'
CLIENT_PUBLIC_KEY_PATH = './keys/client_public_key.pem'

server_ip = "localhost"

@app.route('/', methods=['GET'])
def index(): 
    return render_template('connect.html')

@app.route('/chat', methods=['GET'])
def get_messages():
    # Request messages from the server
    response = requests.get(f'http://{server_ip}:5001/messages')
    encrypted_messages = response.json().get('messages')
    print("Client recieved encrypted_messages: ", encrypted_messages)

    # Decrypt messages
    client_private_key = load_private_key_file(CLIENT_PRIVATE_KEY_PATH)
    decrypted_messages = [
        decrypt_message(bytes.fromhex(msg), client_private_key)
        for msg in encrypted_messages
    ]

    print("Client recieved messages: ", decrypted_messages)

    return render_template('chat.html', messages=decrypted_messages)


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    nickname = data['nickname'] 
    message = data['message']
    server_ip = data['server']

    print(f"{nickname=}\n{message=}")

    # Get server's public key
    response = requests.get(f'http://{server_ip}:5001/public_key')
    server_public_key_pem = response.json().get('public_key')
    server_public_key = load_public_key(server_public_key_pem)

    # Encrypt the message
    encrypted_message = encrypt_message(message, server_public_key)

    # Send encrypted message to server
    sent_request = requests.post(f'http://{server_ip}:5001/send_message', json={
        'nickname': nickname,
        'message': encrypted_message.hex()
    })

    if sent_request.status_code != 200:
        return sent_request.json(), sent_request.status_code

    return redirect('/') 
@app.route('/public_key', methods=['GET'])
def public_key():
    # Serve the client's public key
    with open(CLIENT_PUBLIC_KEY_PATH, 'r') as key_file:
        return jsonify({'public_key': key_file.read()}), 200

if __name__ == '__main__':
    app.run(port=5000)

