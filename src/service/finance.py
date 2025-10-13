import aiohttp
import httpx
from src.utils.config import config
from src.utils.redis import get_redis
from src.schemas.finance import BvnVerification, BvnVerificationResponse, OtpVerification, OtpVerificationResponse, BvnDetails, Account_linking_Initiate
from src.service.user import UserService
from src.utils.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
import json
from src.utils.http_client import http_client




from src.utils.log import setup_logger  # noqa: E402
logger = setup_logger(__name__, file_path="finance.log")

# def get_user_service(db: AsyncSession = get_session()):
#     return UserService(db=db)

#TODO: add error handling
#we will use the user whatsapp number as unique id 
class MonoService():
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db=db)
        self.headers = {
            "mono-sec-key": config.MONO_SECRET_KEY,
        }
        
    
    async def verify_bvn(self, bvn:str, whatsapp_phone_number:str):
        self.session = await http_client.get_session()
        user = await self.user_service.get_user_by_whatsapp_phone_number(whatsapp_phone_number) 
        if not user:
            raise ValueError("User not found")
        verified_bvn = BvnVerification(bvn=bvn)
        "this method verifies user bvn to get user details which we would store in the db, don't store BVN!!!"
        payload = {
            "bvn": verified_bvn.model_dump(),
            "scope": "identity" # or bank_accounts. since we want user data store in the db, so we can pass it to mono linking account api
        }
        url = "https://api.withmono.com/v2/lookup/bvn/initiate"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            logger.info(f"Response status code: {response.status_code}")
            if response.status_code == 200:
                response_data = response.json()
                validated_data = BvnVerificationResponse(**response_data).model_dump()
                logger.info(f"Response data: {validated_data}")
                mono_session_id = validated_data["data"]["session_id"]
  
                user.mono_session_id = mono_session_id
                logger.info(f"saved session id from mono for user {user.whatsapp_phone_number}")
                await self.db.add(user)
                await self.db.commit()
                await self.db.refresh(user)
                return validated_data #store session id in db so we can use it for verification of otp, format methods and send to whatsapp to form the UI for the methods and hint. send json response back to verify
            else:
                logger.error(f"Error: {response.status_code} - {response.text}")
                raise 
            
    
    async def verify_otp(self, method:str, phone_number=None):
        url = "https://api.withmono.com/v2/lookup/bvn/verify"
        headers = { #update self.headers
            "mono-sec-key": config.MONO_SECRET_KEY,
            "x-session-id": "SESSION_ID_FROM_STEP_1" #fetch from db
        } 
        if method == "alternate_phone":
            phone_number=phone_number
            payload = {
                "method": method,
                "phone_number": phone_number
            }
            verified_payload = OtpVerification(**payload).model_dump()
        else:
            payload = {
                method: method
            }
            verified_payload = OtpVerification(**payload).model_dump()   
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=verified_payload, headers=headers)
            logger.info(f"Response status code: {response.status_code}")
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"Response data: {response_data}")
                validated_data = OtpVerificationResponse(**response_data).model_dump()
                return validated_data  #form UI telling user otp has been sent 
            else:
                logger.error(f"Error: {response.status_code} - {response.text}")
                raise
        
    async def details(self, otp):
        #users send otp to verify
        url = "https://api.withmono.com/v2/lookup/bvn/details" 
        headers = { #update self.headers 
            "mono-sec-key": config.MONO_SECRET_KEY,
            "x-session-id": "SESSION_ID_FROM_STEP_1" #fetch from db
        } 
        payload = {
            "otp": otp
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            logger.info(f"Response status code: {response.status_code}")
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"Response data: {response_data}")
                #save user details to the db
                validated_data = BvnDetails(**response_data).model_dump(exclude={"bvn", "nin"})
                return validated_data
            else:
                logger.error(f"Error: {response.status_code} - {response.text}")
                raise

            
    async def linking_account_initation(self, **payload):
        url = "https://api.withmono.com/v2/accounts/initiate"
        
        async with self.session as session:
            async with session.post(url, json=payload, headers=self.headers) as response:
                logger.info(f"Response status code: {response.status}")
                response_json = await response.json()
                logger.info(f"Response JSON: {response_json}")
            
            

    async def bank_details(self, force_refresh: bool = False) -> dict:
        logger.info("Fetching bank details...")
        CACHE_KEY = "mono:institutions"
        CACHE_TTL = 60 * 60 * 24 * 7  # 7 days
        url = "https://api.withmono.com/v3/institutions"
        if not force_refresh:
            redis = await get_redis()  
            cached = await redis.get(CACHE_KEY) 
            # cached = await get_redis().get(CACHE_KEY)
            if cached:
                logger.info("Returning cached bank details.")
                logger.info(f"Successfully fetched {len(cached)} institutions from cache.")
                cleaned_data = json.loads(cached)
                options, bank_map = await self._prepare_bank_options(cleaned_data)
                message = "Select your bank:\n" + "\n".join(options)
                logger.info(message)
                return cleaned_data
            


        logger.info("Fetching bank details from Mono API.")
        params={"country": "ng"}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status() 

            if response.status_code == 200:
                data = response.json().get("data", [])
                logger.info(f"Successfully fetched {len(data)} institutions from Mono API.")

                # Build institution mapping
                processed = {}
                for inst in data:
                    name = inst["institution"]
                    auth = inst.get("auth_methods", [{}])[0]  # safe fallback
                    processed[name] = {
                        "id": inst["id"],
                        "auth_method_id": auth.get("id"),
                        "auth_identifier": auth.get("identifier"),
                    }
                
                await redis.set(CACHE_KEY, json.dumps(processed), ex=CACHE_TTL)
                logger.info("Bank details cached successfully.")
                return processed
        except httpx.HTTPStatusError as e:
            logger.error(f"Mono API Error: {e.response.status_code} - {e.response.text}", exc_info=True)
            raise Exception(f"Mono API Error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            raise

    async def _prepare_bank_options(self, api_response: dict) -> tuple[list[str], dict]:
        bank_map = {}  # map index and name to actual bank key
        options = []

        for idx, bank_name in enumerate(api_response.keys(), start=1):
            clean_name = bank_name.lower().replace(" ", "")
            options.append(f"{idx}. {clean_name}")
            bank_map[str(idx)] = bank_name
            bank_map[clean_name] = bank_name  # allow lookup by name too

        return options, bank_map
    
    async def _resolve_bank_choice(self, client_input: str, bank_map: dict, api_response: dict) -> dict | None:
        cleaned_input = client_input.strip().lower().replace(" ", "")
        bank_name = bank_map.get(cleaned_input)

        if bank_name:
            return api_response[bank_name]
        return None  # invalid input



#TO:DO: modify db mo
