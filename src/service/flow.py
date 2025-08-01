from typing import Optional
import aiohttp
import asyncio

import logging
from src.utils.config import config

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("src/logs/template.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)
logger.propagate = False


class MetaFlowManager:
    BASE_URL = "https://graph.facebook.com/v19.0"
    def __init__(self,  base_url: Optional[str] = None):
        self.waba_id = config.BUSINESS_ACCOUNT_ID
        self.token = config.WHATSAPP_KEY
        # self.template_url =  f"{self.BASE_URL}/{self.waba_id}/message_templates"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    async def create_flow(self, flow_data: dict) -> dict:
        url = f"{self.BASE_URL}/{self.app_id}/flows"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=flow_data) as resp:
                return await resp.json()

    async def list_flows(self) -> dict:
        url = f"{self.BASE_URL}/{self.app_id}/flows"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                return await resp.json()

    async def get_flow(self, flow_id: str) -> dict:
        url = f"{self.BASE_URL}/{flow_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                return await resp.json()

    async def update_flow(self, flow_id: str, update_data: dict) -> dict:
        url = f"{self.BASE_URL}/{flow_id}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=update_data) as resp:
                return await resp.json()

    async def publish_flow(self, flow_id: str) -> dict:
        url = f"{self.BASE_URL}/{flow_id}/publish"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers) as resp:
                return await resp.json()

    async def delete_flow(self, flow_id: str) -> dict:
        url = f"{self.BASE_URL}/{flow_id}"
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=self.headers) as resp:
                return await resp.json()
