from pydantic import BaseModel, EmailStr

class BvnVerificationRequest(BaseModel):
    bvn: str
    whatsapp_phone_number:str
    
class MetaFlowOnboarding(BaseModel):
    name: str
    email: EmailStr