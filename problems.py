import sys
import argparse

from PyQt5 import QtWidgets, QtCore
from google.cloud import firestore
from google.oauth2 import service_account

parser = argparse.ArgumentParser(description='Firestore Interface')
parser.add_argument('--collection', type=str, help='collection name')
args = parser.parse_args()

creds = service_account.Credentials.from_service_account_file(
    'service_account.json'
)
db = firestore.Client(credentials=creds)

class SolutionEditorApp(QtWidgets.QWidget):
    def __init__(self, collection):
        super().__init__()

        self.collection = collection

        self.setWindowTitle("Firestore Interface")
        self.resize(1200, 800)

        hbox = QtWidgets.QHBoxLayout(self)
        form = QtWidgets.QFormLayout()
        hbox.addLayout(form)

        self.doc_id_input = QtWidgets.QLineEdit()

        self.language_input = QtWidgets.QComboBox() # change to dropdown?
        self.language_input.addItems(['python', 'cpp', 'java'])
        self.language_input.currentTextChanged.connect(self.highlight_code)

        self.body_input = QtWidgets.QPlainTextEdit()
        self.status_label = QtWidgets.QLabel()
        self.save_btn = QtWidgets.QPushButton("Save / Update")
        self.load_btn = QtWidgets.QPushButton("Load by ID")

        self.highlight_timer = QtCore.QTimer(self)
        self.highlight_timer.setInterval(1000)  # 1 second
        self.highlight_timer.setSingleShot(True)
        self.highlight_timer.timeout.connect(self.highlight_code)

        self.body_input.setTabStopWidth(4 * self.body_input.fontMetrics().width(' '))
        self.body_input.textChanged.connect(self.start_highlight_timer)

        self.last_updated = None

        form.addRow("Document ID", self.doc_id_input)
        form.addRow("Language", self.language_input)
        form.addRow("Code", self.body_input)
        form.addRow("", self.save_btn)
        form.addRow("", self.load_btn)
        form.addRow("", self.status_label)

        self.save_btn.clicked.connect(self.save_document)
        self.load_btn.clicked.connect(self.load_document)

        highlight_box = QtWidgets.QFormLayout()
        hbox.addLayout(highlight_box)

        self.highlighted_label = QtWidgets.QLabel("Highlighted Code Below")

        self.code_viewer = QtWidgets.QTextEdit()
        self.code_viewer.setReadOnly(True)
        self.code_viewer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)        

        highlight_box.addRow(self.highlighted_label)
        highlight_box.addRow(self.code_viewer)

    def save_document(self):
        data = { 'submission': self.body_input.toPlainText(), 'language': self.language_input.currentText() }
        doc_id = self.doc_id_input.text().strip()

        if not ''.join(data['submission'].split(' ')):
            self.status_label.setText("Empty code") # all whitespace or nothing
            return

        try:
            if doc_id:
                data['updated'] = firestore.SERVER_TIMESTAMP
                db.collection(self.collection).document(doc_id).set(data, merge=True)
                self.status_label.setText(f"Updated document “{doc_id}”.")
            else:
                data['created'] = firestore.SERVER_TIMESTAMP
                data['updated'] = firestore.SERVER_TIMESTAMP
                doc_ref = db.collection(self.collection).add(data)
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
            doc = db.collection(self.collection).document(doc_id).get()
            if doc.exists:
                doc_dict = doc.to_dict()
                self.body_input.setPlainText(doc_dict.get('submission').encode('utf-8').decode('unicode_escape'))
                self.language_input.setCurrentText(doc_dict.get('language', 'python'))
                self.status_label.setText(f"Loaded document “{doc_id}”.")
            else:
                self.status_label.setText(f"No document found at “{doc_id}”.")
        except Exception as e:
            self.status_label.setText(f"Error: {e}")
    
    def start_highlight_timer(self):
        self.highlight_timer.start()

    def highlight_code(self):

        code = self.body_input.toPlainText()
        language = self.language_input.currentText()

        import subprocess
        try:
            result = subprocess.run(
                ['node', 'highlight.js', code, language],
                capture_output=True,
                text=True,
                check=True
            )
            self.code_viewer.setHtml(result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error during highlighting:", e.stderr)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    solution_editor_app = SolutionEditorApp(collection=args.collection)
    solution_editor_app.show()
    sys.exit(app.exec_())
