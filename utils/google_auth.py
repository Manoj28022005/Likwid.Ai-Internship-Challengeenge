from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import json
from pathlib import Path

load_dotenv()

# Google OAuth2 configuration
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_google_flow():
    """Create and return a Google OAuth2 flow instance"""
    return Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI],
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

def get_credentials(token_path='token.json', auth_code=None):
    """Get or refresh Google API credentials"""
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = get_google_flow()
            if auth_code:
                # Use provided authorization code
                flow.fetch_token(code=auth_code)
                creds = flow.credentials
            else:
                # Return authorization URL if no code provided
                auth_url, _ = flow.authorization_url(prompt='consent')
                return None, auth_url
        
        # Save the credentials for future use
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return creds, None

def get_sheets_service(auth_code=None):
    """Get Google Sheets service instance"""
    creds, auth_url = get_credentials(auth_code=auth_code)
    if not creds:
        return None, auth_url
    return build('sheets', 'v4', credentials=creds), None

def get_drive_service(auth_code=None):
    """Get Google Drive service instance"""
    creds, auth_url = get_credentials(auth_code=auth_code)
    if not creds:
        return None, auth_url
    return build('drive', 'v3', credentials=creds), None 