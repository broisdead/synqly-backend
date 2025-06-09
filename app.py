from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "Flask backend is live!"

@app.route('/submit-form', methods=['POST'])
def submit_form():
    data = request.json
    with open('submissions.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), data.get('name'), data.get('email'),
                         data.get('phone'), data.get('identity')])
    return jsonify({"message": "Form submitted successfully"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
from flask import Flask, request, jsonify
from flask_cors import CORS
from google_sheets import append_to_sheet  # ✅ make sure this line is not failing

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "Flask backend is live!"

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    print("📩 Received form data:", data)  # 🔍 Debug log

    try:
        result = append_to_sheet(data)
        print("✅ Google Sheets updated:", result)  # 🔍 Add success log
        return jsonify({'status': 'success', 'message': 'Data saved to Google Sheets'})
    except Exception as e:
        print("❌ Error updating Google Sheets:", str(e))  # 🔍 Add error log
        return jsonify({'status': 'error', 'message': str(e)})
