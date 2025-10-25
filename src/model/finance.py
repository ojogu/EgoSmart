from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Enum as SqlEnum, Integer, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref
from enum import Enum
from src.base.model import BaseModel
from .user import User

class IncomeSource(Enum):
    FULL_TIME = "Full-time (9-5 job)"
    FREELANCING = "Freelancing/Gig work"
    BUSINESS = "Business/Self-employed"
    STUDENT_ALLOWANCE = "Student Allowance"
    OTHER = "Other"

class IncomeFrequency(Enum):
    MONTHLY = "Monthly"
    BI_WEEKLY = "Bi-weekly"
    WEEKLY = "Weekly"
    IRREGULAR = "Irregular/Varies"

class IncomeDateRange(Enum):
    FIRST_TO_TENTH = "1st-10th"
    ELEVENTH_TO_TWENTIETH = "11th-20th"
    TWENTY_FIRST_TO_THIRTY_FIRST = "21st-31st"
    IRREGULAR = "irregular"
 
 
class Budget(BaseModel):
    """
    Represents a user's high-level budget plan (monthly, weekly, or custom period).
    Each budget is linked to a financial profile and contains multiple categories.
    """
    __tablename__ = "budgets"

    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.whatsapp_phone_number"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, default="Monthly Budget", nullable=False)
    period: Mapped[str] = mapped_column(String, default="monthly")  # monthly, weekly, custom
    start_date: Mapped[datetime] = mapped_column(nullable=True)
    end_date: Mapped[datetime] = mapped_column(nullable=True)

    total_income: Mapped[int] = mapped_column(Float, nullable=True)
    total_allocated: Mapped[int] = mapped_column(Float, nullable=True)
    total_spent: Mapped[int] = mapped_column(Float, default=0)
    remaining_balance: Mapped[int] = mapped_column(Float, default=0)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


    # Relationships
    categories: Mapped[List["BudgetCategory"]] = relationship(
        "BudgetCategory", back_populates="budget", cascade="all, delete-orphan"
    )
    user: Mapped["User"] = relationship("User", backref="budgets")
   
class BudgetCategory(BaseModel):
    """
    Represents a category allocation within a user's budget plan.
    Example: Food - ₦30,000, Rent - ₦50,000, Transportation - ₦15,000
    """
    __tablename__ = "budget_categories"

    budget_id: Mapped[int] = mapped_column(ForeignKey("budgets.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    allocated_amount: Mapped[int] = mapped_column(Float, nullable=False)
    spent_amount: Mapped[int] = mapped_column(Float, default=0)
    remaining_amount: Mapped[int] = mapped_column(Float, default=0)
    priority: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # e.g. 1-5 importance ranking


    # Relationship
    budget: Mapped["Budget"] = relationship("Budget", back_populates="categories")
    transactions: Mapped[List["BudgetTransaction"]] = relationship(
        "BudgetTransaction", back_populates="category", cascade="all, delete-orphan"
    )
  
class BudgetTransaction(BaseModel):
    """
    Tracks actual spending or income related to a specific budget category.
    This helps compare planned vs actual performance.
    """
    __tablename__ = "budget_transactions"


    category_id: Mapped[int] = mapped_column(ForeignKey("budget_categories.id"), nullable=False)
    amount: Mapped[int] = mapped_column(Float, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    transaction_type: Mapped[str] = mapped_column(String, default="expense")  # expense | income
    transaction_date: Mapped[datetime] = mapped_column(default=func.now())

    # Relationships
    category: Mapped["BudgetCategory"] = relationship("BudgetCategory", back_populates="transactions")



class FinancialProfile(BaseModel):
    """
    Stores the user's financial baseline used for budgeting and income analysis.
    This model helps the budgeting sub-agent understand earning patterns,
    timing, and variability to craft realistic budget recommendations.
    """
    __tablename__ = "financial_profiles"

    # Core User Link
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.whatsapp_phone_number"), nullable=False
    )

    # Income Information
    primary_income_source: Mapped[Optional[IncomeSource]] = mapped_column(
        SqlEnum(IncomeSource, name="primary_income_source_enum"), nullable=True
    ) #Identify user type and earning model (for financial behavior prediction).
    
    income_frequency: Mapped[Optional[IncomeFrequency]] = mapped_column(
        SqlEnum(IncomeFrequency, name="income_frequency_enum"), nullable=True
    )#Determines budget cycle type (monthly, weekly, irregular).
    
    monthly_income: Mapped[Optional[float]] = mapped_column(Float, nullable=True) #Establish baseline income for allocations and insights.
    
    income_date_range: Mapped[Optional[IncomeDateRange]] = mapped_column(
        SqlEnum(IncomeDateRange, name="income_date_range_enum"), nullable=True
    ) #For scheduling reminders, resetting budgets, or prompting the user to plan.
    
    income_stablity: Mapped[bool] = mapped_column(Boolean, default=False) #Helps determine how conservative to be when suggesting budget allocations.


    # Secondary Income (optional)
    has_other_income: Mapped[bool] = mapped_column(Boolean, default=False) #Detect multiple income streams for total inflow calculation.
    other_income_source: Mapped[Optional[IncomeSource]] = mapped_column(
        SqlEnum(IncomeSource, name="other_income_source_enum"), nullable=True)
    other_income_monthly_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    other_income_frequency: Mapped[Optional[IncomeFrequency]] = mapped_column(
        SqlEnum(IncomeFrequency, name="other_income_frequency_enum"), nullable=True
    )
    
    #expenses
    has_fixed_deductable: Mapped[bool] = mapped_column(Boolean, default=False)
    fixed_deductable_amount: Mapped[float] = mapped_column(Float, nullable=True) #Identify deductions like rent, tithe, savings, or transfers that occur before spending.
    
    #savings
    user_saves: Mapped[bool] = mapped_column(Boolean, default=False)
    savings_amount: Mapped[float] = mapped_column(Float, nullable=True) #Understand saving habits and recommend appropriate strategies.
    
    # mode_of_payment: Mapped[str] = mapped_column(String, nullable=False) #Determines tracking method (manual entry vs. linked account or image receipt).
    
    # Future-Proofing for Budgeting
    total_estimated_monthly_income: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String, default="NGN", nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)  # e.g. if confirmed via transactions

    # Relationship
    user: Mapped["User"] = relationship("User", backref="financial_profile")



class Upload(BaseModel):
    __tablename__ = "uploads"

    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.whatsapp_phone_number"), nullable=False
    )
    upload_type: Mapped[str] = mapped_column(
        String, default="receipt", nullable=False
    )  # or "bank_statement"
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        String, default="pending", nullable=False
    )  # "processed", "pending", "failed"
    extracted_transactions: Mapped[List[Any]] = mapped_column(
        JSON, default=list
    )  # references to transactions
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", backref="uploads")

    def __repr__(self) -> str:
        return (
            f"<Upload(id={self.id!r}, user_id={self.user_id!r}, upload_type={self.upload_type!r}, "
            f"file_path={self.file_path!r}, status={self.status!r}, uploaded_at={self.uploaded_at!r})>"
        )
        


class Transaction(BaseModel):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.whatsapp_phone_number"), nullable=False
    )
    amount: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)  # "expense" or "income"
    category: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String, nullable=True, default="WhatsApp")
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", backref="transactions")

    def __repr__(self) -> str:
        return (
            f"<Transaction(id={self.id!r}, user_id={self.user_id!r}, amount={self.amount!r}, "
            f"type={self.type!r}, category={self.category!r}, timestamp={self.timestamp!r})>"
        )
