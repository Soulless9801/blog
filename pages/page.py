from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWebEngineWidgets import QWebEngineView

from pages.check import check_collection, load_documents, create_document, load_document, update_document, get_timestamp

WIDGET_MAP = {
    'lineedit': QtWidgets.QLineEdit,
    'textedit': QtWidgets.QPlainTextEdit,
    'dropdown': QtWidgets.QComboBox
}

class CollectionEditorPage(QtWidgets.QWidget):

    collectionCreated = QtCore.pyqtSignal(object) # not this class's problem anymore

    def __init__(self, collection=None, doc_id=None, fields={}, theme='dark', title="Collection Editor"):
        super().__init__()

        # initialization
        self.theme = theme

        self.title = title

        self.resize(1200, 800)

        # field wrapper
        hbox = QtWidgets.QHBoxLayout(self)

        # fields
        form = QtWidgets.QFormLayout()
        hbox.addLayout(form, 1)

        # collection field
        self.collection_label = QtWidgets.QLineEdit()
        form.addRow("Collection", self.collection_label)

        # document ID field
        self.doc_id_input = QtWidgets.QComboBox()
        self.doc_id_input.setEditable(True)
        form.addRow("Document ID", self.doc_id_input)

        self.set_collection({ "id": collection, "doc_id": doc_id })

        self.fields = fields
        self.field_widgets = {}

        # other fields
        for field, config in fields.items():
            widget = self._create_widget(config)
            self.field_widgets[field] = widget
            form.addRow(config.get('label', field), widget)
        
        # save button
        self.save_btn = QtWidgets.QPushButton("Save / Update")
        form.addRow("", self.save_btn)
        self.save_btn.clicked.connect(self.save_document)

        # load button
        if self.collection: # if existing collection
            self.load_btn = QtWidgets.QPushButton("Load by ID")
            form.addRow("", self.load_btn)
            self.load_btn.clicked.connect(self.load_document)
        
        # status field
        self.status_label = QtWidgets.QLabel("")
        form.addRow("", self.status_label)

        # display
        render_box = QtWidgets.QFormLayout()
        hbox.addLayout(render_box, 1)

        # description
        self.rendered_label = QtWidgets.QLabel("Collection Type: " + title)
        render_box.addRow(self.rendered_label)

        # web view
        self.web = QWebEngineView()
        self.htmlLoaded = False

        self.web.loadFinished.connect(self.on_html_loaded)
        self.doc_id_input.activated.connect(self.load_document)

        self.web.setHtml(self.gen_html())
        self.web.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        render_box.addRow(self.web)

    def _create_widget(self, config):
        widget_type = config.get('type')
        WidgetClass = WIDGET_MAP.get(widget_type)

        widget = WidgetClass()

        if isinstance(widget, QtWidgets.QComboBox) and 'options' in config:
            widget.addItem("")
            widget.addItems(config['options'])

        if "on_change" in config:
            self._connect_change_signal(widget, config["on_change"])

        return widget

    def _connect_change_signal(self, widget, handler):
        if isinstance(widget, QtWidgets.QLineEdit):
            widget.textChanged.connect(handler)
        elif isinstance(widget, QtWidgets.QPlainTextEdit):
            widget.textChanged.connect(handler)
        elif isinstance(widget, QtWidgets.QComboBox):
            widget.currentTextChanged.connect(handler)
    
    def get_field_value(self, field):
        widget = self.field_widgets.get(field)
        if isinstance(widget, QtWidgets.QLineEdit):
            return widget.text()
        elif isinstance(widget, QtWidgets.QPlainTextEdit):
            return widget.toPlainText()
        elif isinstance(widget, QtWidgets.QComboBox):
            return widget.currentText()
        return ""

    def set_field_value(self, field, value):
        widget = self.field_widgets.get(field)
        if isinstance(widget, QtWidgets.QLineEdit):
            widget.setText(value)
        elif isinstance(widget, QtWidgets.QPlainTextEdit):
            widget.setPlainText(value)
        elif isinstance(widget, QtWidgets.QComboBox):
            widget.setCurrentText(value)

    def on_html_loaded(self):
        self.htmlLoaded = True
        self.load_document()

    def save_document(self):
        if not self.htmlLoaded:
            return
        
        col_id = self.collection if self.collection else self.collection_label.text().strip()

        if not col_id:
            self.status_label.setText("Please enter a collection title to create")
            return

        data = {}

        for field in self.field_widgets:
            data[field] = self.get_field_value(field)
            if not ''.join(data[field].split(' ')):
                self.status_label.setText(f"Field \"{field}\" is empty")
                return 

        doc_id = self.doc_id_input.currentText().strip()
        data['updated'] = get_timestamp()

        if not update_document(col_id, doc_id, data):
            data['created'] = get_timestamp()
            new_id = create_document(col_id, doc_id, data)
            self.doc_id_input.setCurrentText(new_id)
            self.status_label.setText(f"Created new doc with ID \"{new_id}\"")
            if not self.collection:
                self.collectionCreated.emit({"id": col_id, "doc_id": new_id})
        else:
            self.status_label.setText(f"Updated doc with ID \"{doc_id}\"")

    def load_document(self):

        if not self.htmlLoaded:
            return
        
        col_id = self.collection

        if not col_id:
            self.status_label.setText("Creating new collection")
            return
           
        doc_id = self.doc_id_input.currentText().strip()

        if not doc_id:
            self.status_label.setText("Please enter a Document ID")
            return

        doc_dict = load_document(col_id, doc_id)

        if doc_dict is None:
            self.status_label.setText(f"\"{doc_id}\" does not exist in \"{col_id}\"")
            return
        
        for field in self.field_widgets:
            self.set_field_value(field, doc_dict.get(field))
        
        self.status_label.setText(f"Loaded document \"{doc_id}\"")

    def clear_fields(self):
        self.collection_label.setText("")
        self.doc_id_input.setCurrentText("")
        for field in self.field_widgets:
            self.set_field_value(field, "")
        self.status_label.setText("")

    def gen_html(self):
        return ""
    
    def set_collection(self, msg):
        collection = msg.get("id") if msg else None
        self.collection_label.setText(collection)
        if check_collection(collection):
            self.collection = collection
            self.collection_label.setReadOnly(True)
        else:
            self.collection = None
            self.collection_label.setReadOnly(False)
        self.set_documents(msg.get("doc_id"))
    
    def set_documents(self, doc_id=None):
        docs = load_documents(self.collection)
        self.doc_id_input.clear()
        if docs is None:
            return
        for doc in docs:
            self.doc_id_input.addItem(doc['id'])
        self.doc_id_input.setCurrentText(doc_id if doc_id else "")
