import os
import json

from google.cloud import firestore
from google.oauth2 import service_account
from dotenv import load_dotenv

creds = service_account.Credentials.from_service_account_file(
    'service_account.json'
)
db = firestore.Client(credentials=creds)

load_dotenv()

LOCAL_PATH = os.getenv('LOCAL_PATH')

def load_document(doc_id):
    doc = db.collection('posts').document(doc_id).get()
    if doc.exists:
        return doc
    
def write_documents():
    docs = db.collection('posts').stream()
    docs = [{'id': doc.id, **doc.to_dict()} for doc in docs]
    docs = [{**doc, 'timestamp': doc['timestamp'].isoformat(), 'updated': doc['updated'].isoformat()} for doc in docs]
    with open(LOCAL_PATH, "w") as file:
        json.dump(docs, file, indent=4)

if __name__ == '__main__':
    write_documents()

