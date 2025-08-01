from typing import Optional
import uuid
from src.schemas.schema import UserUpdate, CreateUser, Registration
from src.model.user import User, Profile 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from src.base.exception import (
    AlreadyExistsError,
    DatabaseError
)
import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.service.state import RegistrationState

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("src/logs/user.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
logger.propagate = False

class UserService:
    """Service layer for user-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Fetch a user by their UUID."""
        if not isinstance(user_id, uuid.UUID):
            user_id = uuid.UUID(user_id, version=4)
        result = await self.db.execute(select(User).where(User.unique_id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by their email address."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_whatsapp_phone_number(self, whatsapp_phone_number: str) -> Optional[User]:
        """Fetch a user by their email address."""
        result = await self.db.execute(
            select(User).where(User.whatsapp_phone_number == whatsapp_phone_number)
        )
        return result.scalar_one_or_none()

    async def create_user(self, user_data: Registration) -> User:
        """Create a new user."""
        # Check if phone_number already exists
        existing_user = await self.get_user_by_whatsapp_phone_number(user_data.whatsapp_phone_number)
        if existing_user:
            logger.warning(F"user already exists: {existing_user}")
            return existing_user
    
        new_user = User(
            **user_data.model_dump(exclude={"country_flag"})
        )
        logger.info(f"Creating new user with WhatsApp phone number: {new_user.whatsapp_phone_number}, ID: {new_user.unique_id}")
        self.db.add(new_user)
        try:
            await (
                self.db.flush()
            )  # Use flush to get potential errors before commit
            await self.db.refresh(
                new_user
            )  # Refresh to get DB defaults like ID, created_at
            await self.db.commit()
            
            return new_user.to_dict()
        
        except IntegrityError as e:
            await self.db.rollback()
            # Check if it's a unique constraint violation (though checked above, good practice)
            if "unique constraint" in str(e).lower():
                raise AlreadyExistsError(
                    f"Email '{user_data.whatsapp_phone_number}' is already registered (concurrent request?)."
                )
            else:
                # Handle other potential integrity errors
                logger.error(f"Error creating user: {e}")
                raise DatabaseError(f"Database integrity error: {e}") from e
        except SQLAlchemyError as e:
            logger.error(f"Error creating user: {e}")
            await self.db.rollback()
            raise DatabaseError(f"Could not create user: {e}") from e

    async def check_missing_profile_fields(self, user_id: str) -> dict:
        """Check if a user's profile has missing fields."""
        user = await self.get_user_by_whatsapp_phone_number(user_id)
        if not user:
            return {"user_profile_data": "user does not exist"}
        
        # Assuming user object has first_name, last_name, and email attributes
        is_missing = not all([user.first_name, user.last_name, user.email])
        return {"user_profile_data": is_missing}

    async def update_profile_if_missing(
        self,
        whatsapp_phone_number: str,
        first_name: str,
        last_name: str,
        email: str
    ) -> str:
        """Update profile if fields are missing and return the user."""
        try:
            user = await self.get_user_by_whatsapp_phone_number(whatsapp_phone_number)
            if not user:
                logger.info(f"User with WhatsApp number {whatsapp_phone_number} not found.")
                return (f"User with WhatsApp number {whatsapp_phone_number} not found.")
                # return None

            # Check if any of the fields are missing
            if not (user.first_name is None or user.last_name is None or user.email is None):
                logger.info(f"Profile for {whatsapp_phone_number} is already complete. No update needed.")
                # return user
                return (f"Profile for {whatsapp_phone_number} is already complete. No update needed.")

            # Perform the update
            logger.info(f"Updating profile for user {whatsapp_phone_number}")
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"Successfully updated profile for user {whatsapp_phone_number}")
            return (f"Successfully updated profile for user {whatsapp_phone_number}")
            # return user
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error updating profile for {whatsapp_phone_number}: {e}")
            raise DatabaseError(f"Could not update profile: {e}") from e

        
        
    # async def update_user(
    #     self, user_id: uuid.UUID, update_data: UpdateUserRequest, requesting_user: User
    # ) -> User:
    #     """Update an existing user."""
    #     user = await self.get_user_by_id(user_id)
    #     if not user:
    #         raise UserNotFoundException(f"User with ID {user_id} not found.")

    #     update_dict = update_data.model_dump(exclude_unset=True)

    #     # Handle password update separately
    #     if "password" in update_dict:
    #         new_password = update_dict.pop("password")
    #         user.hashed_password = self.get_password_hash(new_password)

    #     # Handle email update - check for uniqueness if changed
    #     if "email" in update_dict and update_dict["email"].lower() != user.email:
    #         new_email = update_dict["email"].lower()
    #         existing_user = await self.get_user_by_email(new_email)
    #         if existing_user:
    #             raise EmailAlreadyExistsException(
    #                 f"Email '{new_email}' is already registered."
    #             )
    #         user.email = new_email
    #         update_dict.pop("email")  # Remove email from dict as it's handled

    #     # Check for sensitive fields and authorize admin access
    #     sensitive_fields = {"role", "reputation_points", "is_verified_agent"}
    #     updating_sensitive = sensitive_fields.intersection(update_dict.keys())

    #     if updating_sensitive and requesting_user.role != UserRole.ADMIN:
    #         raise AuthorizationException(  # Use renamed exception
    #             f"Admin privileges required to update fields: {', '.join(updating_sensitive)}"
    #         )

    #     # Update remaining fields
    #     for key, value in update_dict.items():
    #         setattr(user, key, value)

    #     try:
    #         await self.db.flush()
    #         await self.db.refresh(user)
    #         return user
    #     except IntegrityError as e:
    #         await self.db.rollback()
    #         if "unique constraint" in str(e).lower() and "email" in str(e).lower():
    #             raise EmailAlreadyExistsException(
    #                 "Email update failed due to conflict (concurrent request?)."
    #             )
    #         else:
    #             raise ValueError(f"Database integrity error during update: {e}") from e
    #     except Exception as e:
    #         await self.db.rollback()
    #         raise ValueError(f"Could not update user {user_id}: {e}") from e

    # async def delete_user(self, user_id: uuid.UUID) -> bool:
    #     """Delete a user by ID."""
    #     user = await self.get_user_by_id(user_id)
    #     if not user:
    #         raise UserNotFoundException(f"User with ID {user_id} not found.")

    #     try:
    #         await self.db.delete(user)
    #         await self.db.flush()
    #         return True
    #     except Exception as e:
    #         await self.db.rollback()
    #         # Consider logging the error
    #         print(f"Error deleting user {user_id}: {e}")
    #         return False
    

# user_service = UserService()
