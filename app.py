from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from google_sheets import append_to_sheet # Ensure google_sheets.py is in the same directory

app = Flask(__name__)
# Enable CORS for all origins. In a production setting, you'd want to
# restrict this to your specific frontend domain (e.g., your GitHub Pages URL).
CORS(app)

@app.route('/', methods=['GET'])
def home():
    """
    Simple health check endpoint to confirm the Flask backend is running.
    """
    return "Flask backend for Google Sheets integration is live!"

@app.route('/submit', methods=['POST'])
def submit():
    """
    Receives JSON form data via a POST request and appends it to Google Sheets.
    Includes basic validation and robust error handling.
    """
    # Ensure the incoming request's Content-Type is application/json
    if not request.is_json:
        print("❌ Received non-JSON request. Content-Type header might be incorrect.")
        return jsonify({'status': 'error', 'message': 'Request must be JSON (Content-Type: application/json)'}), 400

    data = request.json
    print(f"📩 Received form data: {data}")

    # Basic server-side validation for required fields
    # Adjust these field names to exactly match what your frontend form sends
    # and what your google_sheets.py expects.
    required_fields = ['Full Name', 'Email Address'] # Example: ['Full Name', 'Email Address', 'Phone Number']
    for field in required_fields:
        if field not in data or not data[field]:
            print(f"❌ Missing or empty required field: '{field}'")
            return jsonify({'status': 'error', 'message': f"Missing or empty required field: '{field}'"}), 400

    try:
        # Call the function from your google_sheets.py to append data
        sheet_write_result = append_to_sheet(data)

        # Check the status returned by append_to_sheet
        if sheet_write_result.get("status") == "success":
            print("✅ Data successfully appended to Google Sheets.")
            return jsonify({'status': 'success', 'message': 'Data saved to Google Sheets'}), 200
        else:
            # Propagate error details from google_sheets.py
            error_detail = sheet_write_result.get("message", "An unknown error occurred in Google Sheets module.")
            print(f"❌ Error from Google Sheets module: {error_detail}")
            return jsonify({'status': 'error', 'message': f"Failed to save data: {error_detail}"}), 500

    except Exception as e:
        # Catch any unexpected errors that might occur during the process
        print(f"❌ Unexpected internal server error: {str(e)}")
        # Provide a generic error message to the client for security, log full error internally
        return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500

# This block is for local development only and will NOT be executed on Render
# when using a production WSGI server like Gunicorn.
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Flask app starting locally on http://0.0.0.0:{port}")
    # In a local development environment, set debug=True for auto-reloading and debugging.
    # NEVER use debug=True in a production environment.
    app.run(host='0.0.0.0', port=port, debug=True)
