from src.service.finance import MonoService
from src.utils.db import get_session
from src.service.user import UserService

db = get_session()
mono_service = MonoService(db)
user_service = UserService(db)

async def collect_user_details(user_id: str, first_name: str, last_name: str, email: str):
    """
    Collects and updates user details if the profile is incomplete.

    This function checks if a user's profile is missing essential details
    (first name, last name, or email) and, if so, updates the profile
    with the provided information.

    Args:
        user_id (str): The user's WhatsApp phone number.
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        email (str): The user's email address.

    Returns:
        str: a string describing the current state of the user profile.
    """
    profile_status = await user_service.check_missing_profile_fields(user_id)
    if profile_status.get("user_profile_data"):
        return await user_service.update_profile_if_missing(
            whatsapp_phone_number=user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
    return "user profile not completed"
