from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from utils.google_auth import get_google_flow
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()  # Remove prefix to handle callback at root level

@router.get("/auth/google")
async def google_auth():
    """Initiate Google OAuth flow"""
    flow = get_google_flow()
    auth_url, _ = flow.authorization_url(prompt='consent')
    return RedirectResponse(url=auth_url)

@router.get("/oauth2callback")
async def oauth2callback(request: Request):
    """Handle OAuth2 callback"""
    try:
        code = request.query_params.get('code')
        if not code:
            raise HTTPException(status_code=400, detail="No authorization code provided")
            
        flow = get_google_flow()
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Save the credentials
        with open('token.json', 'w') as token:
            token.write(credentials.to_json())
            
        # Redirect to sheets endpoint
        return RedirectResponse(url='/sheets/read')
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 