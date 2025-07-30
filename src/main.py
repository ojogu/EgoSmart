import logging
from fastapi import FastAPI
from src.utils.db import init_db, drop_db
from src.utils.redis import setup_redis
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from src.utils.config import Settings
# from utils.config import Settings 
from src.utils.config import logging_settings
from src.auth.auth import auth_route
from src.routes.whatsapp import whatsapp_route
from src.routes.finance import finance_router
from src.routes.google import google_route
from src.routes.whatsapp_flow import whatsapp_flow_route
from src.routes.template import template_route
from src.utils.exception import register_error_handlers
setup_logging = logging_settings.setup_logging

# import ssl
# print(ssl.OPENSSL_VERSION)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle event handler for the FastAPI application.

    This asynchronous function is called when the FastAPI application starts up
    and shuts down. It initializes the database on startup and performs cleanup
    on shutdown.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: This function yields control back to the application after startup.
    """
    # await drop_db()
    # print(f"db dropped")
    await setup_redis()
    print(f"redis initalized")
    
    await init_db()
    print(f"db initalized")
    yield
    
    # await init_indexes()
    # yield

    
try:
    setup_logging() #I initialised the logging configuration in config.py here. This ensures that all loggers in the app follow the pattern
    logger = logging.getLogger(__name__)
    logger.info("FastAPI application is starting...")
except Exception as e:
    print(f"Failed to set up logging: {e}")
    logger.error(f"Failed to set up logging: {e}")
    raise


app = FastAPI(
    title=Settings.PROJECT_NAME,
    version=Settings.PROJECT_VERSION,
    description=Settings.PROJECT_DESCRIPTION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(whatsapp_route)
app.include_router(auth_route)
app.include_router(google_route)
app.include_router(finance_router)
app.include_router(whatsapp_flow_route)
app.include_router(template_route)

register_error_handlers(app)

@app.get("/")
def index():
    return {
        "message": "egosmart API"
    }
    
@app.post("/dev/reset-db", include_in_schema=False)
async def reset_database():
    await drop_db()
    return {"status": "database reset"}
