import json
import argparse

parser = argparse.ArgumentParser(description='Local Saving')
parser.add_argument('--collection', type=str, help='collection name')
parser.add_argument('--path', type=str, help='local path')
args = parser.parse_args()

from google.cloud import firestore
from google.oauth2 import service_account

creds = service_account.Credentials.from_service_account_file(
    'service_account.json'
)
db = firestore.Client(credentials=creds)

LOCAL_PATH = args.path

def load_document(doc_id):
    doc = db.collection(args.collection).document(doc_id).get()
    if doc.exists:
        return doc
    
def write_documents():
    docs = db.collection(args.collection).stream()
    docs = [{'id': doc.id, **doc.to_dict()} for doc in docs]
    docs = [{**doc, 'created': doc['created'].isoformat(), 'updated': doc['updated'].isoformat()} for doc in docs]
    with open(LOCAL_PATH, "w") as file:
        json.dump(docs, file, indent=4)

if __name__ == '__main__':
    write_documents()

