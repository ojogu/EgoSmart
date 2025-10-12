# import logging
# from fastapi import APIRouter, HTTPException, Request, Response, status, Depends
# from fastapi.responses import JSONResponse
# import json
# # from src.utils.logger import logger
# from src.service.whatsapp import send_whatsapp_message, download_twilio_media
# from src.service.agent import get_user, get_or_create_session
# from src.agents.agent import AgentManager, call_agent_and_log
# import json
# import ast
# from src.agents.orchestrator import parse_message_generate_intent
# from src.service.user import UserService
# from src.utils.db import get_session
# from sqlalchemy.ext.asyncio import AsyncSession



# logger = logging.getLogger(__name__)
# file_handler = logging.FileHandler("src/logs/twillo.log")
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)
# logger.setLevel(logging.INFO)
# logger.propagate = False


# twillo_route = APIRouter(prefix="/twillo")

# def get_user_service(db: AsyncSession = Depends(get_session)):
#     return UserService(db=db)

# @twillo_route.post("/incoming", status_code=status.HTTP_200_OK)
# async def incoming_message(request: Request, user_service:UserService = Depends(get_user_service)):

#     headers = dict(request.headers)
#     content_type = headers.get("content-type", "unknown")

#     body_bytes = await request.body()
#     body_text = body_bytes.decode("utf-8", errors="replace")

#     parsed_body = None
#     if content_type.startswith("application/json"):
#         try:
#             parsed_body = await request.json()
#         except Exception as e:
#             logger.warning("JSON parse failed: %s", str(e))
#     elif content_type.startswith("application/x-www-form-urlencoded"):
#         try:
#             form = await request.form()
#             parsed_body = dict(form)
#         except Exception as e:
#             logger.warning("Form parse failed: %s", str(e))

#     logger.info("Webhook received")
#     logger.info("incoming: %s", parsed_body)
#     if parsed_body:
#         # logger.info(parsed_body)
#         if "Body" in parsed_body:
#             message_body = parsed_body["Body"]
#             name = parsed_body["ProfileName"]
#             user_id = parsed_body["From"]
#             phone_number = user_id.split(":")[-1]  # Extracts from the colon down, e.g. 'whatsapp:+2349065011334' -> '+2349065011334'
            
#             user = await user_service.create_user(phone_number)
#             #whatsapp flow to continue other part of auth flow
            
            
#             # if parsed_body["MediaContentType0"] or parsed_body["MediaContentType1"]:
#             #     logger.info("Media content detected")
#             #     media_url = parsed_body["MediaUrl0"]
#             #     logger.info("Downloading media...")
#             #     await download_twilio_media(media_url)
#             #     logger.info("Media downloaded successfully.")
#                 # logger.info("Media URL: %s", media_url)
#             # 1. Get or create user
#             message = {"phone_num": user_id, "message": str(message_body), "name": name}
#             message = str(message)
#             # await get_or_create_user(user_id)

#             # # 2. Get or create session
#             # session_id = await get_or_create_session(user_id=user_id)
            
#             # parser = await parse_message_generate_intent(message, user_id, session_id)
#             # # Step 1: Get the final_response string
#             # raw_response = parser.get("final_response")

#             # # Step 2: Clean triple backticks and whitespace
#             # clean_json_str = raw_response.strip("` \n")

#             # # Step 3: Convert string to dictionary
#             # parsed_response = json.loads(clean_json_str)

#             # # Step 4: Now access user_message
#             # user_message = parsed_response.get("user_message")
#             # logger.info(f"User message: {user_message}")
            
#             # message = send_whatsapp_message(message_body=user_message, to_number=parsed_body["From"], from_number=parsed_body["To"])
#             # logger.info(user_message)

#             # logger.info(json.dumps(CapitalInfoOutput.model_json_schema(), indent=2))
#             # # 3. Ask agent
#             # creator = AgentManager(
#             #     app_name="egosmart",
#             #     user_id=user_id,
#             #     session_id=session_id,
#             #     model_name="openrouter/meta-llama/llama-3.3-8b-instruct:free"
#             # )
            
