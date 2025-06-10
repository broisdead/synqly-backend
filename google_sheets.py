import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import json

# --- Configuration ---
# IMPORTANT: Replace 'YOUR_GOOGLE_SPREADSHEET_ID_HERE' with your actual Google Sheet ID.
# This ID can be found in the URL of your spreadsheet:
# https://docs.google.com/spreadsheets/d/YOUR_GOOGLE_SPREADSHEET_ID_HERE/edit
SPREADSHEET_ID = os.environ.get('GOOGLE_SHEET_ID', 'YOUR_GOOGLE_SPREADSHEET_ID_HERE')

# The name of the specific tab/sheet within your spreadsheet (e.g., 'Sheet1', 'Form Responses').
SHEET_NAME = os.environ.get('GOOGLE_SHEET_TAB_NAME', 'Sheet1')

# Defines the permissions your service account needs.
# 'https://www.googleapis.com/auth/spreadsheets' allows read/write access.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_credentials():
    """
    Attempts to load Google Service Account credentials.
    It prioritizes loading from the 'GOOGLE_SERVICE_ACCOUNT_INFO' environment variable,
    which is the secure and recommended method for production deployments (like Render).
    As a fallback for local development, it can load from a 'service_account.json' file
    if present in the same directory (but this file should NOT be in your GitHub repo).
    """
    service_account_info_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_INFO')
    
    if service_account_info_json:
        try:
            # Attempt to parse the JSON string from the environment variable
            info = json.loads(service_account_info_json)
            credentials = service_account.Credentials.from_service_account_info(
                info, scopes=SCOPES
            )
            print("✅ Credentials loaded from GOOGLE_SERVICE_ACCOUNT_INFO environment variable.")
            return credentials
        except json.JSONDecodeError as e:
            print(f"❌ Error decoding GOOGLE_SERVICE_ACCOUNT_INFO JSON: {e}. Please check its format.")
        except Exception as e:
            print(f"❌ Unexpected error loading credentials from env var: {e}")
        
    # Fallback for local development if environment variable is not set or invalid
    SERVICE_ACCOUNT_FILE_LOCAL = 'service_account.json'
    if os.path.exists(SERVICE_ACCOUNT_FILE_LOCAL):
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE_LOCAL, scopes=SCOPES
        )
        print(f"✅ Credentials loaded from local '{SERVICE_ACCOUNT_FILE_LOCAL}' file.")
        return credentials
    else:
        # If neither method works, raise an error
        raise FileNotFoundError(
            f"❌ Could not load Google Service Account credentials. "
            f"Ensure 'GOOGLE_SERVICE_ACCOUNT_INFO' environment variable is set correctly "
            f"OR '{SERVICE_ACCOUNT_FILE_LOCAL}' exists for local development."
        )

# Initialize credentials globally when the module is imported.
# This will attempt to load them from environment variables (on Render) or a local file (for local testing).
try:
    credentials = get_credentials()
except Exception as e:
    print(f"🛑 Fatal error during Google Sheet credential initialization: {e}")
    # In a production app, you might want to log this and ensure the app doesn't proceed
    credentials = None # Set to None to prevent calls without valid credentials

def append_to_sheet(data: dict) -> dict:
    """
    Appends a new row of data to the specified Google Sheet.
    This function expects specific keys in the 'data' dictionary, matching your frontend.

    Args:
        data (dict): A dictionary containing the form submission data.
                     Expected keys: 'Full Name', 'Email Address', 'Phone Number', 'Identity'.

    Returns:
        dict: A dictionary indicating the status ('success' or 'error') and a message/result.
    """
    if not credentials:
        print("❌ Cannot append to sheet: Google Sheet credentials are not initialized.")
        return {"status": "error", "message": "Google Sheet credentials not loaded or invalid."}
    
    if SPREADSHEET_ID == 'YOUR_GOOGLE_SPREADSHEET_ID_HERE' or not SPREADSHEET_ID:
        print("❌ SPREADSHEET_ID is not configured. Please set it in your environment variables or directly in the code.")
        return {"status": "error", "message": "Google Sheet ID is not configured."}

    print("📤 Attempting to call Google Sheets API to append data...")

    try:
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()

        # Generate a timestamp for when the submission occurred
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Construct the row of values.
        # The order of these .get() calls should EXACTLY match the order of columns
        # you want in your Google Sheet (e.g., Column A, B, C, D, E).
        # Use .get(key, '') to prevent errors if a key is missing from the submitted data.
        values = [[
            data.get('Full Name', ''),      # Corresponds to Column A in your sheet
            data.get('Email Address', ''),  # Corresponds to Column B
            data.get('Phone Number', ''),   # Corresponds to Column C
            data.get('Identity', ''),       # Corresponds to Column D
            timestamp                       # Corresponds to Column E (added by backend)
        ]]

        # Define the range to append data. 'A:E' means from column A to E.
        # Adjust 'E' if you have more or fewer columns in your sheet for these entries.
        # For example, if you have 6 columns (A-F), it would be 'A:F'.
        append_range = f"{SHEET_NAME}!A:E"

        body = {'values': values}

        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=append_range,
            valueInputOption='USER_ENTERED', # USER_ENTERED correctly parses dates, numbers, etc.
            body=body
        ).execute()

        print(f"✅ Data successfully appended to Google Sheets. Updates: {result.get('updates', {})}")
        return {"status": "success", "result": result}

    except Exception as e:
        # Catch and log any exceptions that occur during the API call
        print(f"❌ Error occurred while appending to Google Sheet: {e}")
        return {"status": "error", "message": str(e)}

# --- Example Usage for Local Testing ---
# This block runs ONLY when you execute this file directly (e.g., `python google_sheets.py`)
# It's useful for verifying credential loading and sheet access locally.
if __name__ == '__main__':
    print("\n--- Running Google Sheets Module Local Test ---")
    
    # For local testing, ensure:
    # 1. You have a `service_account.json` file in the same directory.
    # 2. You've replaced 'YOUR_GOOGLE_SPREADSHEET_ID_HERE' with your actual ID.
    # 3. Your service account has Editor access to the sheet.

    sample_form_data = {
        'Full Name': 'Jane Doe',
        'Email Address': 'jane.doe@example.com',
        'Phone Number': '987-654-3210',
        'Identity': 'Influencer'
    }

    print(f"Attempting to append sample data: {sample_form_data}")
    test_response = append_to_sheet(sample_form_data)
    print("Local Test Result:", test_response)
    
    if test_response.get("status") == "success":
        print("\n🎉 Local test appears successful! Check your Google Sheet.")
    else:
        print("\n⚠️ Local test failed. Review the error message above and ensure credentials/ID/permissions are correct.")
