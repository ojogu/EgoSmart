import aiohttp
from src.utils.log import setup_logger  # noqa: E402
from src.utils.config import config
from typing import Dict, Any
from src.utils.exception import format_error
logger = setup_logger(__name__, file_path="finance.log")

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

http_client = HttpConfig()


class Client:

    def __init__(self):
        self.base_url = config.BASE_URL
        logger.debug(f"Base URL configured as: {self.base_url}")

    async def _make_request(
        self,
        http_method: str,
        endpoint: str,
        params: Dict = None,
        data: Dict = None,
        token: str = None
    ) -> Dict[str, Any]:
        """Make HTTP request with JSON content type"""

        self.session = await http_client.get_session()
        url = f"{self.base_url}{endpoint}"
        http_method = http_method.upper()

        # Setup headers with JSON content type
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

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
                return await self._handle_response(response, response.headers)

        except aiohttp.ClientResponseError as e:
            logger.error(
                f"API request failed: Status={e.status}, Message={e.message}, "
                f"URL={e.request_info.real_url}",
                exc_info=True
            )
            return format_error(
                source=__name__,
                error=str(e)
            )

        except Exception as e:
            logger.error(f"Unexpected error during API request: {str(e)}", exc_info=True)
            return format_error(
                source=__name__,
                error=str(e)
            )
