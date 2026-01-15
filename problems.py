import sys
import argparse
import subprocess

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWebEngineWidgets import QWebEngineView

from google.cloud import firestore

from check import check_collection, update_document, create_document, load_document, require_fields

parser = argparse.ArgumentParser(description='Firestore Interface')
parser.add_argument('--collection', type=str, help='collection name')
args = parser.parse_args()

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

        self.code_viewer = QWebEngineView()
        self.code_viewer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)        

        highlight_box.addRow(self.highlighted_label)
        highlight_box.addRow(self.code_viewer)

    def save_document(self):
        data = { 'submission': self.body_input.toPlainText(), 'language': self.language_input.currentText() }
        doc_id = self.doc_id_input.text().strip()

        if not ''.join(data['submission'].split(' ')):
            self.status_label.setText("Empty code") # all whitespace or nothing
            return

        if doc_id:
            data['updated'] = firestore.SERVER_TIMESTAMP
            update_document(self.collection, doc_id, data)
            self.status_label.setText(f"Updated \"{doc_id}\"")
        else:
            data['created'] = firestore.SERVER_TIMESTAMP
            data['updated'] = firestore.SERVER_TIMESTAMP
            new_id = create_document(self.collection, data)[1].id
            self.doc_id_input.setText(new_id)
            self.status_label.setText(f"Created \"{new_id}\"")

    def load_document(self):
        doc_id = self.doc_id_input.text().strip()

        if not doc_id:
            self.status_label.setText("Enter a Document ID")
            return

        doc_dict = load_document(self.collection, doc_id)

        if doc_dict is None:
            self.status_label.setText(f"\"{doc_id}\" does not exist.")
            return
        
        if not require_fields(doc_dict, ['submission', 'language']):
            self.status_label.setText(f"\"{doc_id}\" is missing required fields.")
            return

        self.body_input.setPlainText(doc_dict.get('submission').encode('utf-8').decode('unicode_escape'))
        self.language_input.setCurrentText(doc_dict.get('language', 'python'))
        self.status_label.setText(f"Loaded \"{doc_id}\".")
    
    def start_highlight_timer(self):
        self.highlight_timer.start()

    def highlight_code(self):

        code = self.body_input.toPlainText()
        language = self.language_input.currentText()

        result = subprocess.run(
            ['node', 'highlight.js', code, language],
            capture_output=True,
            text=True,
            check=True
        )

        # print(result.stdout)  # For debugging purposes

        html = f"""
            <html>
                <head>
                    <style>
                        body {{
                            tab-size: 4;
                            font-family: 'Fira Code', monospace;
                        }}
                    </style>
                </head>
                <body>
                    {result.stdout}
                </body>
            </html>
        """

        print(html)  # For debugging purposes

        self.code_viewer.setHtml(html)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    if not check_collection(args.collection):
        print(check_collection(args.collection))
        print(f"\"{args.collection}\" collection does not exist.")
        sys.exit(1)
    solution_editor_app = SolutionEditorApp(collection=args.collection)
    solution_editor_app.show()
    sys.exit(app.exec_())
