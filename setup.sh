#!/bin/bash

# AsyChat Setup Script

# Function to print messages
function print_message() {
    echo -e "\n=== $1 ===\n"
}

# Function to ask for user confirmation
function confirm() {
    read -p "$1 (y/n)? " choice
    case "$choice" in 
        y|Y ) return 0 ;;
        n|N ) return 1 ;;
        * ) echo "Invalid input"; confirm "$1" ;;
    esac
}

# Clone the repository
print_message "Cloning the AsyChat repository"
git clone https://github.com/Muxutruk2/AsyChat && cd AsyChat || exit

# Ask if the user wants to create and activate a virtual environment
if confirm "Do you want to create a virtual environment?"; then
    print_message "Creating a virtual environment"
    python3 -m venv .venv && source .venv/bin/activate
fi

# Install the required packages
print_message "Installing requirements"
pip install -r requirements.txt

# Create necessary folders
print_message "Creating necessary directories"
mkdir -p client/keys server/keys server/allowed_keys

# Generate key pairs
print_message "Generating key pairs"
python3 -m gen_keys

# Ask if the user wants to copy the local client's public key to the server's allowed keys
if confirm "Do you want to copy the local client's public key to the server's allowed keys?"; then
    echo "Please provide the name for the local public key file (e.g., local_key.pem):"
    read local_key_name
    cp client/keys/client_public_key.pem server/allowed_keys/"$local_key_name"
    echo "Public key copied as server/allowed_keys/$local_key_name."
fi

# Instructions for running the server and client
print_message "Running the server and client"
echo "To run the server, execute: python3 -m server.server"
echo "To run the client, execute: python3 -m client.client"
echo "Ensure you have the required keys set up before starting."

print_message "Setup complete!"