#             # agent = creator.create_agent(
#             #     name="response_agent",
#             #     description="Provides capital and estimated population in a specific JSON format.",
#             #     instruction=f"""You are an agent that provides country information.
#             #     The user will provide the country phone number code eg +234 in a JSON format like {{"full_number": "phone_number"}}.
#             #     Respond ONLY with a JSON object matching this exact schema:
#             #     {json.dumps(CapitalInfoOutput.model_json_schema(), indent=2)}
#             #     Use your knowledge to determine the country, capital and estimate the population. Do not use any tools.
#             #     """,
#             #     output_schema=CapitalInfoOutput,
#             #     output_key="capital_info",
#             #     input_schema=CountryInput,
#             # )
            
#             # runner = creator.runner(agent)

#             # response = await call_agent_and_log(agent_manager = creator, 
#             # agent=agent,
#             # runner = runner, query_json=message)
#             # final_response = response.get("final_response")
#             # if isinstance(final_response, str):
#             #     final_response = ast.literal_eval(final_response)
#             # logger.info(type(final_response))
#             # user_message = f"Hello {parsed_body['ProfileName']}, from {final_response.get('country')}, the capital is {final_response.get('capital')} and the estimated population is {final_response.get('population_estimate')}"





#             # 4. Return response to Twilio
#             # return {"message": response.get("text", "I didn't understand that.")}
#     return {"status": "ok"}

# @twillo_route.post("/outgoing", status_code=status.HTTP_200_OK)
# async def handle_outgoing_message(request: Request):
#     try:
#         headers = dict(request.headers)
#         content_type = headers.get("content-type", "unknown")

#         body_bytes = await request.body()
#         body_text = body_bytes.decode("utf-8", errors="replace")

#         parsed_body = None
#         if content_type.startswith("application/json"):
#             try:
#                 parsed_body = await request.json()
#             except Exception as e:
#                 logger.warning("JSON parse failed (outgoing): %s", str(e))
#         elif content_type.startswith("application/x-www-form-urlencoded"):
#             try:
#                 form = await request.form()
#                 parsed_body = dict(form)
#             except Exception as e:
#                 logger.warning("Form parse failed (outgoing): %s", str(e))

#         logger.info("Outgoing webhook received")
#         logger.info("Parsed Outgoing Body: %s", parsed_body)
#         # Add your outgoing message handling logic here

#         return {"status": "ok"}
#     except Exception as e:
#         logger.error(f"Exception in /outgoing handle_outgoing_message: {str(e)}", exc_info=True)
#         return JSONResponse(content={"error": "Internal server error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# import secrets
# import binascii

# def generate_token(length=32):
#     token = secrets.token_bytes(length)
#     return binascii.hexlify(token).decode('utf-8')

# verification_token = generate_token()
# print(verification_token)

from typing import Dict
from src.utils.config import config
import logging
import aiohttp
import asyncio

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("src/logs/twillo.log")
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
logger.propagate = False

async def exchange_access_token() -> Dict:
    """
    Exchange a short-lived access token for a long-lived token.
    """
    url = "https://graph.facebook.com/v19.0/oauth/access_token"
    app_id = config.APP_ID
    app_secret = config.APP_SECRET
    short_lived_token = config.ACCESS_TOKEN  # Use current token!

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
                    # Optionally: store this token somewhere
                    logger.info(f"New access token obtained: {new_token}")

                return {
                    "status": resp.status,
                    "response": data,
                    "access_token": new_token if new_token else None
                }
    except Exception as e:
        logger.exception(f"Exception during access token exchange: {e}")
        return {
            "status": "error",
            "response": str(e)
        }

async def debug_token(input_token: str) -> Dict:
    """
    Debug a token using Facebook's debug_token endpoint.
    """
    url = "https://graph.facebook.com/debug_token"
    app_id = config.APP_ID
    app_secret = config.APP_SECRET
    access_token = f"{app_id}|{app_secret}"

    params = {
        "input_token": input_token,
        "access_token": access_token
    }
    logger.info("Attempting to debug token.")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                data: dict = await resp.json()
                logger.info(f"Token debug response: {data}")
                return {
                    "status": resp.status,
                    "response": data
                }
    except Exception as e:
        logger.exception(f"Exception during token debug: {e}")
        return {
            "status": "error",
            "response": str(e)
        }

# Example usage: debug the current WhatsApp token
if __name__ == "__main__":
#     # Run the token exchange in an event loop
#     result = asyncio.run(exchange_access_token())
#     logger.info(result)

    # Debug the WhatsApp token
    debug_result = asyncio.run(debug_token(config.ACCESS_TOKEN))
    logger.info(debug_result)

