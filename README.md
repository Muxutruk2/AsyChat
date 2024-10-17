# AsyChat

![Asychat Logo and Text](/media/AsyChatLogo_text_back.png)

AsyChat is a web-based chat with assymetric encryption made for secure decentralized messaging. The client acts as a front-end to the server, which acts like an API.

## Explanation

## Installation

Clone the repository and "cd" into it

```bash
git clone https://github.com/Muxutruk2/AsyChat && cd AsyChat
```

(optional) Create a .venv and source it
```bash
python3 -m venv .venv && source .venv/bin/activate
```

Install the requirements
```bash
pip install -r requirements.txt
```

Create these folders
```bash
mkdir client/keys server/keys server/allowed_keys
```

Generate the key pairs
```bash
python3 -m gen_keys
```

## Usage

### Authorize keys
To add an authorized key to the server you can either:

1. Copy the public key to server/allowed_keys

For example: `cp client/keys/client_public_key.pem server/allowed_keys/local_key.pem` to allow connecting to the server in the same machine

2. Run `python3 -m add_key [client IP]` while client is running

### Run server/client

`python3 -m server.server`

`python3 -m client.client`
