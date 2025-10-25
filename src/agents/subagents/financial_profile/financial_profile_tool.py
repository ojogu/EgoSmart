from typing import Optional
from google.adk.tools import ToolContext, FunctionTool
from src.service.financial_profile import FinancialProfileService
from src.utils.db import  async_session
from src.utils.log import setup_logger  
from src.schemas.financial_profile import IncomeSource, IncomeFrequency, IncomeDateRange

logger = setup_logger(__name__, file_path="financial_profile_tool.log")

async def get_budget_service():
    async with async_session() as db:
        return FinancialProfileService(db=db)

async def read_user_financial_profile(tool_context: ToolContext):
    state = tool_context.state # Get the state dictionary
    whatsapp_phone_number = state["user:whatsapp_phone_number"] 
    logger.info(f"Attempting to read financial profile for user: {whatsapp_phone_number}")
    
    budget_service = await get_budget_service()
    financial_profile = await budget_service.read_user_financial_profile(whatsapp_phone_number)
    if not financial_profile:
        logger.info(f"Financial profile does not exist for user: {whatsapp_phone_number}")
        return {"message": "financial profile does not exist, create one"}
    
    logger.info(f"Successfully retrieved financial profile for user: {whatsapp_phone_number}")
    return financial_profile.to_dict()
read_user_financial_profile_tool = FunctionTool(read_user_financial_profile)



async def update_user_financial_profile(
    tool_context: ToolContext,
    # Standard types for automatic function calling:
    primary_income_source: Optional[str] = None, # Changed from IncomeSource
    income_frequency: Optional[str] = None, # Changed from IncomeFrequency
    monthly_income: Optional[float] = None,
    income_date_range: Optional[str] = None, # Changed from IncomeDateRange
    income_stablity: bool = False,
    has_other_income: bool = False,
    other_income_source: Optional[str] = None, # Changed from IncomeSource
    other_income_monthly_amount: Optional[float] = None,
    other_income_frequency: Optional[str] = None, # Changed from IncomeFrequency
    has_fixed_deductable: bool = False,
    fixed_deductable_amount: Optional[float] = None,
    user_saves: bool = False,
    savings_amount: Optional[float] = None,
    total_estimated_monthly_income: Optional[float] = None,
    currency: str = "NGN",
    is_verified: bool = False
    ):
    
    state = tool_context.state # Get the state dictionary
    whatsapp_phone_number = state["user:whatsapp_phone_number"]  
    logger.info(f"Attempting to update financial profile for user: {whatsapp_phone_number}")
    budget_service = await get_budget_service()
    
    # 1. Prepare data dictionary with *validated* schema types
    profile_data = {}

    # 2. Use the imported schema types (IncomeSource, etc.) for validation *here*
    # This is where the conversion from the input 'str' to the required Enum happens
    if primary_income_source is not None:
        try:
            profile_data["primary_income_source"] = IncomeSource(primary_income_source)
            logger.debug(f"Validated primary_income_source: {primary_income_source}")
        except ValueError:
            logger.warning(f"Invalid primary_income_source: {primary_income_source} for user: {whatsapp_phone_number}")
            return {"error": f"Invalid primary_income_source: {primary_income_source}"}
            
    if income_frequency is not None:
        try:
            profile_data["income_frequency"] = IncomeFrequency(income_frequency)
            logger.debug(f"Validated income_frequency: {income_frequency}")
        except ValueError:
            logger.warning(f"Invalid income_frequency: {income_frequency} for user: {whatsapp_phone_number}")
            return {"error": f"Invalid income_frequency: {income_frequency}"}
            
    if monthly_income is not None:
        profile_data["monthly_income"] = monthly_income
        logger.debug(f"Validated monthly_income: {monthly_income}")
        
    if income_date_range is not None:
        try:
            profile_data["income_date_range"] = IncomeDateRange(income_date_range)
            logger.debug(f"Validated income_date_range: {income_date_range}")
        except ValueError:
            logger.warning(f"Invalid income_date_range: {income_date_range} for user: {whatsapp_phone_number}")
            return {"error": f"Invalid income_date_range: {income_date_range}"}
            
    # Include all other parameters as before...
    if income_stablity is not False: 
        profile_data["income_stablity"] = income_stablity
        logger.debug(f"Validated income_stablity: {income_stablity}")
    if has_other_income is not False: 
        profile_data["has_other_income"] = has_other_income
        logger.debug(f"Validated has_other_income: {has_other_income}")
        
    if other_income_source is not None:
        try:
            profile_data["other_income_source"] = IncomeSource(other_income_source)
            logger.debug(f"Validated other_income_source: {other_income_source}")
        except ValueError:
            logger.warning(f"Invalid other_income_source: {other_income_source} for user: {whatsapp_phone_number}")
            return {"error": f"Invalid other_income_source: {other_income_source}"}

    if other_income_monthly_amount is not None:
        profile_data["other_income_monthly_amount"] = other_income_monthly_amount
        logger.debug(f"Validated other_income_monthly_amount: {other_income_monthly_amount}")
        
    if other_income_frequency is not None:
        try:
            profile_data["other_income_frequency"] = IncomeFrequency(other_income_frequency)
            logger.debug(f"Validated other_income_frequency: {other_income_frequency}")
        except ValueError:
            logger.warning(f"Invalid other_income_frequency: {other_income_frequency} for user: {whatsapp_phone_number}")
            return {"error": f"Invalid other_income_frequency: {other_income_frequency}"}
            
    if has_fixed_deductable is not False: 
        profile_data["has_fixed_deductable"] = has_fixed_deductable
        logger.debug(f"Validated has_fixed_deductable: {has_fixed_deductable}")
    if fixed_deductable_amount is not None:
        profile_data["fixed_deductable_amount"] = fixed_deductable_amount
        logger.debug(f"Validated fixed_deductable_amount: {fixed_deductable_amount}")
    if user_saves is not False: 
        profile_data["user_saves"] = user_saves
        logger.debug(f"Validated user_saves: {user_saves}")
    if savings_amount is not None:
        profile_data["savings_amount"] = savings_amount
        logger.debug(f"Validated savings_amount: {savings_amount}")
    if total_estimated_monthly_income is not None:
        profile_data["total_estimated_monthly_income"] = total_estimated_monthly_income
        logger.debug(f"Validated total_estimated_monthly_income: {total_estimated_monthly_income}")
    if currency != "NGN": 
        profile_data["currency"] = currency
        logger.debug(f"Validated currency: {currency}")
    if is_verified is not False: 
        profile_data["is_verified"] = is_verified
        logger.debug(f"Validated is_verified: {is_verified}")

    # 3. Call the service with the validated data
    financial_profile = await budget_service.update_financial_profile_if_missing(
        whatsapp_phone_number=whatsapp_phone_number,
        **profile_data
    )
    logger.info(f"Successfully updated financial profile for user: {whatsapp_phone_number}")
    return financial_profile.to_dict()

update_user_financial_profile_tool = FunctionTool(update_user_financial_profile)
