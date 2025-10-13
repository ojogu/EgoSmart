from typing import Optional
import aiohttp
import asyncio

import logging
from src.utils.config import config

from src.utils.log import setup_logger  # noqa: E402
logger = setup_logger(__name__, file_path="flow.log")

class MetaFlowManager:
    BASE_URL = "https://graph.facebook.com/v19.0"
    def __init__(self,  base_url: Optional[str] = None):
        self.waba_id = config.BUSINESS_ACCOUNT_ID
        self.token = config.ACCESS_TOKEN
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
