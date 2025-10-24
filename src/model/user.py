from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String,  Enum as SqlEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref
from enum import Enum
from src.base.model import BaseModel

class PrimaryIncomeSource(Enum):
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

class Status(Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    SUCCESS = "successful"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    PARTIAL = "partial"
    
    NOT_LINKED = "not linked"
    LINKED_PENDING = "linking pending"
    LINKED = "Linked"

class User(BaseModel):

    # from whatsapp
    whatsapp_phone_number: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, primary_key=True, index=True
    )
    whatsapp_profile_name: Mapped[str] = mapped_column(String, nullable=True)

    email: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    country_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # One-to-one relationship to google table
    google: Mapped["GoogleAccount"] = relationship(
        "GoogleAccount", backref=backref("user", uselist=False)
    )
    # One-to-one relationship to account linking
    account_link: Mapped["AccountLinking"] = relationship(
        "AccountLinking", backref=backref("user", uselist=False)
    )




class GoogleAccount(BaseModel):
    whatsapp_phone_number: Mapped[str] = mapped_column(
        String, ForeignKey("users.whatsapp_phone_number")
    )

    google_id: Mapped[str] = mapped_column(String, nullable=False)
    email_verified: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    oauth_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    picture: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    google_refresh_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    google_access_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class AccountLinking(BaseModel):
    __tablename__ = "account_linkings"

    # from the initiation response
    reference: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)  # "ref"
    customer_id: Mapped[Optional[str]] = mapped_column(String, unique=True)  # "customer"


    # from the webhook events
    mono_id: Mapped[Optional[str]] = mapped_column(String, unique=True)  # "id" or "_id" from webhook
    event: Mapped[Optional[str]] = mapped_column(String)  # "mono.events.account_connected" etc.

    # institution info
    bank_name: Mapped[Optional[str]] = mapped_column(String)
    bank_code: Mapped[Optional[str]] = mapped_column(String)
    account_type: Mapped[Optional[str]] = mapped_column(String)  # e.g. SAVINGS_ACCOUNT
    account_number: Mapped[Optional[str]] = mapped_column(String)
    balance: Mapped[Optional[int]] = mapped_column(Integer)
    account_name: Mapped[Optional[str]] = mapped_column(String)
    currency: Mapped[Optional[str]] = mapped_column(String)
    bvn: Mapped[Optional[str]] = mapped_column(String)
    auth_method: Mapped[Optional[str]] = mapped_column(String)
    external_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # optional — useful to store extra fields like retrieved_data
    meta: Mapped[Optional[dict]] = mapped_column(JSONB)

    status: Mapped[Status] = mapped_column(
        SqlEnum(Status, name="status_enum"), default=Status.PENDING, nullable=False
    )
    
    linking_status: Mapped[Status] = mapped_column(
        SqlEnum(Status, name="linking_enum"), default=Status.NOT_LINKED, nullable=False
    ) #for the agent to know if account linking status, pending, failed, success
    
    data_status: Mapped[Status] = mapped_column(
        SqlEnum(Status, name="data_status_enum"), default=Status.PENDING, nullable=False
    ) #from mono to fetch data status of transaction etc

    failed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        # default=lambda: datetime.now(timezone.utc),
        nullable=True
    )
    
    failure_reason: Mapped[String] = mapped_column(String(), nullable=True)
    # relationship to user
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.whatsapp_phone_number"), nullable=False
    )




class Budgeting(BaseModel):
    """store budgeting details"""
    pass 

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
    primary_income_source: Mapped[Optional[PrimaryIncomeSource]] = mapped_column(
        SqlEnum(PrimaryIncomeSource, name="primary_income_source_enum"), nullable=True
    )
    income_frequency: Mapped[Optional[IncomeFrequency]] = mapped_column(
        SqlEnum(IncomeFrequency, name="income_frequency_enum"), nullable=True
    )
    monthly_income: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    income_date_range: Mapped[Optional[IncomeDateRange]] = mapped_column(
        SqlEnum(IncomeDateRange, name="income_date_range_enum"), nullable=True
    )

    # Secondary Income (optional)
    has_other_income: Mapped[bool] = mapped_column(Boolean, default=False)
    other_income_monthly_amount: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    other_income_frequency: Mapped[Optional[IncomeFrequency]] = mapped_column(
        SqlEnum(IncomeFrequency, name="other_income_frequency_enum"), nullable=True
    )

    # Future-Proofing for Budgeting
    total_estimated_monthly_income: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    currency: Mapped[str] = mapped_column(String, default="NGN", nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)  # e.g. if confirmed via transactions

    # Relationship
    user: Mapped["User"] = relationship("User", backref="financial_profile")


class BanKDetails(BaseModel):
    """store bank details gotten from mono"""

    __tablename__ = "bank_details"

    account_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    account_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    account_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    account_designation: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    bank_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    branch_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    bank_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # created_at: Mapped[datetime] = mapped_column(
    #     DateTime(timezone=True),
    #     default=lambda: datetime.now(timezone.utc),
    #     nullable=False,
    # )

    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.whatsapp_phone_number", ondelete="CASCADE"),
        nullable=False,
    )
    user: Mapped["User"] = relationship("User", backref="bank_details")


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





class Upload(BaseModel):
    __tablename__ = "uploads"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
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

    # def to_dict(self) -> Dict[str, Any]:
    #     return {
    #         "id": self.id,
    #         "user_id": self.user_id,
    #         "upload_type": self.upload_type,
    #         "file_path": self.file_path,
    #         "status": self.status,
    #         "extracted_transactions": self.extracted_transactions,
    #         "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
    #     }


# class Profile(BaseModel):
#     ''' handles the user profile from mono, links to the user table using whatsapp num as fk (mono lookup)'''
#         #user data from mono bvn verification
#     profile_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, primary_key=True, autoincrement=True)
#     bvn_verified: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
#     first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     last_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     middle_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     dob: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     phone_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     phone_number_2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     gender: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     state_of_origin: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     registration_date: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     lga_of_origin: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     lga_of_residence: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     marital_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     watch_listed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
#     photo_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

#     #relationship to the user_id
#     user_id: Mapped[str] = mapped_column(String, ForeignKey('users.whatsapp_phone_number'), nullable=False)
#     user: Mapped["User"] = relationship("User", backref="profile")
