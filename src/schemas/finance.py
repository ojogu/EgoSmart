from pydantic import BaseModel, EmailStr, Field
from typing import Any, Dict, List, Optional
from enum import Enum
from src.utils.config import config

#===========initating linking of account=========

# Utility function to transform the raw flat payload into the required structure
def format_account_linking_payload(first_name: str, last_name: str, email: EmailStr, meta_ref: str):
    return {
        "customer": {
            "name": f"{first_name} {last_name}",
            "email": email
        },
        "scope": "auth",
        "meta": {
            "ref": meta_ref
        },
        "redirect_url": config.REDIRECT_URL,
   
    }

class FlatAccountRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number:str
    
class Customer(BaseModel):
    name: str
    email: EmailStr
    
class InstiutionData(BaseModel):
    id: str
    auth_method: str  

class Meta(BaseModel):
    ref: Optional[str] = None


class AccountlinkingInitiate(BaseModel):
    customer: Customer
    # institution: Optional[InstiutionData] = None
    scope: str  = "auth"
    meta: Optional[Meta] = None
    redirect_url:str =  config.REDIRECT_URL,


class AccountLinkingResponseData(BaseModel):
    mono_url: str
    customer: str
    meta: Meta
    scope: str
    redirect_url: str
    created_at: str

class AccountLinkingResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    data: AccountLinkingResponseData




# ============Webhook================
class Institution(BaseModel):
    name: Optional[str]
    bankCode: Optional[str]
    type: Optional[str]

class AccountInfo(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: Optional[str]
    accountNumber: Optional[str]
    currency: Optional[str]
    balance: Optional[int]
    type: Optional[str]
    bvn: Optional[str]
    authMethod: Optional[str]
    institution: Optional[Institution]
    created_at: Optional[str]
    updated_at: Optional[str]
    
    class Config:
        populate_by_name = True
        
class MetaInfo(BaseModel):
    ref: Optional[str]
    data_status: Optional[str]
    auth_method: Optional[str]
    retrieved_data: Optional[List[str]] = Field(default_factory=list)




#============different mono events, so we can do routing based on each event
class BaseMonoWebhook(BaseModel):
    event: str
    data: Dict[str, Any] #accept anything for now


class AccountConnectedEvent(BaseModel):
    id:str
    customer:str
    meta: dict | None = None
    

class AccountUpdatedEvent(BaseModel):
    account: AccountInfo
    meta: MetaInfo











class BvnVerification(BaseModel):
    bvn: str
    scope: Optional[str] = "identity"
    
class VerificationMethod(BaseModel):
    method: str
    hint: str

class BvnVerificationData(BaseModel):
    session_id: str
    methods: list[VerificationMethod]

class BvnVerificationResponse(BaseModel):  #response from the #initate bvn endpoint 
    status: str
    message: str
    data: BvnVerificationData
    
    

class VerificationMethod(str, Enum):
    phone = "phone"
    phone_1 = "phone_1"
    alternate_phone = "alternate_phone"
    email = "email"

class OtpVerification(BaseModel):
    method: VerificationMethod  # The verification method. sent from whatsapp
    phone_number: Optional[str] = None  # Required if method is "alternate_phone"

class OtpVerificationResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    data: Optional[dict] = None

#user details from mono
class BvnDetailsData(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    dob: str
    phone_number: str
    phone_number_2: Optional[str] = None
    email: Optional[EmailStr] = None
    gender: Optional[str] = None
    state_of_origin: Optional[str] = None
    bvn: str
    nin: Optional[str] = None
    registration_date: Optional[str] = None
    lga_of_origin: Optional[str] = None
    lga_of_Residence: Optional[str] = None
    marital_status: Optional[str] = None
    watch_listed: Optional[bool] = None
    photoId: Optional[str] = None


class BvnDetails(BaseModel):
    status: str
    message: str
    timestamp: str
    data: BvnDetailsData


#bank details from bvn verification
class Institution(BaseModel):
    name: str
    branch: str
    bank_code: str

class BvnBankAccount(BaseModel):
    account_name: str
    account_number: str
    account_type: str
    account_designation: str
    institution: Institution

class BvnBankDetails(BaseModel):
    status: str
    message: str
    timestamp: str
    data: list[BvnBankAccount]
    



    