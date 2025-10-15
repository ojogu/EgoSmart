from src.service.finance import MonoService
from src.service.user import UserService
from src.utils.db import get_session
from google.adk.tools import ToolContext, FunctionTool

async def get_user_service():
    async with get_session() as db:
        return UserService(db=db)

async def get_mono_service():
    async with get_session() as db:
        return MonoService(db=db)



async def fetch_update_user_details(whatsapp_phone_number,first_name, last_name, email, tool_contex:ToolContext):
    user_service = await get_user_service()
    mono_service = await get_mono_service()
    
    user = user_service.update_profile_if_missing(
        whatsapp_phone_number=whatsapp_phone_number,
        first_name=first_name,
        last_name=last_name,
        email=email
    )

async def link_account(whatsapp_phone_number):
    user_service = await get_user_service()
    mono_service = await get_mono_service()
    user = user_service.get_user_by_whatsapp_phone_number(whatsapp_phone_number)
    user_data = {
        "first_name":user.first_name,
        "last_name":user.last_name,
        "email":user.email
    }
    account_link = await mono_service.linking_account_initation(**user_data)
    
    