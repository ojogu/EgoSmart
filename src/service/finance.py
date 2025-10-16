import uuid
from sqlalchemy import select
from src.model.user import AccountLinking, Status
from src.utils.config import config
from src.schemas.finance import BvnVerification, BvnVerificationResponse, MonoWebhook, OtpVerification, OtpVerificationResponse, BvnDetails, AccountlinkingInitiate, AccountLinkingResponse, format_account_linking_payload
from src.service.user import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.http_client import http_client




from src.utils.log import setup_logger  # noqa: E402
logger = setup_logger(__name__, file_path="finance.log")

class MonoService():
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db=db)
        self.headers = {
            "mono-sec-key": config.MONO_TEST_SECRET_KEY,
        }
        
    @staticmethod
    def create_ref() -> str:
        """
        Generates a short unique reference string using UUID.
        Example output: 'a1b2c3d4e5f6'
        """
        return uuid.uuid4().hex[:12] 
            
    async def linking_account_initation(self, whatsapp_phone_number:str, **kwargs):
        """
        Initiates the Mono account linking process.
        
        :param payload: The payload for the initiation request (e.g., account details).
        """
        #fetch user
        user = await self.user_service.get_user_by_whatsapp_phone_number(whatsapp_phone_number)
        
        # Ensure 'meta' exists and is a dict
        meta_ref = kwargs.get("meta", {}).get("ref") if kwargs.get("meta") else None
        if not meta_ref:
            meta_ref = self.create_ref()
        
        #Reformat flat payload to match the Pydantic model
        formatted_payload = format_account_linking_payload(
            first_name=kwargs.get("first_name"),
            last_name=kwargs.get("last_name"),
            email=kwargs.get("email"),
            meta_ref=meta_ref
        )
        logger.info(f"formatted payload: {formatted_payload}")
        #validate 
        validated_payload = AccountlinkingInitiate(**formatted_payload).model_dump()
        logger.info(f"Initiating account linking with validated data: {validated_payload}")
        try:
            res = await http_client.make_request(
                http_method="post",
                endpoint="accounts/initiate", 
                data=validated_payload,
                headers=self.headers 
            )
        except Exception as e:
            logger.error(f"Error during Mono account linking initiation API call: {e}", exc_info=True)
            raise # Re-raise the exception after logging

        # 2. Process Response
        try:
            validated_data = AccountLinkingResponse(**res).model_dump()
            logger.info(f"Response data for account linking initiation: {validated_data}")
            
            #extracting key fields
            # top-level
            status = validated_data.get("status", "")
            
            # nested under "validated_data"
            nested_data = validated_data.get("data", {})
            mono_url = nested_data.get("mono_url", "")
            customer_id = nested_data.get("customer", "")
            created_at = nested_data.get("created_at", "")
            
            # nested under "data" -> "meta"
            meta = nested_data.get("meta", {})
            ref = meta.get("ref", "")
            
            #writing to the db
            account_link = AccountLinking(
                user_id = user,
                status=status,
                customer_id= customer_id,
                reference = ref,
                external_created_at = created_at
                
            )
            logger.info(f"save details for user {user.id} to the db:")
        except Exception as e:
            logger.error(f"Error processing Mono account linking initiation response: {e}", exc_info=True)
            raise # Re-raise the exception after logging

        
        return mono_url
            
            
    async def handle_mono_webhook(self, payload: "MonoWebhook"):
        event = payload.event
        data = payload.data

        logger.info(f"Received Mono webhook for event: {event}")
        # Determine reference (comes from meta.ref or can be inferred later)
        ref = None
        if data.meta and data.meta.ref:
            ref = data.meta.ref
            logger.info(f"Reference found in webhook meta: {ref}")
        else:
            # In case ref is not in webhook (like account_connected), find by customer_id
            logger.info(f"Reference not in meta, attempting to find by customer_id: {data.customer}")
            try:
                stmt = select(AccountLinking).where(AccountLinking.customer_id == data.customer)
                result = await self.db.execute(stmt)
                ref_record = result.scalars().first()
                
                if ref_record:
                    ref = ref_record.reference
                    logger.info(f"Reference found by customer_id: {ref}")
                else:
                    logger.warning(f"No account linking record found for customer_id {data.customer}")
            except Exception as e:
                logger.error(f"Error fetching account linking by customer_id {data.customer}: {e}", exc_info=True)
                return

        if not ref:
            logger.error("Reference not found after attempting to infer. Cannot process webhook.")
            return

        # Fetch existing account linking
        logger.info(f"Fetching existing account linking for reference: {ref}")
        try:
            stmt = select(AccountLinking).where(AccountLinking.reference == ref)
            result = await self.db.execute(stmt)
            account_link = result.scalars().first()
        except Exception as e:
            logger.error(f"Error fetching account linking for ref {ref}: {e}", exc_info=True)
            return

        if not account_link:
            logger.error(f"No account linking found for ref {ref}. This should not happen as initiation creates the record.")
            return

        # Update based on the event type
        logger.info(f"Updating account linking for ref {ref} with event: {event}")
        account_link.event = event

        # Account connected event
        if event == "mono.events.account_connected":
            logger.info(f"Handling account_connected event for ref {ref}")
            account_link.mono_id = data.id

        # Account updated event
        if event == "mono.events.account_updated" and data.account:
            logger.info(f"Handling account_updated event for ref {ref}")
            acc = data.account
            inst = acc.institution

            account_link.mono_id = acc._id or account_link.mono_id
            account_link.account_name = acc.name
            account_link.account_number = acc.accountNumber
            account_link.currency = acc.currency
            account_link.account_type = acc.type
            account_link.bvn = acc.bvn
            account_link.auth_method = acc.authMethod

            if inst:
                account_link.bank_name = inst.name
                account_link.bank_code = inst.bankCode

            account_link.meta = data.meta.model_dump() if data.meta else {}
            account_link.status = Status.SUCCESS
        
        try:
            self.db.add(account_link)
            await self.db.commit()
            await self.db.refresh(account_link)
            logger.info(f"Account linking record for ref {ref} updated successfully.")
        except Exception as e:
            logger.error(f"Error updating account linking record for ref {ref}: {e}", exc_info=True)
            await self.db.rollback() # Rollback in case of error
            return

        return account_link
   
   
   
    
    async def verify_bvn(self, bvn:str, whatsapp_phone_number:str):
        logger.info(f"Attempting to verify BVN for user with WhatsApp number: {whatsapp_phone_number}")
        try:
            user = await self.user_service.get_user_by_whatsapp_phone_number(whatsapp_phone_number) 
            if not user:
                logger.warning(f"User not found for WhatsApp number: {whatsapp_phone_number}")
                raise ValueError("User not found")
        except Exception as e:
            logger.error(f"Error fetching user by WhatsApp number {whatsapp_phone_number}: {e}", exc_info=True)
            raise

        verified_bvn = BvnVerification(bvn=bvn)
        # "this method verifies user bvn to get user details which we would store in the db, don't store BVN!!!"
        
        payload = {
            "bvn": verified_bvn.model_dump(),
            "scope": "identity" # or bank_accounts. since we want user data store in the db, so we can pass it to mono linking account api
        }

        logger.info(f"Initiating BVN lookup with payload: {payload}")
        try:
            res = await http_client.make_request(
                http_method="post",
                endpoint = "lookup/bvn/initiate",
                data = payload, 
                headers=self.headers
            )
        except Exception as e:
            logger.error(f"Error during Mono BVN initiation API call: {e}", exc_info=True)
            raise # Re-raise the exception after logging

        try:
            validated_data = BvnVerificationResponse(**res).model_dump()
            logger.info(f"Response data for BVN initiation: {validated_data}")
            mono_session_id = validated_data["data"]["session_id"]
        except Exception as e:
            logger.error(f"Error processing Mono BVN initiation response: {e}", exc_info=True)
            raise # Re-raise the exception after logging
  
        user.mono_session_id = mono_session_id
        logger.info(f"Saved session ID from Mono for user {user.whatsapp_phone_number}")
        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            logger.info(f"User {user.whatsapp_phone_number} updated with mono_session_id.")
        except Exception as e:
            logger.error(f"Error saving mono_session_id for user {user.whatsapp_phone_number}: {e}", exc_info=True)
            await self.db.rollback()
            raise

        return validated_data #store session id in db so we can use it for verification of otp, format methods and send to whatsapp to form the UI for the methods and hint. send json response back to verify

            

    async def verify_otp(self, method: str, whatsapp_phone_number: str, phone_number: str = None):
        """
        Initiates the OTP sending process for BVN verification via a specified method.
        It fetches the session ID from the user stored in the database.
        
        :param method: The verification method ('alternate_phone', 'fingerprint', 'face', etc.).
        :param whatsapp_phone_number: The user's WhatsApp number to fetch the mono_session_id.
        :param phone_number: The alternate phone number, if 'alternate_phone' method is used.
        """
        logger.info(f"Attempting to verify OTP for user {whatsapp_phone_number} using method: {method}")
        # 1. Fetch User and Session ID
        try:
            user = await self.user_service.get_user_by_whatsapp_phone_number(whatsapp_phone_number)
            if not user:
                logger.warning(f"User not found for WhatsApp number: {whatsapp_phone_number}")
                raise ValueError("User not found")
            if not user.mono_session_id:
                logger.error(f"Mono session ID not found for user {whatsapp_phone_number}. BVN initiation step is required.")
                raise ValueError("Mono session ID not found for user. BVN initiation step is required.")
        except Exception as e:
            logger.error(f"Error fetching user or session ID for {whatsapp_phone_number}: {e}", exc_info=True)
            raise

        # 2. Build Payload
        payload_data = {}
        if method == "alternate_phone":
            if not phone_number:
                logger.error("Phone number is required for 'alternate_phone' method but was not provided.")
                raise ValueError("Phone number is required for 'alternate_phone' method")
            payload_data = {
                "method": method,
                "phone_number": phone_number
            }
        else:
            payload_data = {
                "method": method
            }
        
        # Validate payload data using the Pydantic model
        try:
            verified_payload = OtpVerification(**payload_data).model_dump()
            logger.info(f"OTP verification payload: {verified_payload}")
        except Exception as e:
            logger.error(f"Error validating OTP verification payload: {e}", exc_info=True)
            raise

        # 3. Prepare Request Headers
        request_headers = self.headers.copy()
        request_headers["x-session-id"] = user.mono_session_id
        logger.debug(f"Request headers for OTP verification: {request_headers}")

        # 4. Make Request using http_client
        try:
            res, header = await http_client.make_request(
                http_method="post",
                endpoint="lookup/bvn/verify",
                data=verified_payload,
                headers=request_headers
            )
        except Exception as e:
            logger.error(f"Error during Mono OTP verification API call for user {whatsapp_phone_number}: {e}", exc_info=True)
            raise # Re-raise the exception after logging
        
        # 5. Process Response
        try:
            validated_data = OtpVerificationResponse(**res).model_dump()
            logger.info(f"Response data for OTP initiation: {validated_data}")
        except Exception as e:
            logger.error(f"Error processing Mono OTP verification response for user {whatsapp_phone_number}: {e}", exc_info=True)
            raise # Re-raise the exception after logging
        
        return validated_data
                
            

    async def details(self, otp: str, whatsapp_phone_number: str):
        """
        Validates the OTP and fetches the user's BVN details, excluding sensitive data.
        
        :param otp: The one-time password provided by the user.
        :param whatsapp_phone_number: The user's WhatsApp number to fetch the mono_session_id.
        """
        logger.info(f"Attempting to fetch BVN details for user {whatsapp_phone_number} with OTP.")
        # 1. Fetch User and Session ID
        try:
            user = await self.user_service.get_user_by_whatsapp_phone_number(whatsapp_phone_number)
            if not user:
                logger.warning(f"User not found for WhatsApp number: {whatsapp_phone_number}")
                raise ValueError("User not found")
            if not user.mono_session_id:
                logger.error(f"Mono session ID not found for user {whatsapp_phone_number}. BVN initiation step is required.")
                raise ValueError("Mono session ID not found for user. BVN initiation step is required.")
        except Exception as e:
            logger.error(f"Error fetching user or session ID for {whatsapp_phone_number}: {e}", exc_info=True)
            raise

        # 2. Build Payload
        payload_data = {
            "otp": otp
        }
        logger.debug(f"BVN details payload: {payload_data}")

        # 3. Prepare Request Headers
        request_headers = self.headers.copy()
        request_headers["x-session-id"] = user.mono_session_id
        logger.debug(f"Request headers for BVN details: {request_headers}")

        # 4. Make Request using http_client
        try:
            res, header = await http_client.make_request(
                http_method="post",
                endpoint="lookup/bvn/details", 
                data=payload_data,
                headers=request_headers
            )
        except Exception as e:
            logger.error(f"Error during Mono BVN details API call for user {whatsapp_phone_number}: {e}", exc_info=True)
            raise # Re-raise the exception after logging
        
        # 5. Process and Store Response Data
        try:
            validated_data = BvnDetails(**res).model_dump(exclude={"bvn", "nin"})
            logger.info(f"Successfully fetched and validated BVN details for user {user.whatsapp_phone_number}")
        except Exception as e:
            logger.error(f"Error processing Mono BVN details response for user {whatsapp_phone_number}: {e}", exc_info=True)
            raise # Re-raise the exception after logging

        # You can now update the user object with the details here, e.g.:
        # user.first_name = validated_data.get("first_name")
        # user.date_of_birth = validated_data.get("date_of_birth")
        # await self.db.add(user)
        # await self.db.commit()

        return validated_data
            

    
    
    
    
    
    
    
    
    
    
    
    
    
    
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
