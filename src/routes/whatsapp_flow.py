#this route handles whatsapp flow

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from src.utils.config import config
from src.utils.encrypt import AESRSAEncryptor
import logging

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("src/logs/whatsapp.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
logger.propagate = False


whatsapp_flow_route = APIRouter(prefix="/whatsapp-flow")



# Load the private key (from .env or environment variable)
PRIVATE_KEY = config.RSA
PRIVATE_KEY_PASSWORD = config.PRIVATE_KEY_PASSWORD
if not PRIVATE_KEY and not PRIVATE_KEY_PASSWORD:
    raise ValueError("Missing PRIVATE_KEY environment variable")

def get_encryption_service():
    return AESRSAEncryptor(private_key_pem=PRIVATE_KEY, private_key_password=PRIVATE_KEY_PASSWORD)

@whatsapp_flow_route.post("/onboard-user")
async def data(request: Request, encrypt_service:AESRSAEncryptor = Depends(get_encryption_service)):
    try:
        body = await request.json()

        encrypted_flow_data_b64 = body['encrypted_flow_data']
        encrypted_aes_key_b64 = body['encrypted_aes_key']
        initial_vector_b64 = body['initial_vector']

        decrypted_data, aes_key, iv = encrypt_service.decrypt_request(
            encrypted_flow_data_b64,
            encrypted_aes_key_b64,
            initial_vector_b64
        )

        print("Decrypted payload:", decrypted_data)

        response = {
            "data": {
            "status": "active"
            }
        }

        # Encrypt response
        encrypted_response = encrypt_service.encrypt_response(response, aes_key, iv)

        # Return raw encrypted text (Base64 string) as plain text
        return PlainTextResponse(content=encrypted_response, media_type="text/plain")

    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")


# @whatsapp_flow_route.get("/health")
# async def health_check():
#     return {"status": "ok"}