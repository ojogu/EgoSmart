from twilio.rest import Client
from src.utils.config import config
import aiohttp
import asyncio
from typing import Dict
from src.utils.log import setup_logger  # noqa: E402
from datetime import datetime, timedelta


logger = setup_logger(__name__, file_path="whatsapp.log")
#Twilio 
# def send_whatsapp_message(to_number, from_number, message_body):
#     account_sid = config.Account_SID
#     auth_token = config.AUTH_TOKEN

#     try:
#         client = Client(account_sid, auth_token)
#         message = client.messages.create(
#             to=to_number,
#             from_=from_number,
#             body=message_body
#         )
#         logger.info(f"WhatsApp message sent to {to_number}. SID: {message.sid}")
#         return message
#     except Exception as e:
#         logger.exception(f"Failed to send WhatsApp message to {to_number}: {e}")
#         return None



# async def download_twilio_media(url, save_path='image.jpg'):
#     account_sid = config.Account_SID
#     auth_token = config.AUTH_TOKEN

#     try:
#         async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(account_sid, auth_token)) as session:
#             async with session.get(url) as response:
#                 if response.status == 200:
#                     content = await response.read()
#                     with open(save_path, 'wb') as f:
#                         f.write(content)
#                     logger.info(f"Image saved successfully to {save_path}.")
#                 else:
#                     logger.error(f"Failed to fetch image: {response.status}")
#     except Exception as e:
#         logger.exception(f"Exception occurred while downloading media: {e}")
        
        



class WhatsAppClient:
    def __init__(self, api_version: str = "v22.0"):
        self.token = self._load_stored_token() or config.ACCESS_TOKEN
        self.phone_number_id = config.PHONE_NUMBER_ID
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.token_expiry = self._load_token_expiry()  # store and load this from DB too
        logger.info(f"WhatsAppClient initialized with phone_number_id={self.phone_number_id}")

    async def _exchange_access_token(self) -> Dict:
        url = "https://graph.facebook.com/v19.0/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": config.APP_ID,
            "client_secret": config.APP_SECRET,
            "fb_exchange_token": self.token
        }
        logger.info("Attempting to exchange access token.")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    data = await resp.json()
                    logger.info(f"Access token exchange response: {data}")

                    if "access_token" in data:
                        new_token = data["access_token"]
                        self.token = new_token
                        self.headers["Authorization"] = f"Bearer {new_token}"
                        self.token_expiry = datetime.utcnow() + timedelta(days=55)
                        self._store_token(new_token, self.token_expiry)
                        return {"status": resp.status, "response": data}
                    else:
                        return {"status": resp.status, "response": data}
        except Exception as e:
            logger.exception(f"Exception during access token exchange: {e}")
            return {"status": "error", "response": str(e)}

    async def refresh_token_if_needed(self):
        if not self.token_expiry or datetime.utcnow() >= (self.token_expiry - timedelta(days=5)):
            logger.info("Access token is near expiry — refreshing...")
            await self._exchange_access_token()





    async def send_message(self, to: str, content: Dict, message_type: str = "text") -> Dict:
        """
        Send a regular WhatsApp message (text, image, document, audio, etc.)
        """
        await self.refresh_token_if_needed()
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": message_type,
            message_type: content
        }
        logger.info(f"Sending {message_type} message to {to} with content: {content}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=self.headers, json=payload) as resp:
                    data = await resp.json()
                    logger.info(f"{message_type.capitalize()} message response: {data}")
                    if resp.status == 401:
                        logger.warning("Received 401 Unauthorized. Attempting token refresh.")
                        new_token_resp = await self._exchange_access_token()
                        new_token = new_token_resp.get("response", {}).get("access_token")
                        if new_token:
                            self.token = new_token
                            new_header = {
                                "Authorization": f"Bearer {self.token}",
                                "Content-Type": "application/json"
                            }
                            logger.info("Retrying template message with refreshed token.")
                            async with session.post(self.base_url, headers=new_header, json=payload) as retry_resp:
                                data = await retry_resp.json()
                                logger.info(f"Retried template message response: {data}")
                                return {
                                    "status": retry_resp.status,
                                    "response": data
                                }
                        else:
                            logger.error("Failed to refresh token.")
                            return {
                                "status": resp.status,
                                "response": data
                            }
                    return {
                        "status": resp.status,
                        "response": data
                    }
        except Exception as e:
            logger.exception(f"Exception while sending {message_type} message: {e}")
            return {
                "status": "error",
                "response": str(e)
            }

    # 🔐 Helper methods for persistence
    def _store_token(self, token: str, expiry: datetime):
        # TODO: save to DB or file
        logger.info("Storing refreshed token securely")

    def _load_stored_token(self) -> str:
        # TODO: load from DB or file
        return None

    def _load_token_expiry(self) -> datetime:
        # TODO: load expiry from DB or file
        return None

# 🔧 Usage Example
# async def main():
#     TOKEN = "your_whatsapp_bearer_token"
#     PHONE_NUMBER_ID = "676753072188208"
#     TO_PHONE = "2349065011334"

#     client = WhatsAppClient(token=TOKEN, phone_number_id=PHONE_NUMBER_ID)
#     response = await client.send_template_message(to=TO_PHONE, template_name="hello_world")
#     print(response)

# if __name__ == "__main__":
#     asyncio.run(main())

# async def main():
#     TOKEN = "your_whatsapp_bearer_token"
#     PHONE_NUMBER_ID = "676753072188208"
#     TO_PHONE = "2349065011334"

#     client = WhatsAppClient(token=TOKEN, phone_number_id=PHONE_NUMBER_ID)

#     # Send plain text message
#     text_content = {"body": "Hey 👋 This is EgoSmart checking in!"}
#     response = await client.send_message(to=TO_PHONE, message_type="text", content=text_content)
#     print(response)
