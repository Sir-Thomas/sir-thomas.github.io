import json
import os
import firebase_admin
from firebase_admin import credentials, firestore

# Load credentials
cred_path = ""
for item in os.listdir("./creds"):
    cred_path = os.path.join("./creds", item)
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Load jobs data from data.js (assumes valid JSON format after export)
with open("jobs.json", "r") as f:
    jobs_json = f.read()

# Convert JS object to valid JSON
jobs = json.loads(jobs_json)

# Upload each job to Firestore
for job_name, job_data in jobs.items():
    db.collection("jobs").document(job_name).set(job_data)

print("Upload complete.")