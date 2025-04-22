from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from typing import List, Dict
import os
from datetime import datetime
from models import Customer, Sale, Product
from sqlalchemy.orm import Session
import logging
from .google_auth import get_sheets_service

SPREADSHEET_ID = os.getenv('GOOGLE_SHEET_ID')
SHEET_RANGE = 'Sheet1!A1:K'  # Using Sheet1 as the default sheet name

class GoogleSheetsSync:
    def __init__(self):
        service_tuple = get_sheets_service()
        if isinstance(service_tuple, tuple):
            self.service, _ = service_tuple
        else:
            self.service = service_tuple

    def sync_to_sheets(self, customers: List[Dict]):
        """Sync customer data to Google Sheets"""
        try:
            if not self.service:
                self.service = get_sheets_service()
                if isinstance(self.service, tuple):
                    self.service, _ = self.service

            values = [
                ['ID', 'Name', 'Email', 'Phone', 'Address', 'City', 'State', 
                 'Country', 'Postal Code', 'Created At', 'Updated At']
            ]
            
            for customer in customers:
                values.append([
                    customer.id,
                    customer.name,
                    customer.email,
                    customer.phone,
                    customer.address,
                    customer.city,
                    customer.state,
                    customer.country,
                    customer.postal_code,
                    str(customer.created_at),
                    str(customer.updated_at)
                ])

            body = {
                'values': values
            }
            
            # Clear the existing content first
            self.service.spreadsheets().values().clear(
                spreadsheetId=SPREADSHEET_ID,
                range=SHEET_RANGE
            ).execute()
            
            # Update with new data
            self.service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=SHEET_RANGE,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logging.info(f"Successfully synced {len(customers)} customers to Google Sheets")
            
        except Exception as e:
            logging.error(f"Failed to sync to Google Sheets: {str(e)}")
            raise

    def sync_from_sheets(self, db: Session):
        """Sync customer data from Google Sheets to database"""
        try:
            if not self.service:
                self.service = get_sheets_service()
                if isinstance(self.service, tuple):
                    self.service, _ = self.service

            result = self.service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=SHEET_RANGE
            ).execute()
            
            values = result.get('values', [])
            if not values:
                logging.info("No data found in sheet")
                return
                
            # Skip the header row
            for row in values[1:]:
                if len(row) < 9:  # We need at least the basic customer fields
                    continue
                    
                customer_data = {
                    'name': row[1],
                    'email': row[2],
                    'phone': row[3],
                    'address': row[4],
                    'city': row[5],
                    'state': row[6],
                    'country': row[7],
                    'postal_code': row[8]
                }
                
                # Check for existing customer
                customer = db.query(Customer).filter(
                    Customer.email == customer_data['email']
                ).first()
                
                if customer:
                    # Update existing customer
                    for key, value in customer_data.items():
                        setattr(customer, key, value)
                else:
                    # Create new customer
                    customer = Customer(**customer_data)
                    db.add(customer)
                
            db.commit()
            logging.info(f"Successfully synced {len(values)-1} customers from Google Sheets")
            
        except Exception as e:
            db.rollback()
            logging.error(f"Failed to sync from Google Sheets: {str(e)}")
            raise 