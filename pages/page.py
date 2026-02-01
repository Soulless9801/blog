import uuid
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

    def __init__(self, collection=None, doc_id=None, fields={}, tag=None, intended_collections=[], theme='dark', title="Collection Editor"):
        super().__init__()

        # initialization
        self.theme = theme

        self.tag = tag

        self.intended = intended_collections

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
        self.field_collection = {}

        # other fields
        for field, config in fields.items():
            collections = [None] if 'collection' not in config else config['collection']
            for collection in collections:
                if collection not in self.field_collection:
                    self.field_collection[collection] = []
                self.field_collection[collection].append(field)
            widget = self._create_widget(config)
            self.field_widgets[field] = widget
            form.addRow(config.get('label', field), widget)
        
        # save button
        self.save_btn = QtWidgets.QPushButton("Create / Update")
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

    def message(self, msg, silent=False):
        if hasattr(self, "status_label") and not silent:
            print(msg)
            self.status_label.setText(msg)

    def warning(self, msg):
        self.message(f"WARNING: {msg}", silent=False)

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
        self.load_document(silent=True)

    def check_id(self, col_id, doc_id):
        for col in self.field_collection:
            col = col_id if not col else col
            doc = load_document(col, doc_id)
            if doc:
                return True
        return False

    def gen_id(self, col_id):
        s = ""
        while True:
            s = uuid.uuid4()
            if not self.check_id(col_id, str(s)):
                return str(s)

    def save_document(self, silent=False):
        if not hasattr(self, "htmlLoaded") or not self.htmlLoaded:
            return
        
        col_id = self.collection if self.collection else self.collection_label.text().strip()

        if not col_id: # valid collection ID check
            self.message("Empty Collection ID", silent=silent)
            return
        
        for collection in self.field_collection:
            if not collection or check_collection(collection):
                continue
            self.warning(f"\"{collection}\" Does Not Exist (Proceeding Anyway)")
        
        doc_id = self.doc_id_input.currentText().strip()
        doc_id = self.gen_id(col_id) if not doc_id else doc_id

        for field in self.fields: # valid data check
            if not ''.join(self.get_field_value(field).split(' ')):
                self.message(f"Empty \"{field}\" Field", silent=silent)
                return

        for collection in self.field_collection:

            data = {}

            for field in self.field_collection[collection]:
                data[field] = self.get_field_value(field)

            col = col_id if not collection else collection

            if self.tag:
                data['tag'] = self.tag

            data['updated'] = get_timestamp()

            if not update_document(col, doc_id, data):
                data['created'] = get_timestamp()
                create_document(col, doc_id, data)
        
        self.message(f"Saved \"{doc_id}\"", silent=silent)
        
        self.doc_id_input.setCurrentText(doc_id)

        if not self.collection: # new collection created
            self.collectionCreated.emit({"id": col_id, "doc_id": doc_id})

    def load_document(self, silent=False):

        if not hasattr(self, "htmlLoaded") or not self.htmlLoaded:
            return
        
        col_id = self.collection

        if not col_id: # collection ID check
            self.message("Creating New Collection", silent=silent)
            return
           
        doc_id = self.doc_id_input.currentText().strip()

        if not doc_id: # document ID check
            self.message("Empty Document ID", silent=silent)
            return
        
        for collection in self.field_collection:

            col_id = self.collection if not collection else collection

            doc_dict = load_document(col_id, doc_id)

            if not doc_dict:
                continue
            
            for field in self.field_collection[collection]:
                self.set_field_value(field, doc_dict.get(field))
        
        self.message(f"Loaded document \"{doc_id}\"", silent=silent)

    def clear_fields(self):
        if hasattr(self, "collection_label"):
            self.collection_label.setText("")
        if hasattr(self, "doc_id_input"):
            self.doc_id_input.setCurrentText("")
        if hasattr(self, "field_widgets"):
            for field in self.field_widgets:
                self.set_field_value(field, "")
        if hasattr(self, "status_label"):
            self.status_label.setText("")

    def gen_html(self):
        return ""
    
    def set_collection(self, msg):
        self.clear_fields()
        collection = msg.get("id")
        if hasattr(self, "intended"):
            if collection and collection not in self.intended:
                self.warning(f"\"{collection}\" Not Intended for \"{self.title}\" Page")
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
            if self.tag and doc.get('tag') != self.tag:
                continue
            self.doc_id_input.addItem(doc['id'])

        self.doc_id_input.setCurrentText(doc_id if doc_id else "")

        self.load_document(silent=True)
        