from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/submit-form', methods=['POST'])
def submit_form():
    data = request.json
    with open('submissions.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), data['name'], data['email'], data['phone'], data['identity']])
    return jsonify({"message": "Form submitted successfully"}), 200

@app.route('/')
def home():
    return 'Flask backend is live!'
