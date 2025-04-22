from datetime import datetime, timedelta
from typing import Dict, Optional
import time
from fastapi import HTTPException

class SyncStatus:
    def __init__(self):
        self.last_sync_time: Dict[str, datetime] = {}
        self.sync_in_progress: Dict[str, bool] = {}
        self.sync_errors: Dict[str, str] = {}
        self.rate_limit_window = timedelta(minutes=1)
        self.max_requests_per_window = 60  # Google Sheets API quota

    def can_sync(self, sync_type: str) -> bool:
        """Check if we can perform a sync based on rate limits"""
        if sync_type not in self.last_sync_time:
            return True
        
        time_since_last_sync = datetime.now() - self.last_sync_time[sync_type]
        return time_since_last_sync >= self.rate_limit_window

    def start_sync(self, sync_type: str) -> None:
        """Mark the start of a sync operation"""
        if self.sync_in_progress.get(sync_type, False):
            raise HTTPException(
                status_code=429,
                detail=f"{sync_type} sync already in progress"
            )
        
        if not self.can_sync(sync_type):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        self.sync_in_progress[sync_type] = True
        self.last_sync_time[sync_type] = datetime.now()

    def end_sync(self, sync_type: str, error: Optional[str] = None) -> None:
        """Mark the end of a sync operation"""
        self.sync_in_progress[sync_type] = False
        if error:
            self.sync_errors[sync_type] = error
        else:
            self.sync_errors.pop(sync_type, None)

    def get_sync_status(self, sync_type: str) -> Dict:
        """Get the current status of a sync operation"""
        return {
            "in_progress": self.sync_in_progress.get(sync_type, False),
            "last_sync": self.last_sync_time.get(sync_type),
            "error": self.sync_errors.get(sync_type),
            "can_sync": self.can_sync(sync_type)
        }

# Global sync status tracker
sync_status = SyncStatus() 