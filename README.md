# Likwid.Ai ERP - Customer Management Module

A full-stack ERP module for manufacturing companies, featuring customer management and Google Sheets integration.

![image](https://github.com/user-attachments/assets/cba23441-96cd-47aa-abb9-afbc42bfb32a)

![image](https://github.com/user-attachments/assets/f001492f-8574-4450-9fce-887b22aaa1d7)

![image](https://github.com/user-attachments/assets/7e6037ce-8347-4c01-8cf2-2ad751ebc5fd)

## Data file used

[sample_customer_data.xlsx](https://github.com/user-attachments/files/19849164/sample_customer_data.xlsx)


## For problem statement-2

# -> Google sheet data
![image](https://github.com/user-attachments/assets/25c5cecb-279b-409d-9f4c-96e328746396)
# -> got printed when we update in the sheet and reload it
![image](https://github.com/user-attachments/assets/a82b8d6f-cf5a-4c87-85e0-7f4b7a1414aa)


## Features

### 1. Customer Management
- Upload customer lists via Excel/CSV
- Automatic duplicate detection and handling
- Customer dashboard with analytics:
  - Top 10 customers by geography
  - Top 10 customers by sales volume
  - Top 10 customers by most purchased product

### 2. Google Sheets Integration
- Bidirectional sync with Google Sheets
- Automatic updates when:
  - New customers are added
  - Existing customers are updated
  - Changes are made in the Google Sheet
- Duplicate handling maintained in both directions

## Setup Instructions

### Backend Setup
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file with:
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/oauth2callback
GOOGLE_SHEET_ID=your_sheet_id
```

4. Start the backend server:
```bash
uvicorn main:app --reload
```

### Frontend Setup
1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

## API Endpoints

### Customer Management
- `POST /customers/upload` - Upload customer list
- `GET /customers/top-by-geography` - Top customers by geography
- `GET /customers/top-by-sales` - Top customers by sales volume
- `GET /customers/top-by-products` - Top customers by product purchases

### Google Sheets Integration
- `GET /sheets/read` - Read and sync sheet data
- `POST /sheets/sync` - Force bidirectional sync
- `GET /sheets/status` - Check sync status

## Demonstration Steps

1. **Customer Upload**
   - Prepare an Excel/CSV file with customer data
   - Use the upload feature in the frontend
   - Verify data is stored in the database

2. **Dashboard Features**
   - View top customers by geography
   - View top customers by sales
   - View top customers by products

3. **Google Sheets Integration**
   - Connect to Google Sheets
   - Add/update customers in the system
   - Verify changes appear in the sheet
   - Make changes in the sheet
   - Verify changes sync back to the system

## Tech Stack
- Backend: Python, FastAPI, SQLAlchemy
- Frontend: React, JavaScript, HTML
- Database: SQLite
- Integration: Google Sheets API

## Excel File Format

The Excel file should contain the following columns:
- name
- email
- phone
- address
- city
- state
- country
- postal_code

## Development

- Backend code is in the root directory
- Frontend code is in the `frontend` directory
- Database is automatically created on first run 
