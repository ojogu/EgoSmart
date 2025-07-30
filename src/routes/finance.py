import json
from fastapi import Request, APIRouter, Response
from src.schemas.finance import MonoWebhook, Account_linking_Initiate
from src.schemas.request_schemas import BvnVerificationRequest, MetaFlowOnboarding
import logging
from src.service.finance import MonoService
from src.service.user import UserService
from src.utils.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
import base64
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("src/logs/finance.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
logger.propagate = False

finance_router = APIRouter(prefix="/finance")

def get_user_service(db: AsyncSession = Depends(get_session)):
    return UserService(db=db)

def get_mono_service(db: AsyncSession = Depends(get_session)):
    return MonoService(db=db)


@finance_router.post("/webhook")
async def webhook_handler(request: MonoWebhook):
    logger.info(f"Webhook received: {request}")
    return {"message": "verified"} 

@finance_router.post("/initate-linking")
async def initiate_linking(data:Account_linking_Initiate, mono_service:MonoService = Depends(get_mono_service)):
    account_link = await mono_service.linking_account_initation(**data.model_dump())
    logger.info(account_link)
    return JSONResponse(content={"msg": "working"})

@finance_router.post("/verify-bvn")
async def verify_bvn(data:BvnVerificationRequest, financial_service:MonoService = Depends(get_mono_service)):
    #fetch the user details from whatsapp flow
    verify = await financial_service.verify_bvn(bvn=data.bvn, whatsapp_phone_number=data.whatsapp_phone_number)
    logger.info(verify)

@finance_router.get("/bank-details")
async def fetch_bank_details(mono_service:MonoService = Depends(get_mono_service)):
    bank_details = await mono_service.bank_details()
    # logger.info(bank_details)
    return JSONResponse(content=bank_details)

