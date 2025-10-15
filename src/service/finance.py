import uuid
import httpx
from src.utils.config import config
from src.utils.redis import get_redis
from src.schemas.finance import BvnVerification, BvnVerificationResponse, OtpVerification, OtpVerificationResponse, BvnDetails, AccountlinkingInitiate, AccountLinkingResponse
from src.service.user import UserService
from src.utils.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
import json
from src.utils.http_client import http_client




from src.utils.log import setup_logger  # noqa: E402
logger = setup_logger(__name__, file_path="finance.log")

class MonoService():
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db=db)
        self.headers = {
            "mono-sec-key": config.MONO_LIVE_SECRET_KEY,
        }
        
    
    async def verify_bvn(self, bvn:str, whatsapp_phone_number:str):
        user = await self.user_service.get_user_by_whatsapp_phone_number(whatsapp_phone_number) 
        if not user:
            raise ValueError("User not found")
        verified_bvn = BvnVerification(bvn=bvn)
        "this method verifies user bvn to get user details which we would store in the db, don't store BVN!!!"
        
        payload = {
            "bvn": verified_bvn.model_dump(),
            "scope": "identity" # or bank_accounts. since we want user data store in the db, so we can pass it to mono linking account api
        }

        
        res, header = await http_client.make_request(
            http_method="post",
            endpoint = "lookup/bvn/initiate",
            data = payload, 
            headers=self.headers
        )
        validated_data = BvnVerificationResponse(**res).model_dump()
        logger.info(f"Response data: {validated_data}")
        mono_session_id = validated_data["data"]["session_id"]
  
        user.mono_session_id = mono_session_id
        logger.info(f"saved session id from mono for user {user.whatsapp_phone_number}")
        await self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return validated_data #store session id in db so we can use it for verification of otp, format methods and send to whatsapp to form the UI for the methods and hint. send json response back to verify

            

    async def verify_otp(self, method: str, whatsapp_phone_number: str, phone_number: str = None):
        """
        Initiates the OTP sending process for BVN verification via a specified method.
        It fetches the session ID from the user stored in the database.
        
        :param method: The verification method ('alternate_phone', 'fingerprint', 'face', etc.).
        :param whatsapp_phone_number: The user's WhatsApp number to fetch the mono_session_id.
        :param phone_number: The alternate phone number, if 'alternate_phone' method is used.
        """
        
        # 1. Fetch User and Session ID
        user = await self.user_service.get_user_by_whatsapp_phone_number(whatsapp_phone_number)
        if not user:
            raise ValueError("User not found")
        if not user.mono_session_id:
            raise ValueError("Mono session ID not found for user. BVN initiation step is required.")

        # 2. Build Payload
        if method == "alternate_phone":
            if not phone_number:
                raise ValueError("Phone number is required for 'alternate_phone' method")
            payload_data = {
                "method": method,
                "phone_number": phone_number
            }
        else:
            # Assuming other methods only require the 'method' field in the payload
            payload_data = {
                "method": method
            }
        
        # Validate payload data using the Pydantic model
        verified_payload = OtpVerification(**payload_data).model_dump()

        # 3. Prepare Request Headers
        # Use existing self.headers and add the required x-session-id
        request_headers = self.headers.copy()
        request_headers["x-session-id"] = user.mono_session_id

        # 4. Make Request using http_client
        # Note: I'm assuming 'http_client' is a utility that handles the base URL and error checking
        res, header = await http_client.make_request(
            http_method="post",
            endpoint="lookup/bvn/verify", # Assuming the endpoint is relative to the client's base URL
            data=verified_payload,
            headers=request_headers
        )
        
        # 5. Process Response
        validated_data = OtpVerificationResponse(**res).model_dump()
        logger.info(f"Response data for OTP initiation: {validated_data}")
        
        # The response should indicate that the OTP has been successfully sent.
        return validated_data
                
            

    async def details(self, otp: str, whatsapp_phone_number: str):
        """
        Validates the OTP and fetches the user's BVN details, excluding sensitive data.
        
        :param otp: The one-time password provided by the user.
        :param whatsapp_phone_number: The user's WhatsApp number to fetch the mono_session_id.
        """
        
        # 1. Fetch User and Session ID
        user = await self.user_service.get_user_by_whatsapp_phone_number(whatsapp_phone_number)
        if not user:
            raise ValueError("User not found")
        if not user.mono_session_id:
            raise ValueError("Mono session ID not found for user. BVN initiation step is required.")

        # 2. Build Payload
        payload_data = {
            "otp": otp
        }
        # Assuming BvnOtp is the Pydantic model for the request payload
        # validated_payload = OtpVerification(**payload_data).model_dump()

        # 3. Prepare Request Headers
        request_headers = self.headers.copy()
        request_headers["x-session-id"] = user.mono_session_id

        # 4. Make Request using http_client
        res, header = await http_client.make_request(
            http_method="post",
            endpoint="lookup/bvn/details", 
            data=payload_data,
            headers=request_headers
        )
        
        # 5. Process and Store Response Data
        # BvnDetails is the Pydantic model for the response structure
        # We exclude BVN and NIN from the final validated data before processing/storage
        validated_data = BvnDetails(**res).model_dump(exclude={"bvn", "nin"})
        
        logger.info(f"Successfully fetched and validated BVN details for user {user.whatsapp_phone_number}")

        # You can now update the user object with the details here, e.g.:
        # user.first_name = validated_data.get("first_name")
        # user.date_of_birth = validated_data.get("date_of_birth")
        # await self.db.add(user)
        # await self.db.commit()

        return validated_data
            

    @staticmethod
    def create_ref() -> str:
        """
        Generates a short unique reference string using UUID.
        Example output: 'a1b2c3d4e5f6'
        """
        return uuid.uuid4().hex[:12] 
            
    async def linking_account_initation(self,  **kwargs):
        """
        Initiates the Mono account linking process.
        
        :param payload: The payload for the initiation request (e.g., account details).
        """

    # Ensure 'meta' exists and is a dict
        if kwargs.get("meta") is None:
            kwargs["meta"] = {}

        if "ref" not in kwargs["meta"]:
            kwargs["meta"]["ref"] = self.create_ref()
            
        validated_payload = AccountlinkingInitiate(**kwargs).model_dump()
        logger.info(f"validated data: {validated_payload}")
        res = await http_client.make_request(
            http_method="post",
            endpoint="accounts/initiate", 
            data=validated_payload,
            headers=self.headers 
        )
        
        # 2. Process Response
        validated_data = AccountLinkingResponse(**res).model_dump()
        
        logger.info(f"Response data for account linking initiation: {validated_data}")
        
        # Typically, you would save the session ID or reference returned by this call
        
        return validated_data
            
            
    async def handle_webhook(self):
        pass 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#     async def bank_details(self, force_refresh: bool = False) -> dict:
