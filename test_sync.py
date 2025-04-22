import requests
import json
import time
from typing import Dict, List

BASE_URL = "http://localhost:8000"

def test_customer_creation_and_sync():
    """Test creating a customer and verify sync to Google Sheets"""
    print("\n1. Testing Customer Creation and Sync")
    
    # Create a new customer
    customer_data = {
        "name": "Test Customer",
        "email": "test.customer@example.com",
        "phone": "1234567890",
        "address": "123 Test St",
        "city": "Test City",
        "state": "TS",
        "country": "Test Country",
        "postal_code": "12345"
    }
    
    response = requests.post(f"{BASE_URL}/customers/", json=customer_data)
    print(f"Create Customer Response: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Check sync status
    time.sleep(2)  # Wait for sync to complete
    response = requests.get(f"{BASE_URL}/customers/sync-status")
    print(f"\nSync Status: {response.json()}")

def test_customer_update_and_sync():
    """Test updating a customer and verify sync"""
    print("\n2. Testing Customer Update and Sync")
    
    # First get all customers to find the test customer
    response = requests.get(f"{BASE_URL}/customers/all")
    customers = response.json()
    test_customer = next((c for c in customers if c["email"] == "test.customer@example.com"), None)
    
    if not test_customer:
        print("Test customer not found")
        return
    
    # Update the customer
    update_data = {
        "name": "Updated Test Customer",
        "phone": "0987654321"
    }
    
    response = requests.put(
        f"{BASE_URL}/customers/{test_customer['id']}",
        json=update_data
    )
    print(f"Update Customer Response: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Check sync status
    time.sleep(2)
    response = requests.get(f"{BASE_URL}/customers/sync-status")
    print(f"\nSync Status: {response.json()}")

def test_manual_sync():
    """Test manual sync trigger"""
    print("\n3. Testing Manual Sync")
    
    response = requests.post(f"{BASE_URL}/customers/sync-sheets")
    print(f"Manual Sync Response: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Check sync status
    time.sleep(2)
    response = requests.get(f"{BASE_URL}/customers/sync-status")
    print(f"\nSync Status: {response.json()}")

def test_rate_limiting():
    """Test rate limiting functionality"""
    print("\n4. Testing Rate Limiting")
    
    # Try to trigger multiple syncs quickly
    for i in range(3):
        print(f"\nAttempt {i+1}:")
        response = requests.post(f"{BASE_URL}/customers/sync-sheets")
        print(f"Response Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 429:
            print("Rate limit hit as expected")
            break
            
        time.sleep(1)

def main():
    print("Starting Google Sheets Sync Tests")
    print("=" * 50)
    
    try:
        test_customer_creation_and_sync()
        test_customer_update_and_sync()
        test_manual_sync()
        test_rate_limiting()
        
        print("\nAll tests completed!")
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")

if __name__ == "__main__":
    main() 