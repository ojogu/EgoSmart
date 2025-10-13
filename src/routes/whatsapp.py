
from fastapi import APIRouter, HTTPException, Query, Request, Response, status, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from src.service.whatsapp import WhatsAppClient
from src.utils.config import config 
from src.agents.agent import process_query_service
from src.service.user import UserService
from src.utils.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.redis import get_redis

from src.utils.log import setup_logger  # noqa: E402
logger = setup_logger(__name__, file_path="whatsapp.log")



whatsapp_route = APIRouter(prefix="/whatsapp")

def get_user_service(db: AsyncSession = Depends(get_session)):
    return UserService(db=db)

def get_whatsapp_service():
    return WhatsAppClient()

@whatsapp_route.get("/incoming")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    if hub_mode == "subscribe" and hub_verify_token == config.VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge, status_code=200)
    raise HTTPException(status_code=403, detail="Verification failed")


@whatsapp_route.post("/incoming", status_code=status.HTTP_200_OK)
async def incoming_message(
    request: Request,
    whatsapp_service: WhatsAppClient = Depends(get_whatsapp_service),
    user_service: UserService = Depends(get_user_service)
):
    # Headers
    # headers = dict(request.headers)

    # Query Parameters
    # query_params = dict(request.query_params)

    # Raw Body
    # body_bytes = await request.body()
    # body_str = body_bytes.decode("utf-8")  # Optional: decode from bytes
    client = await get_redis()
    # JSON Body (optional, if known to be JSON)
    try:
        json_body:dict = await request.json()
    except Exception:
        json_body = None  # fallback if not JSON

    # Form data (optional)
    try:
        form_data = await request.form()
        form_dict = dict(form_data)
    except Exception:
        form_dict = None


    logger.info(
        {
            "json_body": json_body,
            "form_data": form_dict,
        }
    )
    # data = json_body
    try:
        entry = json_body.get("entry", [])[0]
        change_value = entry.get("changes", [])[0].get("value", {})

        contacts = change_value.get("contacts", [])
        messages = change_value.get("messages", [])

        if not (contacts and messages):
            logger.warning("No contacts or messages found in webhook payload.")
            return JSONResponse(status_code=200, content={"status": "ignored"})

        contact = contacts[0]
        message = messages[0]

        user_wa_id = contact.get("wa_id")
        user_name = contact.get("profile", {}).get("name")
        message_id = message.get("id")
        timestamp = message.get("timestamp")
        message_body = message.get("text", {}).get("body", "")
        phone_number_id = change_value.get("metadata", {}).get("phone_number_id")

    except (IndexError, AttributeError, KeyError, TypeError) as e:
        logger.error(f"Error parsing webhook payload: {e}")
        return JSONResponse(status_code=400, content={"error": "Malformed webhook payload"})
    
    # Deduplication: check if message_id was already processed
    
    if await client.get(message_id):
        logger.warning(f"{message_id} duplicate - already processed")
        return JSONResponse(content={"status": "duplicate - already processed"}, status_code=200)
    
    # Mark message as processed (expires after 1 hour)
    await client.setex(message_id, 3600, "seen")
    # agent_msg = {
    #         "phone" :user_wa_id,
    #         "name": user_name,
    #         "Message": message_body
    #     }
    agent = await process_query_service.process_query(
            phone_number = user_wa_id, 
            query=message_body,
            username=user_name
        )
        

    text_content = {"body": agent}
    response = await whatsapp_service.send_message(
        to = user_wa_id,
        content = text_content
    )
    logger.info(f"response: {response}")
    logger.warning("Non-user message event received. Ignoring.")
    return JSONResponse(content={"status": "processed"}, status_code=200)

    
    
        # Process the user message
        # your logic here...
        # Extract the country dial code (first 3 digits)
        # country_dial_code = user_wa_id[:3]
        # get_country_details = get_country_by_dial_code(country_dial_code)
        # final_data = {
        #     **get_country_details, "whatsapp_phone_number": user_wa_id,
        #     "whatsapp_profile_name":user_name
        # }
        # agent_msg = {
        #     "phone" :user_wa_id,
        #     "name": user_name,
        #     "Message": message_body
        # }
        # logger.info(f"user_details: {final_data}")
        
        # user_state = await user_service.get_registration_state(user_wa_id)

        # if user_state is None:
        #     # First-time user, create new registration state
        #     new_user = await user_service.create_user(Registration(**final_data))
            
        #     state = RegistrationState()
        #     state.start()
        #     state.add_step(f"first verification with phone number for user {new_user}")
        # else:
        #     # User already has a state — deserialize and continue using it
        #     state = RegistrationState.from_dict(user_state.to_dict())
        #     state.add_step("user revisited registration step (already exists)")

        # # Update or persist the state
        # await user_service.update_registration_state(user_wa_id, state)
        # logger.info(f"user_state: {state.to_dict()}")
        









