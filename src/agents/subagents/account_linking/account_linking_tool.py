from src.service.finance import MonoService
from src.service.user import UserService
from src.utils.db import  async_session
from google.adk.tools import ToolContext, FunctionTool
from src.utils.log import setup_logger  # noqa: E402
logger = setup_logger(__name__, file_path="account_linking_tool.log")


async def get_user_service():
    async with async_session() as db:
        return UserService(db=db)

async def get_mono_service():
    async with async_session() as db:
        return MonoService(db=db)



async def check_link_status( tool_context:ToolContext):
    """
    Checks the account linking status for a given WhatsApp phone number.

    This function queries the Mono service to determine if an account is linked
    to the provided WhatsApp number. It returns the linking status or indicates
    if the user does not exist.

    Args:
        whatsapp_phone_number (str): The WhatsApp phone number of the user.


    Returns:
        dict: A dictionary containing the linking status.
              Example: {"status": "linked"} or "user does not exist"
    """
    state = tool_context.state # Get the state dictionary
    whatsapp_phone_number = state["whatsapp_phone_number"]
    logger.info(f"Checking link status for WhatsApp number: {whatsapp_phone_number}")
    mono_service = await get_mono_service()
    account = await mono_service.check_if_account_linked(whatsapp_phone_number)
    if account is None: 
        logger.info(f"Account not found for WhatsApp number: {whatsapp_phone_number}")
        return "user does not exist"
    status = account.linking_status.value
    logger.info(f"Link status for {whatsapp_phone_number}: {status}")
    return {"status":status}

check_link_status_tool = FunctionTool(check_link_status)

async def verify_link_completion( tool_context:ToolContext):
    """
    Verifies the completion of the account linking process for a WhatsApp phone number.

    This function checks the linking status of an account with the Mono service.
    It returns the linking status and the timestamp of when the account was linked,
    or indicates if the user does not exist.

    Args:
        whatsapp_phone_number (str): The WhatsApp phone number of the user.


    Returns:
        dict: A dictionary containing the linking status and linked timestamp.
              Example: {"status": "linked", "linked at": "2023-10-27T10:00:00Z"}
              or "user does not exist"
    """
    state = tool_context.state # Get the state dictionary
    whatsapp_phone_number = state["whatsapp_phone_number"]
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


async def initiate_account_link(email:str, first_name:str, last_name:str, tool_context:ToolContext):
    
    """
    Initiates the account linking process for a user.

    This function updates the user's profile with the provided email, first name, and last name. It then initiates the account linking
    process with the Mono service and returns the URL for the linking.

    Args:
        whatsapp_phone_number (str): The WhatsApp phone number of the user.
        email (str): The email address of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.


    Returns:
        dict: A dictionary containing the Mono account linking URL.
              Example: {"mono_url": "https://mono.co/link/..."}
    """
    state = tool_context.state # Get the state dictionary
    state["user:first_name"] = first_name
    state["user:last_name"] = last_name
    state["user:email"] = email
    whatsapp_phone_number = state["whatsapp_phone_number"]
    logger.info(f"Initiating account link for WhatsApp number: {whatsapp_phone_number}, email: {email}")
    user_service = await get_user_service()
    mono_service = await get_mono_service()
    user = await user_service.update_profile_if_missing(
        whatsapp_phone_number=whatsapp_phone_number,
        first_name=first_name,
        last_name=last_name,
        email=email
    )

    user_data = {
        "first_name":user.first_name,
        "last_name":user.last_name,
        "email":user.email
    }
    logger.info(f"User profile updated: {user_data}")
    mono_url = await mono_service.linking_account_initation(whatsapp_phone_number,**user_data)
    logger.info(f"Mono account linking initiated, URL: {mono_url}")
    return {"mono_url": mono_url}

initiate_account_link_tool = FunctionTool(initiate_account_link)
