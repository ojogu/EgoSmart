from twilio.rest import Client
from src.utils.config import config
import logging
import aiohttp
import asyncio

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("src/logs/whatsapp.log")
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
logger.propagate = False


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
        
        


from typing import Dict

class WhatsAppClient:
    def __init__(self, api_version: str = "v22.0"):
        self.token = config.WHATSAPP_KEY
        self.phone_number_id = config.PHONE_NUMBER_ID
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        logger.info(f"WhatsAppClient initialized with phone_number_id={self.phone_number_id} and api_version={self.api_version}")

    async def _exchange_access_token(self) -> Dict:
        """
        Exchange a short-lived access token for a long-lived token.
        """
        url = "https://graph.facebook.com/v19.0/oauth/access_token"
        app_id = config.APP_ID
        app_secret = config.APP_SECRET
        short_lived_token = self.token  # Use current token

        params = {
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": short_lived_token
        }
        logger.info("Attempting to exchange access token.")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    data: dict = await resp.json()
                    logger.info(f"Access token exchange response: {data}")

                    new_token = data.get("access_token")
                    if new_token:
                        self.token = new_token
                        self.headers["Authorization"] = f"Bearer {self.token}"
                        # Optionally: store this token somewhere

                    return {
                        "status": resp.status,
                        "response": data
                    }
        except Exception as e:
            logger.exception(f"Exception during access token exchange: {e}")
            return {
                "status": "error",
                "response": str(e)
            }



    async def send_message(self, to: str, content: Dict, message_type: str = "text") -> Dict:
        """
        Send a regular WhatsApp message (text, image, document, audio, etc.)
        """
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