#         logger.info("Fetching bank details...")
#         CACHE_KEY = "mono:institutions"
#         CACHE_TTL = 60 * 60 * 24 * 7  # 7 days
#         url = "https://api.withmono.com/v3/institutions"
#         if not force_refresh:
#             redis = await get_redis()  
#             cached = await redis.get(CACHE_KEY) 
#             # cached = await get_redis().get(CACHE_KEY)
#             if cached:
#                 logger.info("Returning cached bank details.")
#                 logger.info(f"Successfully fetched {len(cached)} institutions from cache.")
#                 cleaned_data = json.loads(cached)
#                 options, bank_map = await self._prepare_bank_options(cleaned_data)
#                 message = "Select your bank:\n" + "\n".join(options)
#                 logger.info(message)
#                 return cleaned_data
            


#         logger.info("Fetching bank details from Mono API.")
#         params={"country": "ng"}
#         try:
#             async with httpx.AsyncClient() as client:
#                 response = await client.get(url, headers=self.headers, params=params)
#                 response.raise_for_status() 

#             if response.status_code == 200:
#                 data = response.json().get("data", [])
#                 logger.info(f"Successfully fetched {len(data)} institutions from Mono API.")

#                 # Build institution mapping
#                 processed = {}
#                 for inst in data:
#                     name = inst["institution"]
#                     auth = inst.get("auth_methods", [{}])[0]  # safe fallback
#                     processed[name] = {
#                         "id": inst["id"],
#                         "auth_method_id": auth.get("id"),
#                         "auth_identifier": auth.get("identifier"),
#                     }
                
#                 await redis.set(CACHE_KEY, json.dumps(processed), ex=CACHE_TTL)
#                 logger.info("Bank details cached successfully.")
#                 return processed
#         except httpx.HTTPStatusError as e:
#             logger.error(f"Mono API Error: {e.response.status_code} - {e.response.text}", exc_info=True)
#             raise Exception(f"Mono API Error: {e.response.status_code} - {e.response.text}")
#         except Exception as e:
#             logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#             raise

#     async def _prepare_bank_options(self, api_response: dict) -> tuple[list[str], dict]:
#         bank_map = {}  # map index and name to actual bank key
#         options = []

#         for idx, bank_name in enumerate(api_response.keys(), start=1):
#             clean_name = bank_name.lower().replace(" ", "")
#             options.append(f"{idx}. {clean_name}")
#             bank_map[str(idx)] = bank_name
#             bank_map[clean_name] = bank_name  # allow lookup by name too

#         return options, bank_map
    
#     async def _resolve_bank_choice(self, client_input: str, bank_map: dict, api_response: dict) -> dict | None:
#         cleaned_input = client_input.strip().lower().replace(" ", "")
#         bank_name = bank_map.get(cleaned_input)

#         if bank_name:
#             return api_response[bank_name]
#         return None  # invalid input



# #TO:DO: modify db mo
