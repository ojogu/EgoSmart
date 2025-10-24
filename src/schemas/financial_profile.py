from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

# Assuming these are string enums. Adjust if their actual definitions are different.
class IncomeSource(str, Enum):
    SALARY = "salary"
    FREELANCE = "freelance"
    INVESTMENT = "investment"
    BUSINESS = "business"
    OTHER = "other"

class IncomeFrequency(str, Enum):
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    BI_WEEKLY = "bi_weekly"
    IRREGULAR = "irregular"

class IncomeDateRange(str, Enum):
    BEGINNING_OF_MONTH = "beginning_of_month"
    MIDDLE_OF_MONTH = "middle_of_month"
    END_OF_MONTH = "end_of_month"
    IRREGULAR = "irregular"

class FinancialProfile(BaseModel):
    """
    Stores the user's financial baseline used for budgeting and income analysis.
    This model helps the budgeting sub-agent understand earning patterns,
    timing, and variability to craft realistic budget recommendations.
    """
    user_id: str = Field(..., description="Core User Link: User's WhatsApp phone number.")

    # Income Information
    primary_income_source: Optional[IncomeSource] = Field(None, description="Identify user type and earning model (for financial behavior prediction).")
    income_frequency: Optional[IncomeFrequency] = Field(None, description="Determines budget cycle type (monthly, weekly, irregular).")
    monthly_income: Optional[float] = Field(None, description="Establish baseline income for allocations and insights.")
    income_date_range: Optional[IncomeDateRange] = Field(None, description="For scheduling reminders, resetting budgets, or prompting the user to plan.")
    income_stablity: bool = Field(False, description="Helps determine how conservative to be when suggesting budget allocations.")

    # Secondary Income (optional)
    has_other_income: bool = Field(False, description="Detect multiple income streams for total inflow calculation.")
    other_income_source: Optional[IncomeSource] = Field(None)
    other_income_monthly_amount: Optional[float] = Field(None)
    other_income_frequency: Optional[IncomeFrequency] = Field(None)
    
    # Expenses
    has_fixed_deductable: bool = Field(False)
    fixed_deductable_amount: Optional[float] = Field(None, description="Identify deductions like rent, tithe, savings, or transfers that occur before spending.")
    
    # Savings
    user_saves: bool = Field(False)
    savings_amount: Optional[float] = Field(None, description="Understand saving habits and recommend appropriate strategies.")
    
    # mode_of_payment: str = Field(..., description="Determines tracking method (manual entry vs. linked account or image receipt).")
    
    # Future-Proofing for Budgeting
    total_estimated_monthly_income: Optional[float] = Field(None)
    currency: str = Field("NGN", description="Currency used for financial transactions.")
    is_verified: bool = Field(False, description="e.g. if confirmed via transactions")
