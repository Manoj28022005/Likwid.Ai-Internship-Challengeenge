from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Dict
import pandas as pd
import logging
from database import get_db
from models import Customer, Sale, Product
from schemas import CustomerCreate, CustomerUpdate, CustomerResponse
from utils.google_sheets_sync import GoogleSheetsSync

router = APIRouter(prefix="/customers", tags=["customers"])
sheets_sync = GoogleSheetsSync()

def sync_to_sheets_background(customers):
    try:
        sheets_sync.sync_to_sheets(customers)
    except Exception as e:
        logging.error(f"Background sync to sheets failed: {str(e)}")

@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer: CustomerCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new customer and trigger sync"""
    try:
        db_customer = Customer(**customer.dict())
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        
        # Trigger automatic sync
        background_tasks.add_task(sheets_sync.trigger_automatic_sync, background_tasks, db)
        
        return db_customer
    except Exception as e:
        db.rollback()
        logging.error(f"Error in create_customer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Update a customer and trigger sync"""
    try:
        db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not db_customer:
            raise HTTPException(status_code=404, detail="Customer not found")
            
        for key, value in customer.dict(exclude_unset=True).items():
            setattr(db_customer, key, value)
            
        db.commit()
        db.refresh(db_customer)
        
        # Trigger automatic sync
        background_tasks.add_task(sheets_sync.trigger_automatic_sync, background_tasks, db)
        
        return db_customer
    except Exception as e:
        db.rollback()
        logging.error(f"Error in update_customer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Delete a customer and trigger sync"""
    try:
        db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not db_customer:
            raise HTTPException(status_code=404, detail="Customer not found")
            
        db.delete(db_customer)
        db.commit()
        
        # Trigger automatic sync
        background_tasks.add_task(sheets_sync.trigger_automatic_sync, background_tasks, db)
        
        return {"message": "Customer deleted successfully"}
    except Exception as e:
        db.rollback()
        logging.error(f"Error in delete_customer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sync-status")
async def get_sync_status():
    """Get the current sync status"""
    return sheets_sync.get_sync_status()

@router.post("/upload", response_model=List[CustomerResponse])
async def upload_customers(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(('.xlsx', '.csv')):
        raise HTTPException(status_code=400, detail="Only Excel (.xlsx) or CSV files are allowed")
    
    try:
        # Read the file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file.file)
        else:
            df = pd.read_excel(file.file)

        # Validate required columns
        required_columns = ["name", "email", "product_name", "quantity", "amount"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )

        customers = []
        # Process each row
        for _, row in df.iterrows():
            # Customer data
            customer_data = {
                "name": row["name"],
                "email": row["email"],
                "phone": str(row.get("phone", "")),
                "address": str(row.get("address", "")),
                "city": str(row.get("city", "")),
                "state": str(row.get("state", "")),
                "country": str(row.get("country", "")),
                "postal_code": str(row.get("postal_code", ""))
            }

            # Check for existing customer
            existing_customer = db.query(Customer).filter(Customer.email == customer_data["email"]).first()
            
            if existing_customer:
                # Update existing customer
                for key, value in customer_data.items():
                    setattr(existing_customer, key, value)
                customer = existing_customer
            else:
                # Create new customer
                customer = Customer(**customer_data)
                db.add(customer)
                db.flush()  # This will assign an ID to the customer

            # Handle product and sale
            product_name = str(row["product_name"])
            # Check for existing product
            product = db.query(Product).filter(Product.name == product_name).first()
            if not product:
                # Create new product if it doesn't exist
                product = Product(
                    name=product_name,
                    description=f"Description for {product_name}",
                    price=float(row["amount"]) / float(row["quantity"])
                )
                db.add(product)
                db.flush()

            # Create sale record
            sale = Sale(
                customer_id=customer.id,
                product_id=product.id,
                quantity=int(row["quantity"]),
                amount=float(row["amount"])
            )
            db.add(sale)
            
            if customer not in customers:
                customers.append(customer)

        db.commit()
        
        # Sync to Google Sheets in the background
        background_tasks.add_task(sync_to_sheets_background, customers)
        
        return customers
    
    except Exception as e:
        db.rollback()
        logging.error(f"Error in upload_customers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-by-geography")
def get_top_customers_by_geography(db: Session = Depends(get_db)):
    try:
        result = db.query(
            Customer.country,
            func.count(Customer.id).label('customer_count')
        ).group_by(
            Customer.country
        ).order_by(func.count(Customer.id).desc()).limit(10).all()
        
        return [{"country": r.country or "Unknown", "customer_count": r.customer_count} for r in result] or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-by-sales")
def get_top_customers_by_sales(db: Session = Depends(get_db)):
    try:
        result = db.query(
            Customer.name,
            func.coalesce(func.sum(Sale.amount), 0).label('total_sales')
        ).outerjoin(Sale).group_by(
            Customer.id,
            Customer.name
        ).order_by(func.sum(Sale.amount).desc()).limit(10).all()
        
        return [{"customer_name": r.name, "total_sales": float(r.total_sales)} for r in result] or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-by-products")
def get_top_customers_by_products(db: Session = Depends(get_db)):
    try:
        # First check if we have any sales data
        has_sales = db.query(Sale).first() is not None
        
        if not has_sales:
            # If no sales data, return customer names with 0 quantities
            customers = db.query(Customer).limit(10).all()
            return [{
                "customer_name": customer.name,
                "product_name": "No purchases yet",
                "total_quantity": 0
            } for customer in customers] or []
        
        # If we have sales data, proceed with the fixed query
        result = db.query(
            Customer.name.label('customer_name'),
            Product.name.label('product_name'),
            func.coalesce(func.sum(Sale.quantity), 0).label('total_quantity')
        ).select_from(Customer)\
         .join(Sale, Customer.id == Sale.customer_id)\
         .join(Product, Sale.product_id == Product.id)\
         .group_by(
            Customer.id,
            Customer.name,
            Product.id,
            Product.name
        ).order_by(func.sum(Sale.quantity).desc()).limit(10).all()
        
        return [{
            "customer_name": r.customer_name,
            "product_name": r.product_name or "No product",
            "total_quantity": int(r.total_quantity)
        } for r in result] or []
    except Exception as e:
        logging.error(f"Error in get_top_customers_by_products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all", response_model=List[CustomerResponse])
def get_all_customers(db: Session = Depends(get_db)):
    """Get all customers for testing purposes"""
    try:
        customers = db.query(Customer).all()
        return customers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync-sheets")
async def sync_with_sheets(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Manually trigger a sync with Google Sheets"""
    try:
        # First sync from sheets to database
        sheets_sync.sync_from_sheets(db)
        
        # Then sync from database to sheets
        customers = db.query(Customer).all()
        background_tasks.add_task(sync_to_sheets_background, customers)
        
        return {"message": "Sync initiated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
async def reset_data(db: Session = Depends(get_db)):
    """Clear all customer and sales data"""
    try:
        # Delete all sales first (due to foreign key constraints)
        db.query(Sale).delete()
        # Delete all products
        db.query(Product).delete()
        # Delete all customers
        db.query(Customer).delete()
        db.commit()
        return {"message": "All customer and sales data has been reset"}
    except Exception as e:
        db.rollback()
        logging.error(f"Error in reset_data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 