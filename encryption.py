# encryption.py
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

# Function to generate a new key pair
def generate_key_pair(private_key_path, public_key_path):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    # Store private key
    with open(private_key_path, "wb") as private_file:
        private_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # Store public key
    with open(public_key_path, "wb") as public_file:
        public_file.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

def load_public_key(public_key_str):
    """Load public key from a string."""
    return serialization.load_pem_public_key(public_key_str.encode('utf-8'))

def load_private_key(private_key_str):
    """Load private key from a string."""
    print(f"Loading private key starting with {private_key_str[0:20]}")
    return serialization.load_pem_private_key(private_key_str.encode('utf-8'), password=None)

def load_public_key_file(public_key_path):
    """Load public key from a file."""
    with open(public_key_path, "rb") as public_file:
        return serialization.load_pem_public_key(public_file.read())

def load_private_key_file(private_key_path):
    """Load private key from a file."""
    with open(private_key_path, "rb") as private_file:
        return serialization.load_pem_private_key(private_file.read(), password=None)

# Encrypt a message with a public key
def encrypt_message(message, public_key):
    return public_key.encrypt(
        message.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

# Decrypt a message with a private key
def decrypt_message(encrypted_message, private_key):
    return private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    ).decode('utf-8')

