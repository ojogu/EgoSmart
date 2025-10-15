from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from enum import Enum

#===========initating linking of account=========
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
    redirect_url:str =  "https://1828ebe0e0b2.ngrok-free.app/redirect-url"


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
    _id: Optional[str]
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

class MetaInfo(BaseModel):
    ref: Optional[str]
    data_status: Optional[str]
    auth_method: Optional[str]
    retrieved_data: Optional[List[str]] = []

class WebhookData(BaseModel):
    id: Optional[str]
    customer: Optional[str]
    account: Optional[AccountInfo]
    meta: Optional[MetaInfo] = Field(default_factory=MetaInfo)

class MonoWebhook(BaseModel):
    event: str
    data: WebhookData












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
    



    