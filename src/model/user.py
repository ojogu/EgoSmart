from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON
from src.base.model import BaseModel
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import relationship, Mapped, mapped_column



class User(BaseModel):
    __tablename__ = 'users'

    #from whatsapp
    whatsapp_phone_number: Mapped[str] = mapped_column(String, unique=True, nullable=False, primary_key=True)
    whatsapp_profile_name: Mapped[str] = mapped_column(String, nullable=True)
    
    #from google
    email: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True, nullable=True)
    google_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email_verified: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    oauth_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    picture: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    google_refresh_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    google_access_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    mono_account_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, unique=True)
    



    def __repr__(self) -> str:
        return (
            f"<User(id={self.id!r}, whatsapp_phone_number={self.whatsapp_phone_number!r}, email={self.email!r}, "
            f"first_name={self.first_name!r}, last_name={self.last_name!r})>"
        )

    # def to_dict(self) -> Dict[str, Any]:
    #     return {
    #         "id": self.id,
    #         "whatsapp_phone_number": self.whatsapp_phone_number,
    #         "country_name": self.country_name,
    #         "country_code": self.country_code,
    #         "email": self.email,
    #         "google_id": self.google_id,
    #         "email_verified": self.email_verified,
    #         "oauth_verified": self.oauth_verified,
    #         "picture": self.picture,
    #         "first_name": self.first_name,
    #         "last_name": self.last_name,
    #         "onboarded": self.onboarded,
    #         "refresh_token": self.refresh_token,
    #         "access_token": self.access_token,
    #         "created_at": self.created_at.isoformat() if self.created_at else None,
    #         "updated_at": self.updated_at.isoformat() if self.updated_at else None,
    #     }

class BvnStatus(str):
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
class Profile(BaseModel):
    ''' handles the user profile from mono, links to the user table using whatsapp num as fk (mono lookup)'''
        #user data from mono bvn verification
    profile_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, primary_key=True, autoincrement=True)
    bvn_verified: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    middle_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    dob: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone_number_2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    state_of_origin: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    registration_date: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    lga_of_origin: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    lga_of_residence: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    marital_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    watch_listed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    photo_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    #relationship to the user_id
    user_id: Mapped[str] = mapped_column(String, ForeignKey('users.whatsapp_phone_number'), nullable=False)
    user: Mapped["User"] = relationship("User", backref="profile")


class BanKDetails(BaseModel):
    '''store bank details gotten from mono'''

    __tablename__ = 'bank_details'

    account_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    account_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    account_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    account_designation: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bank_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    branch_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    bank_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user_id: Mapped[str] = mapped_column(String, ForeignKey('users.whatsapp_phone_number', ondelete="CASCADE"), nullable=False)
    user: Mapped["User"] = relationship("User", backref="bank_details")

    # def to_dict(self) -> Dict[str, Any]:
    #     return {
    #         "id": self.id,
    #         "user_id": self.user_id,
    #         "session_id": self.session_id,
    #         "messages": self.messages,
    #         "created_at": self.created_at.isoformat() if self.created_at else None,
    #         "active": self.active,
    #         "agent_name": self.agent_name,
    #         "state": self.state,
    #     }


class Transaction(BaseModel):
    __tablename__ = 'transactions'

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey('users.whatsapp_phone_number'), nullable=False)
    amount: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)  # "expense" or "income"
    category: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String, nullable=True, default="WhatsApp")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user: Mapped["User"] = relationship("User", backref="transactions")

    def __repr__(self) -> str:
        return (
            f"<Transaction(id={self.id!r}, user_id={self.user_id!r}, amount={self.amount!r}, "
            f"type={self.type!r}, category={self.category!r}, timestamp={self.timestamp!r})>"
        )

    # def to_dict(self) -> Dict[str, Any]:
    #     return {
    #         "id": self.id,
    #         "user_id": self.user_id,
    #         "amount": self.amount,
    #         "type": self.type,
    #         "category": self.category,
    #         "description": self.description,
    #         "source": self.source,
    #         "timestamp": self.timestamp.isoformat() if self.timestamp else None,
    #         "logged_at": self.logged_at.isoformat() if self.logged_at else None,
    #     }
    
class IntentsLog(BaseModel):
    __tablename__ = 'intents_log'

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey('users.whatsapp_phone_number'), nullable=False)
    raw_message: Mapped[str] = mapped_column(String, nullable=False)
    detected_intent: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    entities: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user: Mapped["User"] = relationship("User", backref="intents_logs")

    def __repr__(self) -> str:
        return (
            f"<IntentsLog(id={self.id!r}, user_id={self.user_id!r}, raw_message={self.raw_message!r}, "
            f"detected_intent={self.detected_intent!r}, timestamp={self.timestamp!r})>"
        )

    # def to_dict(self) -> Dict[str, Any]:
    #     return {
    #         "id": self.id,
    #         "user_id": self.user_id,
    #         "raw_message": self.raw_message,
    #         "detected_intent": self.detected_intent,
    #         "entities": self.entities,
    #         "timestamp": self.timestamp.isoformat() if self.timestamp else None,
    #     }
        
        
        


class Upload(BaseModel):
    __tablename__ = 'uploads'

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey('users.whatsapp_phone_number'), nullable=False)
    upload_type: Mapped[str] = mapped_column(String, default="receipt", nullable=False)  # or "bank_statement"
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False)  # "processed", "pending", "failed"
    extracted_transactions: Mapped[List[Any]] = mapped_column(JSON, default=list)  # references to transactions
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

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
