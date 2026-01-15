import sys
import argparse
from PyQt5 import QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView
from google.cloud import firestore

from check import check_collection, create_document, load_document, update_document, require_fields

parser = argparse.ArgumentParser(description='Firestore Interface')
parser.add_argument('--collection', type=str, help='collection name')
parser.add_argument('--theme', type=str, choices=['light', 'dark'], default='light', help='css theme')
args = parser.parse_args()

theme = args.theme

HTML_TEMPLATE = r"""
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="utf-8" />
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.css">
            <script src="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/contrib/auto-render.min.js"></script>

            <style>
                body {
                    font-family: Arial, sans-serif;
                    color: %s;
                    background-color: %s;
                    transition: background-color 0.3s, color 0.3s;
                }
                .textParserBlock {
                    display: block;
                    margin-bottom: 1em;
                }
                a {
                    color: %s;
                    text-decoration: none;
                    transition: background-color 0.3s, color 0.3s;
                }
                a:hover {
                    color: %s;
                }
            </style>
        </head>

        <body>
            <div id="content"></div>

            <script>

                function parseNewlines(text) {
                    return text
                    .split('\\n')
                    .map(p => `<p class="textParserBlock">${p}</p>`)
                    .join("");
                }

                function parseBlockMath(html) {
                    return html.replace(
                        /\$\$([\s\S]+?)\$\$/g,
                        (_, expr) => `<div>\\[${expr.trim()}\\]</div>`
                    );
                }

                function parseInlineMath(html) {
                    return html.replace(
                        /\$(.+?)\$/g,
                        (_, expr) => `\\(${expr}\\)`
                    );
                }

                function parseTextDecorations(html) {
                    return html
                    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
                    .replace(/\*(.+?)\*/g, "<em>$1</em>")
                    .replace(/__(.+?)__/g, "<u>$1</u>");
                }

                function parseLinks(html) {
                    return html.replace(
                        /\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g,
                        '<a href="$2" target="_blank">$1</a>'
                    );
                }

                function parseMarkdown(text) {
                    let html = text;
                    html = parseNewlines(html);
                    html = parseBlockMath(html);
                    html = parseInlineMath(html);
                    html = parseTextDecorations(html);
                    html = parseLinks(html);
                    return html;
                }

                function renderContent(text) {
                    const container = document.getElementById("content");
                    container.innerHTML = parseMarkdown(text);

                    renderMathInElement(container, {
                        delimiters: [
                            {left: "\\[", right: "\\]", display: true},
                            {left: "\\(", right: "\\)", display: false}
                        ]
                    });
                }
            </script>
        </body>
    </html>
""" % (
    '#252525' if theme == 'light' else '#ffffff',
    '#f9f5f1' if theme == 'light' else '#212529',
    '#252525' if theme == 'light' else '#ffffff',
    '#898989' if theme == 'light' else '#9b9b9b',
)


class CollectionEditorApp(QtWidgets.QWidget):
    def __init__(self, collection):
        super().__init__()

        self.collection = collection

        self.setWindowTitle("Firestore Interface")
        self.resize(1200, 800)

        hbox = QtWidgets.QHBoxLayout(self)
        form = QtWidgets.QFormLayout()
        hbox.addLayout(form)

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
        form.addRow("", self.status_label)

        self.save_btn.clicked.connect(self.save_document)
        self.load_btn.clicked.connect(self.load_document)

        self.body_input.textChanged.connect(self.render_markdown)

        render_box = QtWidgets.QFormLayout()
        hbox.addLayout(render_box)

        self.rendered_label = QtWidgets.QLabel("Rendered Body Markdown Below")
        render_box.addRow(self.rendered_label)

        self.web = QWebEngineView()
        self.web.setHtml(HTML_TEMPLATE)
        self.web.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        render_box.addRow(self.web)


    def save_document(self):
        data = { 'title': self.title_input.text(), 'body': self.body_input.toPlainText().replace("\n\n", "\n\\n\n") }
        doc_id = self.doc_id_input.text().strip()

        if not ''.join(data['title'].split(' ')) or not ''.join(data['body'].split(' ')):
            self.status_label.setText("Empty title or body")
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
            self.status_label.setText(f"Created new doc with ID \"{new_id}\"")

    def load_document(self):
        doc_id = self.doc_id_input.text().strip()
        if not doc_id:
            self.status_label.setText("Please enter a Document ID to load.")
            return

        doc_dict = load_document(self.collection, doc_id)

        if doc_dict is None:
            self.status_label.setText(f"\"{doc_id}\" does not exist")
            return
        
        if not require_fields(doc_dict, ['title', 'body']):
            self.status_label.setText(f"\"{doc_id}\" is missing required fields")
            return
        
        self.title_input.setText(doc_dict.get('title'))
        self.body_input.setPlainText(doc_dict.get('body').replace("\n\\n\n", "\n\n"))
        self.status_label.setText(f"Loaded document \"{doc_id}\"")

    def render_markdown(self):
        latex_str = self.body_input.toPlainText().replace("\n\n", "\n\\n\n")
        js = f"renderContent({latex_str!r});"
        self.web.page().runJavaScript(js)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    if not check_collection(args.collection):
        print(f"\"{args.collection}\" does not exist.")
        sys.exit(1)
    collection_editor_app = CollectionEditorApp(collection=args.collection)
    collection_editor_app.show()
    sys.exit(app.exec_())
