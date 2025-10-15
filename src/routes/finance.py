
from fastapi import Request, APIRouter, Response
from fastapi.responses import JSONResponse
from src.schemas.finance import MonoWebhook
from src.service.finance import MonoService
from src.service.user import UserService
from src.utils.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from src.schemas.finance import AccountlinkingInitiate
from src.utils.log import setup_logger  # noqa: E402
logger = setup_logger(__name__, file_path="finance.log")

finance_router = APIRouter(prefix="/finance")

def get_user_service(db: AsyncSession = Depends(get_session)):
    return UserService(db=db)

def get_mono_service(db: AsyncSession = Depends(get_session)):
    return MonoService(db=db)


@finance_router.post("/webhook")
async def webhook_handler(request: Request):
    logger.info(f"Webhook received: {await request.json()}")
    return {"message": "verified"} 

@finance_router.post("/initate-linking")
async def initiate_linking(data:AccountlinkingInitiate, mono_service:MonoService = Depends(get_mono_service)):
    account_link = await mono_service.linking_account_initation(**data.model_dump())
    logger.info(account_link)
#     return JSONResponse(content={"msg": "working"})

@finance_router.get("/redirect-url")
async def redirect_url(status: str = None, reason: str = None):
    return JSONResponse(content={
        "msg": "working",
        "status": status,
        "reason": reason
    })


# @finance_router.post("/verify-bvn")
# async def verify_bvn(data:BvnVerificationRequest, financial_service:MonoService = Depends(get_mono_service)):
#     #fetch the user details from whatsapp flow
#     verify = await financial_service.verify_bvn(bvn=data.bvn, whatsapp_phone_number=data.whatsapp_phone_number)
#     logger.info(verify)

# @finance_router.get("/bank-details")
# async def fetch_bank_details(mono_service:MonoService = Depends(get_mono_service)):
#     bank_details = await mono_service.bank_details()
#     # logger.info(bank_details)
#     return JSONResponse(content=bank_details)

