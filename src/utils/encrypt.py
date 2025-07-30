import json
from base64 import b64decode, b64encode
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1
from cryptography.hazmat.primitives import hashes

class AESRSAEncryptor:
    def __init__(self, private_key_pem, private_key_password=None):
        self.private_key = load_pem_private_key(
            private_key_pem.encode("utf-8"),
            password=private_key_password.encode() if private_key_password else None
        )

    def decrypt_request(self, encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64):
        flow_data = b64decode(encrypted_flow_data_b64)
        iv = b64decode(initial_vector_b64)
        encrypted_aes_key = b64decode(encrypted_aes_key_b64)

        aes_key = self.private_key.decrypt(
            encrypted_aes_key,
            OAEP(
                mgf=MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        encrypted_flow_data_body = flow_data[:-16]
        encrypted_flow_data_tag = flow_data[-16:]

        decryptor = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(iv, encrypted_flow_data_tag)
        ).decryptor()

        decrypted_data_bytes = decryptor.update(encrypted_flow_data_body) + decryptor.finalize()
        decrypted_data = json.loads(decrypted_data_bytes.decode("utf-8"))
        return decrypted_data, aes_key, iv

    def encrypt_response(self, response, aes_key, iv):
        # Flip the IV
        flipped_iv = bytearray(byte ^ 0xFF for byte in iv)

        encryptor = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(flipped_iv)
        ).encryptor()

        encrypted_data = encryptor.update(json.dumps(response).encode("utf-8")) + encryptor.finalize()

        # Return the base64-encoded result with tag
        return b64encode(encrypted_data + encryptor.tag).decode("utf-8")
