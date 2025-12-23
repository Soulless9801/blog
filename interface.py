import sys
from PyQt5 import QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView
from google.cloud import firestore
from google.oauth2 import service_account

creds = service_account.Credentials.from_service_account_file(
    'service_account.json'
)
db = firestore.Client(credentials=creds)

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
                    margin: 0;
                    padding: 8px;
                    font-family: sans-serif;
                }
                .textParserBlock {
                    display: block;
                    margin-bottom: 1em;
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
                        (_, expr) => `<div class="math-block">\\[${expr.trim()}\\]</div>`
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
"""


class PlannerApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blog Post Interface")
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

        self.rendered_label = QtWidgets.QLabel("Rendered Markdown will appear here.")
        render_box.addRow(self.rendered_label)

        self.web = QWebEngineView()
        self.web.setHtml(HTML_TEMPLATE)
        self.web.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        render_box.addRow(self.web)


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

    def render_markdown(self):
        latex_str = self.body_input.toPlainText()
        # print("Rendering LaTeX:", latex_str)
        js = f"renderContent({latex_str!r});"
        self.web.page().runJavaScript(js)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    planner = PlannerApp()
    planner.show()
    sys.exit(app.exec_())
