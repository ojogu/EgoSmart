private_key = "live_pk_bsv2harbox6nwtz4l2q4"
secret_key = "live_sk_i3ws71i6zglmf76ovtry"  # This is actually the secret key

import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import httpx
import uvicorn
import logging
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)
app = FastAPI(title="Mono API Client", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class Customer(BaseModel):
    name: str
    email: str

class Meta(BaseModel):
    ref: str

class MonoInitiateRequest(BaseModel):
    customer: Customer
    meta: Meta
    scope: str
    redirect_url: str

class MonoInitiateResponse(BaseModel):
    # Add response fields based on Mono API documentation
    status: str = None
    message: str = None
    data: dict = None

@app.get("/")
async def root():
    return {"message": "Mono API Client Server"}

@app.post("/webhook")
async def webhook_handler(data: dict):
    logger.info(f"Webhook received: {data}")
    return {"message": "Webhook received successfully", "data": data}

@app.get("/redirect", response_class=HTMLResponse)
async def handle_redirect(request: Request, code: str = None, error: str = None, state: str = None):
    """
    Handle Mono redirect after account linking with HTML response
    """
    logger.info(f"Redirect received - code: {code}, error: {error}, state: {state}")
    
    # Get all query parameters for debugging
    query_params = dict(request.query_params)
    
    if error:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Account Linking Failed</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .error {{ color: #d32f2f; background: #ffebee; padding: 15px; border-radius: 4px; margin: 20px 0; }}
                .params {{ background: #f5f5f5; padding: 15px; border-radius: 4px; margin: 20px 0; }}
                pre {{ white-space: pre-wrap; word-wrap: break-word; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>❌ Account Linking Failed</h1>
                <div class="error">
                    <strong>Error:</strong> {error}
                </div>
                <div class="params">
                    <strong>All Parameters:</strong>
                    <pre>{query_params}</pre>
                </div>
                <p>Please try linking your account again.</p>
            </div>
        </body>
        </html>
        """
        return html_content
    
    if code:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Account Linking Successful</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .success {{ color: #2e7d32; background: #e8f5e8; padding: 15px; border-radius: 4px; margin: 20px 0; }}
                .code {{ background: #f5f5f5; padding: 15px; border-radius: 4px; margin: 20px 0; font-family: monospace; }}
                .params {{ background: #f0f0f0; padding: 15px; border-radius: 4px; margin: 20px 0; }}
                pre {{ white-space: pre-wrap; word-wrap: break-word; }}
                .copy-btn {{ background: #1976d2; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; }}
                .copy-btn:hover {{ background: #1565c0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✅ Account Linking Successful!</h1>
                <div class="success">
                    Your bank account has been successfully linked to Mono.
                </div>
                
                <h3>Authorization Code:</h3>
                <div class="code">
                    <code id="auth-code">{code}</code>
                    <button class="copy-btn" onclick="copyCode()">Copy Code</button>
                </div>
                
                {f'<p><strong>State:</strong> {state}</p>' if state else ''}
                
                <div class="params">
                    <strong>All Parameters Received:</strong>
                    <pre>{query_params}</pre>
                </div>
                
                <h3>Next Steps:</h3>
                <ul>
                    <li>Use this authorization code to exchange for an account token</li>
                    <li>The code can be used to fetch account details, transactions, etc.</li>
                    <li>Store this code securely for future API calls</li>
                </ul>
            </div>
            
            <script>
                function copyCode() {{
                    const code = document.getElementById('auth-code').textContent;
                    navigator.clipboard.writeText(code).then(function() {{
                        alert('Code copied to clipboard!');
                    }});
                }}
            </script>
        </body>
        </html>
        """
        return html_content
    
    # Default response when no specific parameters
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mono Redirect Endpoint</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .info {{ color: #1976d2; background: #e3f2fd; padding: 15px; border-radius: 4px; margin: 20px 0; }}
            .params {{ background: #f5f5f5; padding: 15px; border-radius: 4px; margin: 20px 0; }}
            pre {{ white-space: pre-wrap; word-wrap: break-word; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔗 Mono Redirect Endpoint</h1>
            <div class="info">
                This endpoint is ready to receive authorization callbacks from Mono.
            </div>
            
            <div class="params">
                <strong>Current Parameters:</strong>
                <pre>{query_params}</pre>
            </div>
            
            <p>After a successful account linking, this page will display the authorization code and next steps.</p>
        </div>
    </body>
    </html>
    """
    return html_content

@app.post("/initiate-mono-account")
async def initiate_mono_account():
    """
    Initiate a Mono account connection
    """
    
    # Request payload
    payload = {
        "customer": {
            "name": "Nkang Precious Ojogu",
            "email": "nkangprecious26@gmail.com"
        },
        "meta": {"ref": "99008877TEST"},
        "scope": "auth",
        "redirect_url": "https://cfdba769bba2.ngrok-free.app/redirect"
    }
    
    # Headers - using the correct secret key
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "mono-sec-key": secret_key  # Changed from private_key to secret_key
    }
    
    # Make async HTTP request
    async with httpx.AsyncClient() as client:
        try:
            print(f"Making request with payload: {payload}")
            print(f"Using secret key: {secret_key[:20]}...")  # Only show first 20 chars for security
            
            response = await client.post(
                "https://api.withmono.com/v2/accounts/initiate",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
            
            # Check if request was successful
            if response.status_code == 200:
                return {
                    "status": "success",
                    "status_code": response.status_code,
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "status_code": response.status_code,
                    "error": response.text,
                    "debug_info": {
                        "payload": payload,
                        "headers_sent": {k: v for k, v in headers.items() if k != "mono-sec-key"}
                    }
                }
                
        except httpx.TimeoutException:
            raise HTTPException(status_code=408, detail="Request timeout")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/initiate-mono-custom")
async def initiate_mono_custom(request: MonoInitiateRequest):
    """
    Initiate Mono account with custom data
    """
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "mono-sec-key": secret_key  # Changed from private_key to secret_key
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Fixed: Use model_dump() instead of model_dump_json() and pass dict to json parameter
            payload = request.model_dump()
            
            response = await client.post(
                "https://api.withmono.com/v2/accounts/initiate",
                json=payload,  # Changed from request.model_dump_json()
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "status_code": response.status_code,
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "status_code": response.status_code,
                    "error": response.text,
                    "debug_info": {
                        "payload": payload,
                        "headers_sent": {k: v for k, v in headers.items() if k != "mono-sec-key"}
                    }
                }
                
        except httpx.TimeoutException:
            raise HTTPException(status_code=408, detail="Request timeout")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mono-api-client"}

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "monotest:app",  # Change this to your filename if different
        host="0.0.0.0",
        port=3000,
        reload=True,
        log_level="info"
    )