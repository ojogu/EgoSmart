import aiohttp
from typing import Dict, Optional
from src.utils.config import config


from src.utils.log import setup_logger  # noqa: E402
logger = setup_logger(__name__, file_path="whatsapp_template.log")



class TemplateService:
    """
    service to create whatsapp template
    """
    
    BASE_URL = "https://graph.facebook.com/v19.0"

    def __init__(self,  base_url: Optional[str] = None):
        self.waba_id = config.BUSINESS_ACCOUNT_ID
        self.token = config.ACCESS_TOKEN
        self.template_url =  f"{self.BASE_URL}/{self.waba_id}/message_templates"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = f"{self.BASE_URL}/{self.waba_id}/messages"

    async def create_template(self,  payload:dict) -> Dict:
        logger.debug(f"Creating template with payload: {payload}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.template_url, headers=self.headers, json=payload) as response:
                    data = await response.json()
                    logger.info(f"Create template response: {data} (status: {response.status})")
                    return data
        except Exception as e:
            logger.exception(f"Exception while creating template: {e}")
            return {
                "status": "error",
                "response": str(e)
            }

    def _build_template_payload(
        self,
        name: str,
        language: str,
        category: str,
        body_text: str,
        header_text: Optional[str] = None,
        footer_text: Optional[str] = None,
        buttons: Optional[list] = None
    ) -> dict:
        components = []

        if header_text:
            components.append({
                "type": "HEADER",
                "format": "TEXT",
                "text": header_text
            })

        components.append({
            "type": "BODY",
            "text": body_text
        })

        if footer_text:
            components.append({
                "type": "FOOTER",
                "text": footer_text
            })

        if buttons:
            components.append({
                "type": "BUTTONS",
                "buttons": buttons
            })

        payload = {
            "name": name,
            "language": language,
            "category": category,
            "components": components
        }
        logger.debug(f"Built template payload: {payload}")
        return payload

    async def send_template_message(self, to: str, template_name: str, lang_code: str = "en_US") -> Dict:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": lang_code
                }
            }
        }
        logger.info(f"Sending template message to {to} with template '{template_name}' and language '{lang_code}'")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=self.headers, json=payload) as resp:
                    data = await resp.json()
                    logger.info(f"Template message response: {data} (status: {resp.status})")
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
                            async with session.post(self.base_url, headers=new_header, json=payload) as resp:
                                data = await resp.json()
                                logger.info(f"Retried template message response: {data} (status: {resp.status})")
                        else:
                            logger.error("Failed to refresh token.")
                    return {
                        "status": resp.status,
                        "response": data
                    }
        except Exception as e:
            logger.exception(f"Exception while sending template message: {e}")
            return {
                "status": "error",
                "response": str(e)
            }

    async def list_templates(self) -> dict:
        logger.info("Listing templates")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.template_url, headers=self.headers) as response:
                    data = await response.json()
                    logger.info(f"List templates response: {data} (status: {response.status})")
                    return data
        except Exception as e:
            logger.exception(f"Exception while listing templates: {e}")
            return {
                "status": "error",
                "response": str(e)
            }

    async def delete_template(self, template_name: str) -> dict:
        params = {"name": template_name}
        logger.info(f"Deleting template: {template_name}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(self.template_url, headers=self.headers, params=params) as response:
                    data = await response.json()
                    logger.info(f"Delete template response: {data} (status: {response.status})")
                    return data
        except Exception as e:
            logger.exception(f"Exception while deleting template: {e}")
            return {
                "status": "error",
                "response": str(e)
            }

    async def get_template_insights(self) -> dict:
        logger.info("Getting template insights")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.template_url, headers=self.headers) as response:
                    data = await response.json()
                    logger.info(f"Get template insights response: {data} (status: {response.status})")
                    return data
        except Exception as e:
            logger.exception(f"Exception while getting template insights: {e}")
            return {
                "status": "error",
                "response": str(e)
            }
            
template_service = TemplateService()