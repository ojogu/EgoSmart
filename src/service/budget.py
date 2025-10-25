from src.model import FinancialProfile, User
from src.service.user import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from src.base.exception import (
    AlreadyExistsError,
    DatabaseError
)
from src.schemas.financial_profile import FinancialProfile as FinancialProfileSchema
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.utils.log import setup_logger  # noqa: E402
logger = setup_logger(__name__, file_path="budget.log")


class Budgeting():
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db=db)
    

    async def update_financial_profile_if_missing(
        self,
        whatsapp_phone_number,
        **data:FinancialProfileSchema 
    ) -> str:
        """Update profile if fields are missing and return the user."""
        validated_data = FinancialProfileSchema(**data)
        try:
            user = await self.user_service.get_user_by_whatsapp_phone_number(whatsapp_phone_number)
            if not user:
                logger.warning(f"user: {whatsapp_phone_number} does not exist, create user")
                user = await self.user_service.create_user(whatsapp_phone_number=whatsapp_phone_number)
                logger.info(f"successfully created user: {whatsapp_phone_number}")
            
            #fetch financial profile
            stmt = select(FinancialProfile).where(user.whatsapp_phone_number == FinancialProfile.user_id)
            result = await self.db.execute(stmt)
            financial_profile = result.scalars().first()
            
            if not financial_profile:
                logger.warning(f"Financial profile for user: {whatsapp_phone_number} does not exist, creating one.")
                financial_profile = FinancialProfile(user_id=whatsapp_phone_number)
                self.db.add(financial_profile)
                await self.db.commit()
                await self.db.refresh(financial_profile)
                logger.info(f"Successfully created financial profile for user: {whatsapp_phone_number}")

            # Check if any of the fields in validated_data are present and the corresponding financial_profile field is missing
            fields_to_update = {}
            for field, value in validated_data.model_dump(exclude_unset=True).items():
                if field == "user_id":
                    continue
                if getattr(financial_profile, field) is None and value is not None:
                    fields_to_update[field] = value
            
            if not fields_to_update:
                logger.info(f"Financial profile for {whatsapp_phone_number} is already complete or no new data provided. No update needed.")
                return user # Still returning user as per original function signature

            # Perform the update
            logger.info(f"Updating financial profile for user {whatsapp_phone_number}")
            for field, value in fields_to_update.items():
                setattr(financial_profile, field, value)
            
            await self.db.commit()
            await self.db.refresh(financial_profile)
            
            logger.info(f"Successfully updated financial profile for user {whatsapp_phone_number}")
            return user # Still returning user as per original function signature
        
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error updating profile for {whatsapp_phone_number}: {e}")
            raise DatabaseError(f"Could not update profile: {e}") from e

    
    async def read_user_profile(self, user_id):
        pass 
    
    async def create_budget(self, user_id, budget_data):
        pass 
    
    async def updated_budget(self, user_id, budget_data):
        pass 
    
    async def check_progress(self, user_id):
        pass 
    
    async def get_all_budgets(self, user_id):
        pass 
    
    async def set_alert(self, user_id):
        pass 
    
    async def schedule_reminder(self, user_id):
        pass 
    
    async def generate_budget_summary(self, user_id):
        pass 
    
    # These happen IMMEDIATELY - no scheduling
    async def send_immediate_alert(self, user_id, message):
        pass
