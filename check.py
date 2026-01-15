from google.cloud import firestore
from google.oauth2 import service_account

creds = service_account.Credentials.from_service_account_file(
    'service_account.json'
)

db = firestore.Client(credentials=creds)

def check_collection(collection_name): # check if collection exists
    collections = db.collections()
    for collection in collections:
        if collection.id == collection_name:
            return True
    return False

def load_documents(collection_name): # load all documents from collection
    if not check_collection(collection_name):
        return None
    docs = db.collection(collection_name).stream()
    return [{'id': doc.id, **doc.to_dict()} for doc in docs]

def load_document(collection_name, document_id): # load document from collection
    doc = db.collection(collection_name).document(document_id).get()
    if not doc.exists:
        return None
    return doc.to_dict()

def update_document(collection_name, document_id, data): # update document in collection
    doc = load_document(collection_name, document_id)
    if doc is None:
        return False
    db.collection(collection_name).document(document_id).set(data, merge=True)
    return True

def create_document(collection_name, data): # create new document in collection
    if not check_collection(collection_name):
        return False
    return db.collection(collection_name).add(data)

def require_fields(dict, fields):
    for field in fields:
        if field not in dict:
            return False
    return True