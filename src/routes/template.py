from fastapi import APIRouter, HTTPException, Request, Response, Body, status
from fastapi.responses import JSONResponse
from src.service.templates import TemplateService

import logging
template_route = APIRouter(prefix="/whatsapp")
service = TemplateService()

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("src/logs/template.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
logger.propagate = False

@template_route.post("/templates", status_code=201)
async def create_template_endpoint(payload: dict = Body(...)):
    """
    Create a new WhatsApp template.
    """
    logger.info("Received request to create template with payload: %s", payload)
    try:
        result = await service.create_template(payload)
        logger.error(result)
        if "error" in result:
            logger.warning("Template creation failed: %s", result["error"])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        logger.info("Template created successfully: %s", result)
        return JSONResponse(content=result, status_code=201)
    except Exception as e:
        logger.error("Error creating template: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@template_route.get("/templates")
async def list_templates():
    logger.info("Received request to list templates")
    try:
        result = await service.list_templates()
        logger.info("Templates listed successfully")
        return JSONResponse(content=result)
    except Exception as e:
        logger.error("Error listing templates: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
@template_route.delete("/templates/{template_name}")
async def delete_template(template_name: str):
    logger.info("Received request to delete template: %s", template_name)
    try:
        result = await service.delete_template(template_name)
        logger.info("Template deleted successfully: %s", template_name)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error("Error deleting template '%s': %s", template_name, str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
@template_route.get("/templates/insights")
async def get_template_insights():
    logger.info("Received request to get template insights")
    try:
        result = await service.get_template_insights()
        logger.info("Template insights retrieved successfully")
        return JSONResponse(content=result)
    except Exception as e:
        logger.error("Error getting template insights: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))