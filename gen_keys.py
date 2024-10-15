from encryption import generate_key_pair
import os

# Directories where the keys will be stored
KEYS_DIR = './keys/'

# Ensure the directory exists
if not os.path.exists(KEYS_DIR):
    os.makedirs(KEYS_DIR)

# Paths for private and public key files
CLIENT_PRIVATE_KEY_PATH = os.path.join(KEYS_DIR, 'client_private_key.pem')
CLIENT_PUBLIC_KEY_PATH = os.path.join(KEYS_DIR, 'client_public_key.pem')

SERVER_PRIVATE_KEY_PATH = os.path.join(KEYS_DIR, 'server_private_key.pem')
SERVER_PUBLIC_KEY_PATH = os.path.join(KEYS_DIR, 'server_public_key.pem')
# Generate RSA key pair
generate_key_pair(CLIENT_PRIVATE_KEY_PATH, CLIENT_PUBLIC_KEY_PATH)
generate_key_pair(SERVER_PRIVATE_KEY_PATH, SERVER_PUBLIC_KEY_PATH)

