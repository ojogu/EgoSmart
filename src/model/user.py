from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String,  Enum as SqlEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref
from enum import Enum
from src.base.model import BaseModel



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
