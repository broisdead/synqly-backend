from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from google_sheets import append_to_sheet # Make sure google_sheets.py is in the same directory or accessible via PYTHONPATH

app = Flask(__name__)
# Enable CORS for all origins, allowing your GitHub Pages form to submit data.
# For production, consider restricting origins to your specific GitHub Pages URL.
CORS(app)

@app.route('/', methods=['GET'])
def home():
    """
    Simple route to confirm the Flask backend is running.
    """
    return "Flask backend for Google Sheets integration is live!"

@app.route('/submit', methods=['POST'])
def submit():
    """
    Receives form data via a POST request and appends it to Google Sheets.
    """
    if not request.is_json:
        # This handles cases where the frontend might send data not as JSON.
        # It's good practice to ensure the request content type is 'application/json'.
        print("❌ Received non-JSON request.")
        return jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400

    data = request.json
    print("📩 Received form data:", data) # Debug log for incoming data

    # --- Data Validation (Highly Recommended) ---
    # Add validation to ensure essential fields are present and correctly formatted
    required_fields = ['Full Name', 'Email Address'] # Adjust based on your form's crucial fields
    for field in required_fields:
        if field not in data or not data[field]:
            print(f"❌ Missing or empty required field: {field}")
            return jsonify({'status': 'error', 'message': f"Missing or empty required field: '{field}'"}), 400

    try:
        # Call the append_to_sheet function from your google_sheets.py
        result = append_to_sheet(data)

        if result.get("status") == "success":
            print("✅ Data successfully appended to Google Sheets.")
            return jsonify({'status': 'success', 'message': 'Data saved to Google Sheets'}), 200
        else:
            # If append_to_sheet returns an error status
            error_message = result.get("message", "Unknown error when appending to sheet.")
            print("❌ Error from Google Sheets module:", error_message)
            return jsonify({'status': 'error', 'message': error_message}), 500

    except Exception as e:
        # Catch any unexpected errors during the process
        print("❌ Unexpected error during sheet update:", str(e))
        return jsonify({'status': 'error', 'message': f"An internal server error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # Get the port from environment variable (for Render deployment) or default to 5000
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Flask app starting on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=True) # debug=True is good for development, disable in production
