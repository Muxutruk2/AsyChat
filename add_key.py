import requests
import encryption
from cryptography.hazmat.backends import default_backend
import sys

key_holder_ip = sys.argv[1] 
if key_holder_ip is None:
    print("Usage: python3 add_key.py [IP]")

request = requests.get(f'http://{key_holder_ip}:5000/public_key')
if request.status_code != 200:
    print(f"ERROR. Client responded with {request.status_code}")
    exit(1)
try:
    public_key = request.json()['public_key']

except Exception as e:
    print(f"Could not convert the response to json: ", e)
    print(request)
    exit(1)

print(f"{request=}\n{public_key=}")

key_pem = encryption.load_public_key(public_key)
key_hash = encryption.get_public_key_hash(key_pem)

print(key_hash)
print(key_hash.hex())

with open(f'./allowed_keys/public_key_{key_hash.hex()[0:20]}.pem', 'w') as f:
    f.write(public_key)



