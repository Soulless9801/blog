import sys
from PyQt5 import QtWidgets, QtCore
from google.cloud import firestore
from google.oauth2 import service_account
creds = service_account.Credentials.from_service_account_file(
    'service_account.json'
)
db = firestore.Client(credentials=creds)

class PlannerApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blog Post Interface")
        self.resize(600, 800)

        vbox = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        vbox.addLayout(form)

        self.doc_id_input = QtWidgets.QLineEdit()
        self.title_input = QtWidgets.QLineEdit()
        self.body_input = QtWidgets.QPlainTextEdit()
        self.status_label = QtWidgets.QLabel()
        self.save_btn = QtWidgets.QPushButton("Save / Update")
        self.load_btn = QtWidgets.QPushButton("Load by ID")

        form.addRow("Document ID", self.doc_id_input)
        form.addRow("Title", self.title_input)
        form.addRow("Body", self.body_input)
        form.addRow("", self.save_btn)
        form.addRow("", self.load_btn)
        vbox.addWidget(self.status_label)

        self.save_btn.clicked.connect(self.save_document)
        self.load_btn.clicked.connect(self.load_document)

    def save_document(self):
        data = { 'title': self.title_input.text(), 'body': self.body_input.toPlainText() }
        doc_id = self.doc_id_input.text().strip()

        if not ''.join(data['title'].split(' ')) or not ''.join(data['body'].split(' ')):
            self.status_label.setText("Empty title or body")
            return

        try:
            if doc_id:
                data['updated'] = firestore.SERVER_TIMESTAMP
                db.collection('posts').document(doc_id).set(data, merge=True)
                self.status_label.setText(f"Updated document “{doc_id}”.")
            else:
                existing = db.collection('posts').where('title', '==', data['title']).get()
                if existing:
                    self.status_label.setText("Title must be unique. Another post already uses this title.")
                    return
                data['timestamp'] = firestore.SERVER_TIMESTAMP
                data['updated'] = firestore.SERVER_TIMESTAMP
                doc_ref = db.collection('posts').add(data)
                new_id = doc_ref[1].id
                self.doc_id_input.setText(new_id)
                self.status_label.setText(f"Created new doc with ID “{new_id}”.")
        except Exception as e:
            self.status_label.setText(f"Error: {e}")

    def load_document(self):
        doc_id = self.doc_id_input.text().strip()
        if not doc_id:
            self.status_label.setText("Please enter a Document ID to load.")
            return

        try:
            doc = db.collection('posts').document(doc_id).get()
            if doc.exists:
                self.title_input.setText(doc.to_dict().get('title'))
                self.body_input.setPlainText(doc.to_dict().get('body'))
                self.status_label.setText(f"Loaded document “{doc_id}”.")
            else:
                self.status_label.setText(f"No document found at “{doc_id}”.")
        except Exception as e:
            self.status_label.setText(f"Error: {e}")

# ——— Run App ———
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    planner = PlannerApp()
    planner.show()
    sys.exit(app.exec_())
