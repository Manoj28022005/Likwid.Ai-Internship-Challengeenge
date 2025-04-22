from database import engine, SessionLocal
from models import Base, Customer, Product, Sale
from datetime import datetime

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Add sample data
    db = SessionLocal()
    try:
        # Check if we already have data
        if db.query(Customer).first() is None:
            # Add sample products
            products = [
                Product(name="Product A", description="Description A", price=100.0),
                Product(name="Product B", description="Description B", price=200.0),
                Product(name="Product C", description="Description C", price=300.0)
            ]
            db.add_all(products)
            db.commit()

            # Add sample customers
            customers = [
                Customer(
                    name="John Doe",
                    email="john.doe@example.com",
                    phone="1234567890",
                    address="123 Main St",
                    city="New York",
                    state="NY",
                    country="USA",
                    postal_code="10001"
                ),
                Customer(
                    name="Jane Smith",
                    email="jane.smith@example.com",
                    phone="9876543210",
                    address="456 Oak Ave",
                    city="Los Angeles",
                    state="CA",
                    country="USA",
                    postal_code="90001"
                )
            ]
            db.add_all(customers)
            db.commit()

            # Add sample sales
            sales = [
                Sale(
                    customer_id=1,
                    product_id=1,
                    quantity=5,
                    amount=500.0,
                    date=datetime.utcnow()
                ),
                Sale(
                    customer_id=1,
                    product_id=2,
                    quantity=3,
                    amount=600.0,
                    date=datetime.utcnow()
                ),
                Sale(
                    customer_id=2,
                    product_id=3,
                    quantity=2,
                    amount=600.0,
                    date=datetime.utcnow()
                )
            ]
            db.add_all(sales)
            db.commit()
    
    except Exception as e:
        print(f"Error initializing sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("Database tables created successfully!") 