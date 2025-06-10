import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import json # Added for handling JSON from environment variable

# --- Configuration ---
# It's HIGHLY recommended to load these from environment variables
# for security and flexibility, especially in production.

# SPREADSHEET_ID: The ID of your Google Sheet.
# You can find this in the URL of your spreadsheet:
# https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit
SPREADSHEET_ID = os.environ.get('GOOGLE_SHEET_ID', '1lYDvQkHjT6KYLas9yp1Da08wIz3Oef_OLFsYKf7twh0')

# SHEET_NAME: The name of the specific tab/sheet within your spreadsheet.
SHEET_NAME = os.environ.get('GOOGLE_SHEET_TAB_NAME', 'Sheet1')

# SCOPES: Defines the permissions your service account needs.
# For writing to a sheet, 'https://www.googleapis.com/auth/spreadsheets' is typically sufficient.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# --- Service Account Credentials ---
# Load service account credentials securely.
# Option 1: From a file (good for local development, but avoid in production if possible)
# Option 2: From an environment variable (recommended for production deployments)

SERVICE_ACCOUNT_FILE = 'service_account.json' # Default fallback for local testing

def get_credentials():
    """
    Attempts to load credentials from an environment variable first,
    then falls back to a local file.
    """
    service_account_info = os.environ.get('GOOGLE_SERVICE_ACCOUNT_INFO')
    if service_account_info:
        try:
            # Parse the JSON string from the environment variable
            info = json.loads(service_account_info)
            credentials = service_account.Credentials.from_service_account_info(
                info, scopes=SCOPES
            )
            print("✅ Credentials loaded from environment variable.")
            return credentials
        except json.JSONDecodeError as e:
            print(f"❌ Error decoding GOOGLE_SERVICE_ACCOUNT_INFO JSON: {e}")
            print("Attempting to load from service_account.json file instead.")
    
    # Fallback to loading from a file if environment variable is not set or malformed
    if os.path.exists(SERVICE_ACCOUNT_FILE):
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        print(f"✅ Credentials loaded from {SERVICE_ACCOUNT_FILE}.")
        return credentials
    else:
        raise FileNotFoundError(
            f"❌ Service account file '{SERVICE_ACCOUNT_FILE}' not found, "
            "and GOOGLE_SERVICE_ACCOUNT_INFO environment variable is not set or invalid."
        )

# Initialize credentials globally or pass them around
try:
    credentials = get_credentials()
except (FileNotFoundError, Exception) as e:
    print(f"Fatal error initializing Google Sheet credentials: {e}")
    # In a real application, you might want to exit or log this more severely
    credentials = None # Set to None to indicate failure

def append_to_sheet(data: dict) -> dict:
    """
    Appends a new row of data to the specified Google Sheet.

    Args:
        data (dict): A dictionary containing the form submission data.
                     Expected keys: 'Full Name', 'Email Address', 'Phone Number'.

    Returns:
        dict: The result of the Google Sheets API append operation.
    """
    if not credentials:
        print("❌ Cannot append to sheet: Credentials not initialized.")
        return {"status": "error", "message": "Google Sheet credentials not loaded."}

    print("📤 Calling Google Sheets API to append data...")

    try:
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()

        # Ensure the order of columns matches your sheet and expected data keys
        # You can add a timestamp here if desired.
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        values = [[
            data.get('Full Name', ''),      # Use .get() with a default for robustness
            data.get('Email Address', ''),
            data.get('Phone Number', ''),
            timestamp # Adding a timestamp column
        ]]

        body = {'values': values}

        # Range 'A:D' (or 'A:E' if you add a timestamp) should cover all columns you're writing to.
        # If adding timestamp, range becomes 'A:E'
        append_range = f"{SHEET_NAME}!A:E" # Updated range to include timestamp column

        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=append_range,
            valueInputOption='USER_ENTERED', # USER_ENTERED parses dates, numbers correctly
            body=body
        ).execute()

        print(f"✅ Data appended successfully. Updates: {result.get('updates', {})}")
        return {"status": "success", "result": result}

    except Exception as e:
        print(f"❌ Error appending to Google Sheet: {e}")
        return {"status": "error", "message": str(e)}

# --- Example Usage (for local testing) ---
# This part will only run if you execute this script directly
# (i.e., python googlesheet.py)
if __name__ == '__main__':
    # --- IMPORTANT: FOR LOCAL TESTING ONLY ---
    # Make sure you have a 'service_account.json' file in the same directory
    # or set the GOOGLE_SERVICE_ACCOUNT_INFO environment variable correctly.
    # Also, set GOOGLE_SHEET_ID and GOOGLE_SHEET_TAB_NAME environment variables
    # or update them directly in the script for testing.

    print("\n--- Running Google Sheet Test ---")
    test_data = {
        'Full Name': 'John Doe',
        'Email Address': 'john.doe@example.com',
        'Phone Number': '123-456-7890'
    }

    print(f"Attempting to append test data: {test_data}")
    response = append_to_sheet(test_data)
    print("Test Result:", response)

    print("\n--- Running Google Sheet Test with missing data ---")
    test_data_incomplete = {
        'Full Name': 'Jane Smith',
        'Email Address': 'jane.smith@example.com',
        # Phone Number is missing
    }
    print(f"Attempting to append incomplete test data: {test_data_incomplete}")
    response_incomplete = append_to_sheet(test_data_incomplete)
    print("Incomplete Test Result:", response_incomplete)
