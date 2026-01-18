import os
import sys
import json
import argparse

parser = argparse.ArgumentParser(description='Local Saving')
parser.add_argument('--collection', type=str, help='collection name')
parser.add_argument('--path', type=str, help='local path')
args = parser.parse_args()

from google.cloud import firestore
from google.oauth2 import service_account

from pages.check import check_collection, load_documents

creds = service_account.Credentials.from_service_account_file(
    'service_account.json'
)
db = firestore.Client(credentials=creds)

LOCAL_PATH = args.path
    
def write_documents():

    docs = load_documents(args.collection)

    if docs is None:
        print(f"\"{args.collection}\" collection does not exist.")
        return
    
    for doc in docs:
        for field in doc:
            if hasattr(doc[field], "isoformat"):
                doc[field] = doc[field].isoformat()

    with open(LOCAL_PATH, "w") as file:
        json.dump(docs, file, indent=4)

if __name__ == '__main__':
    if not check_collection(args.collection):
        print(f"\"{args.collection}\" collection does not exist.")
        sys.exit(1)
    if not os.path.exists(LOCAL_PATH) or os.path.isdir(LOCAL_PATH):
        print(f"Error: \"{LOCAL_PATH}\" is not a valid file path.")
        sys.exit(1)
    write_documents()

