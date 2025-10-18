from src.service.finance import MonoService
from src.service.user import UserService
from src.utils.db import get_session
from google.adk.tools import ToolContext, FunctionTool
from src.utils.log import setup_logger  # noqa: E402
logger = setup_logger(__name__, file_path="account_linking_tool.log")


async def get_user_service():
    async with get_session() as db:
        return UserService(db=db)

async def get_mono_service():
    async with get_session() as db:
        return MonoService(db=db)



async def check_link_status(whatsapp_phone_number:str, tool_context:ToolContext): 
    logger.info(f"Checking link status for WhatsApp number: {whatsapp_phone_number}")
    mono_service = await get_mono_service()
    account = await mono_service.check_if_account_linked(whatsapp_phone_number)
    if account is None: 
        logger.info(f"Account not found for WhatsApp number: {whatsapp_phone_number}")
        return "user does not exist"
    status = account.linking_status.value
    state = tool_context.state # Get the state dictionary
    logger.info(f"Link status for {whatsapp_phone_number}: {status}")
    return {"status":status}

check_link_status_tool = FunctionTool(check_link_status)

async def verify_link_completion(whatsapp_phone_number:str, tool_context:ToolContext): 
    logger.info(f"Verifying link completion for WhatsApp number: {whatsapp_phone_number}")
    mono_service = await get_mono_service()
    account = await mono_service.check_if_account_linked(whatsapp_phone_number)
    if account is None: 
        logger.info(f"Account not found for WhatsApp number: {whatsapp_phone_number}")
        return "user does not exist"
    status = account.linking_status.value
    state = tool_context.state # Get the state dictionary
    logger.info(f"Link completion status for {whatsapp_phone_number}: {status}, linked at: {account.created_at}")
    return {"status":status, "linked at": account.created_at}
    
verify_link_completion_tool = FunctionTool(verify_link_completion)


async def initiate_account_link(whatsapp_phone_number:str, email:str, first_name:str, last_name:str, tool_context:ToolContext):
    logger.info(f"Initiating account link for WhatsApp number: {whatsapp_phone_number}, email: {email}")
    user_service = await get_user_service()
    mono_service = await get_mono_service()
    user = user_service.update_profile_if_missing(
        whatsapp_phone_number=whatsapp_phone_number,
        first_name=first_name,
        last_name=last_name,
        email=email
    )
    state = tool_context.state # Get the state dictionary
    state["user:first_name"] = first_name
    state["user:last_name"] = last_name
    state["user:first_name"] = email
    user_data = {
        "first_name":user.first_name,
        "last_name":user.last_name,
        "email":user.email
    }
    logger.info(f"User profile updated: {user_data}")
    mono_url = await mono_service.linking_account_initation(**user_data)
    logger.info(f"Mono account linking initiated, URL: {mono_url}")
    return mono_url

initiate_account_link_tool = FunctionTool(initiate_account_link)
