import requests
import time
from typing import Dict, List

BASE_URL = "http://localhost:8000"

def test_sheets_to_db_sync():
    """Test syncing data from Google Sheets to database"""
    print("\nTesting Google Sheets to Database Sync")
    print("=" * 50)
    
    # Step 1: Get current customers from database
    print("\n1. Getting current customers from database")
    response = requests.get(f"{BASE_URL}/customers/all")
    initial_customers = response.json()
    print(f"Initial customer count: {len(initial_customers)}")
    
    # Step 2: Trigger manual sync from sheets
    print("\n2. Triggering manual sync from sheets")
    response = requests.post(f"{BASE_URL}/customers/sync-sheets")
    print(f"Sync Response: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Step 3: Wait for sync to complete
    print("\n3. Waiting for sync to complete")
    time.sleep(5)  # Give more time for the sync to complete
    
    # Step 4: Check sync status
    print("\n4. Checking sync status")
    response = requests.get(f"{BASE_URL}/customers/sync-status")
    print(f"Sync Status: {response.json()}")
    
    # Step 5: Get updated customers from database
    print("\n5. Getting updated customers from database")
    response = requests.get(f"{BASE_URL}/customers/all")
    updated_customers = response.json()
    print(f"Updated customer count: {len(updated_customers)}")
    
    # Step 6: Compare changes
    print("\n6. Comparing changes")
    initial_emails = {c["email"] for c in initial_customers}
    updated_emails = {c["email"] for c in updated_customers}
    
    new_customers = updated_emails - initial_emails
    removed_customers = initial_emails - updated_emails
    
    print(f"New customers added: {len(new_customers)}")
    print(f"Customers removed: {len(removed_customers)}")
    
    if new_customers:
        print("\nNew customers:")
        for email in new_customers:
            customer = next(c for c in updated_customers if c["email"] == email)
            print(f"- {customer['name']} ({email})")
    
    if removed_customers:
        print("\nRemoved customers:")
        for email in removed_customers:
            print(f"- {email}")

def main():
    try:
        test_sheets_to_db_sync()
        print("\nAll tests completed!")
    except Exception as e:
        print(f"\nError during testing: {str(e)}")

if __name__ == "__main__":
    main() 