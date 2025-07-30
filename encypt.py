import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from src.utils.config import config
# Replace these
ACCESS_TOKEN = config.WHATSAPP_KEY # Your system user access token
APP_ID = config.APP_ID
APP_SECRET = config.APP_SECRET
PHONE_NUMBER_ID = config.PHONE_NUMBER_ID
PUBLIC_KEY_PATH = "public.pem"

GRAPH_VERSION = "v23.0"

# Step 1: Validate token
def check_access_token():
    print("🔍 Verifying access token permissions...")
    url = f"https://graph.facebook.com/debug_token"
    params = {
        "input_token": ACCESS_TOKEN,
        "access_token": f"{APP_ID}|{APP_SECRET}"
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "data" not in data or not data["data"].get("is_valid"):
        raise Exception("❌ Invalid or expired access token.")
    
    scopes = data["data"].get("scopes", [])
    if "whatsapp_business_messaging" not in scopes:
        raise Exception("❌ Access token missing 'whatsapp_business_messaging' permission.")
    
    print("✅ Token is valid and has required permissions.")
    return True

# Step 2: Load and verify RSA key
def load_and_validate_public_key():
    print("🔍 Validating RSA public key...")
    with open(PUBLIC_KEY_PATH, "rb") as f:
        key_data = f.read()

    public_key = serialization.load_pem_public_key(key_data, backend=default_backend())

    # Check if it's a 2048-bit RSA key
    try:
        key_size = public_key.key_size
        if key_size != 2048:
            raise Exception(f"❌ Invalid RSA key size: {key_size}. Must be 2048 bits.")
        print("✅ RSA key is valid and 2048 bits.")
    except AttributeError:
        raise Exception("❌ The loaded key is not an RSA key.")

    return key_data.decode("utf-8")

# Step 3: Upload public key to Meta
import re

def clean_pem(pem: str) -> str:
    """Strip trailing whitespace and encode newlines for form submission."""
    lines = pem.strip().splitlines()
    return "\\n".join(line.strip() for line in lines if line.strip())

def send_public_key(public_key_str):
    print("🚀 Sending public key to Meta...")

    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PHONE_NUMBER_ID}/whatsapp_business_encryption"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # Requests will handle encoding safely if passed as raw multi-line PEM string
    data = {
        "business_public_key": public_key_str
    }

    print("\n📤 Sending key (with newlines preserved):\n", public_key_str)

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        print("✅ Public key registered successfully.")
        print(response.json())
    else:
        print("❌ Failed to register public key.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)

def get_business_public_key():
    print("🔍 Fetching registered business public key from Meta...")
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PHONE_NUMBER_ID}/whatsapp_business_encryption"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("✅ Retrieved successfully:")
        print("\n🔐 Public Key:")
        print(data.get("business_public_key", "Not found"))
        print("\n📜 Signature Status:")
        print(data.get("business_public_key_signature_status", "Unknown"))
    else:
        print("❌ Failed to retrieve business public key.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)


def load_and_validate_public_key():
    print("🔍 Validating RSA public key...")
    with open(PUBLIC_KEY_PATH, "rb") as f:
        key_data = f.read()

    public_key = serialization.load_pem_public_key(key_data, backend=default_backend())
    key_size = public_key.key_size
    if key_size != 2048:
        raise Exception(f"❌ Invalid RSA key size: {key_size}. Must be 2048 bits.")
    print("✅ RSA key is valid and 2048 bits.")
    return key_data.decode("utf-8")


# if __name__ == "__main__":
#     get_business_public_key()

# Run the full process
if __name__ == "__main__":
    try:
        check_access_token()
        public_key = load_and_validate_public_key()
        send_public_key(public_key)
        get_business_public_key()
    except Exception as e:
        print("💥 Error:", e)
