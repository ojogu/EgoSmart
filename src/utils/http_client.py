import json
import aiohttp
from src.utils.log import setup_logger  # noqa: E402
from src.utils.config import config
from typing import Dict, Any
from src.utils.exception import format_error

logger = setup_logger(__name__, file_path="client.log")

class HttpConfig:
    _instance = None
    _session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def get_session(self, headers:dict=None):
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30)

            #Adjusting the TCP Connector may yield different performance levels in production
            connector = aiohttp.TCPConnector(limit=60, limit_per_host=40)


            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout,
                connector=connector
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None  # reset so it can be recreated

http_config = HttpConfig()


class Client:

    def __init__(self):
        self.base_url = config.BASE_URL
        logger.debug(f"Base URL configured as: {self.base_url}")

    async def make_request(
        self,
        http_method: str,
        endpoint: str,
        params: Dict = None,
        data: Dict = None,
        headers: Dict = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with JSON content type"""

        self.session = await http_config.get_session()
        url = f"{self.base_url}{endpoint}"
        http_method = http_method.upper()



        # Setup request arguments
        request_kwargs = {
            "method": http_method,
            "url": url,
            "headers": headers,
            "params": params,
        }

        # Add JSON data for POST, PUT, PATCH requests
        if http_method in ("POST", "PUT", "PATCH") and data:
            request_kwargs["json"] = data

        logger.info(f"Making {http_method} request to: {url}")
        logger.debug(f"Request headers: {headers}")
        logger.debug(f"Request params: {params}")

        try:
            async with self.session.request(**request_kwargs) as response:
                return await self._handle_response(response)

        except Exception as e:
            logger.error(f"Unexpected error during API request: {str(e)}", exc_info=True)
            # return structured error
            return format_error(
            source=__name__,
            error=str(e),
            status_code=500,
            url=url,
            ) 
        # ========== Helper Method =============
    async def _handle_response(self, response: aiohttp.ClientResponse):
        """
        Handle the response, raising clean errors when status is not OK.
        """
        try:
            response.raise_for_status()
            try:
                response_json = await response.json()
                logger.debug(f"Response JSON: {response_json}")
                return response_json
            except aiohttp.ContentTypeError:
                response_text = await response.text()
                logger.warning(f"Non-JSON response received: {response_text}")
                return response_text

        except aiohttp.ClientResponseError as e:
            # Try to extract error body
            error_details = None
            try:
                raw_body = await response.text()
                try:
                    error_details = json.loads(raw_body)
                except json.JSONDecodeError:
                    error_details = raw_body
            except Exception:
                error_details = None

            # Log everything clearly
            logger.error(
                f"Request failed — Status: {e.status}, Message: {e.message or 'Unknown'}, "
                f"URL: {e.request_info.real_url}, Body: {error_details}",
                exc_info=True
            )

            # return structured error
            return format_error(
                source=__name__,
                error=e.message,
                status_code=e.status,
                url=str(e.request_info.real_url),
                details=error_details
            )



http_client = Client()