import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Response, status, Depends, Request
import logging
# from src.schemas.schema import Registration, User
from src.service.whatsapp import WhatsAppClient
from src.service.google import google_service
from fastapi.responses import JSONResponse
from src.service.user import UserService
from src.utils.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from src.utils.log import setup_logger  # noqa: E402
logger = setup_logger(__name__, file_path="google.log")

google_route = APIRouter(prefix="/google")

def get_user_service(db: AsyncSession = Depends(get_session)):
    return UserService(db=db)

def get_whatsapp_service():
    return WhatsAppClient()

@google_route.get("/login", status_code=status.HTTP_200_OK)
async def oauth_login():
    try:
        url = google_service.login_with_google()
        return {
            "url": url
        }
    except Exception as e:
        logger.error(f"Exception in /login oauth_login: {str(e)}", exc_info=True)
        return JSONResponse(content={"error": "Internal server error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



@google_route.get("/callback", status_code=status.HTTP_200_OK)
async def oauth(request: Request, user_service:UserService = Depends(get_user_service)):
    try:
        params = dict(request.query_params)
        logger.info(f"query_params; {params}")
        data = google_service.handle_callback(request)
        # logger.info(f"user google_data: {data}")
        user_data = google_service.verify_id(data["id_token"])
        user_info = {
            "google_id": user_data["sub"],
            "refresh_token": data["refresh_token"],
            "access_token": data["access_token"],
            "email": user_data["email"],
            "oauth_verified": True,
            "onboarded": True,
            "email_verified": user_data["email_verified"],
            "name": user_data["name"],
            "picture": user_data.get("picture"),
            "first_name": user_data.get("given_name"),
            "last_name": user_data.get("family_name"),
        }
        logger.info(f"user_data: {user_info}")

        # Check if user exists by google_id or email
        existing_user = await user_service.get_user_by_email(
            email=user_info["email"]
        )

        if existing_user:
            # Compare emails
            if existing_user.get("email") == user_info["email"]:
                # Update user info
                updated_user = await user_service.update_user(
                    email=existing_user["email"], update_data=user_info
                )
                logger.info(f"user updated: {updated_user}")
                message = {"message": "user_updated"}
            else:
                logger.warning("Email mismatch for existing user.")
                message = {"message": "email_mismatch"}
        else:
            # Create new user
            new_user = await user_service.create_user(**user_info)
            logger.info(f"new_user: {new_user}")
            message = {"message": "user_created"}

        return JSONResponse(content=message, status_code=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Exception in /google oauth: {str(e)}", exc_info=True)
        return JSONResponse(content={"error": "Internal server error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
