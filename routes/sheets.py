from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from utils.google_auth import get_sheets_service
from utils.google_sheets_sync import GoogleSheetsSync, SHEET_RANGE
from database import get_db
from sqlalchemy.orm import Session
from models import Customer
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime

load_dotenv()

router = APIRouter(prefix="/sheets", tags=["sheets"])
sheets_sync = GoogleSheetsSync()

# Track last sync times
last_db_sync = datetime.now()
last_sheet_sync = datetime.now()

@router.get("/read")
async def read_sheet(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Read data from Google Sheet and sync with database"""
    try:
        if not os.getenv('GOOGLE_SHEET_ID'):
            raise HTTPException(status_code=500, detail="GOOGLE_SHEET_ID not configured")
            
        service_tuple = get_sheets_service()
        if isinstance(service_tuple, tuple):
            service, auth_url = service_tuple
        else:
            service = service_tuple
            auth_url = None
            
        if not service:
            return RedirectResponse(url=auth_url) if auth_url else HTTPException(status_code=401, detail="Authentication required")
            
        # Sync from sheets to database
        sheets_sync.sync_from_sheets(db)
        
        # Get updated data
        result = service.spreadsheets().values().get(
            spreadsheetId=os.getenv('GOOGLE_SHEET_ID'),
            range=SHEET_RANGE
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return JSONResponse(content={"message": "No data found in sheet"}, status_code=200)
            
        return JSONResponse(content={"data": values}, status_code=200)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync")
async def force_sync(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Force a bidirectional sync between database and sheets"""
    try:
        # Sync from sheets to database
        sheets_sync.sync_from_sheets(db)
        
        # Get all customers from database
        customers = db.query(Customer).all()
        
        # Sync from database to sheets
        sheets_sync.sync_to_sheets(customers)
        
        return {"message": "Sync completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def sync_status():
    """Get the current sync status"""
    return {
        "last_db_sync": last_db_sync.isoformat(),
        "last_sheet_sync": last_sheet_sync.isoformat()
    } 