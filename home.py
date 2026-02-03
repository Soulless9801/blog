import sys
from pages.posts import PostsPage
from pages.problems import ProblemsPage, USACOProblemsPage
from PyQt5 import QtWidgets, QtCore

from datetime import datetime

Timestamp = datetime

from pages.check import get_collections

class CollectionMenu(QtWidgets.QWidget):

    pageRequested = QtCore.pyqtSignal(object)

    def __init__(self, pages):
        super().__init__()

        self.layout = QtWidgets.QVBoxLayout(self)

        for page in pages:
            btn = QtWidgets.QPushButton(page["label"])
            btn.clicked.connect(lambda _, p=page["route"]: self.pageRequested.emit(p))
            self.layout.addWidget(btn)
        
        self.layout.addStretch()
    
    def add(self, page):
        btn = QtWidgets.QPushButton(page["label"])
        btn.clicked.connect(lambda _, p=page["route"]: self.pageRequested.emit(p))
        self.layout.insertWidget(self.layout.count() - 2, btn) # add before new collection button

class HomePage(QtWidgets.QWidget):

    def __init__(self, types):
        super().__init__()

        # initialization
        self.setWindowTitle("Firestore Interface")

        # main layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)

        # wrapper widget for menu
        bigw = QtWidgets.QWidget()
        layout.addWidget(bigw)

        # layout for menu
        menu = QtWidgets.QHBoxLayout(bigw)

        # collection menu initialization
        collection_menu = QtWidgets.QVBoxLayout()
        collection_menu.setAlignment(QtCore.Qt.AlignCenter)
        menu.addLayout(collection_menu)

        # collection menu label
        collection_label = QtWidgets.QLabel("Collection Name")
        collection_menu.addWidget(collection_label)

        # collection menu buttons layout
        self.collection_box = QtWidgets.QVBoxLayout()
        collection_menu.addLayout(self.collection_box)

        # collection buttons
        for collection in get_collections():
            btn = QtWidgets.QPushButton(collection.id)
            btn.clicked.connect(lambda _, c=collection.id: self.refresh_page({"id": c}))
            self.collection_box.addWidget(btn)
        
        # new collection button
        new_collection_btn = QtWidgets.QPushButton("+ New")
        new_collection_btn.clicked.connect(lambda _: self.refresh_page({"id": None}))
        self.collection_box.addWidget(new_collection_btn)

        # expand space
        self.collection_box.addStretch()

        # type menu initialization
        type_menu = QtWidgets.QVBoxLayout()
        type_menu.setAlignment(QtCore.Qt.AlignTop)
        menu.addLayout(type_menu)

        # type menu label
        type_label = QtWidgets.QLabel("Collection Types")
        type_menu.addWidget(type_label)

        # type menu buttons layout
        type_box = QtWidgets.QVBoxLayout()
        type_box.setAlignment(QtCore.Qt.AlignCenter)
        type_menu.addLayout(type_box)

        # pages widget stack
        self.stack = QtWidgets.QStackedWidget()
        layout.addWidget(self.stack)

        # pages initialization
        self.pages = {}
        self.routes = []
    
        # add pages
        for type in types:

            page = type()

            # type button
            btn = QtWidgets.QPushButton(page.title)
            btn.clicked.connect(lambda _, p=page.title: self.navigate(p))
            type_box.addWidget(btn)

            # type page
            self.pages[page.title] = page
            self.stack.addWidget(page)
            self.routes.append({ "label": page.title, "route": page.title })

            # when new collection created
            page.collectionCreated.connect(self.add_collection)

        # set initial page  
        self.stack.setCurrentWidget(self.pages[self.routes[0]["route"]])
    
    def add_collection(self, msg):

        # type button
        btn = QtWidgets.QPushButton(msg.get("id"))
        btn.clicked.connect(lambda _, c=msg: self.refresh_page({"id": c.get("id")}))
        self.collection_box.insertWidget(self.collection_box.count() - 2, btn)

        # refresh page
        self.refresh_page(msg)
        widget = self.stack.currentWidget()
        widget.message(f"Note: Add {msg.get('id')} to Intended Collections for page \"{widget.title}\"")

    def refresh_page(self, msg): # response to collection changed
        widget = self.stack.currentWidget()
        widget.set_collection(msg)

    def navigate(self, route):
        page = self.pages.get(route)
        collection = self.stack.currentWidget().collection
        doc = self.stack.currentWidget().doc_id_input.currentText().strip()
        if page:
            self.stack.setCurrentWidget(page)
            self.refresh_page({ "id": collection, "doc_id": doc })

theme = 'dark' # TODO: implement theme switching

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(r"""
        QWidget, QHBoxLayout, QVBoxLayout, QFormLayout {
            padding: 0;
            margin: 0;
            font-size: 11px;
            background-color: %s;
        }
        QLabel, QLineEdit, QTextEdit, QComboBox, QAbstractItemView, QPlainTextEdit, QPushButton {
            padding: 4px;
            font-size: 11px;
            background-color: transparent;
            border: 1px solid %s;
            color: %s;
            border-radius: 4px;
        }
        QLabel {
            border: none !important;
        }
        QPushButton:hover {
            background-color: %s;
        }
    """ % ( # TODO: use some global styling system
        '#f9f5f1' if theme == 'light' else '#212529',
        '#252525' if theme == 'light' else '#ffffff',
        '#252525' if theme == 'light' else '#ffffff',
        '#faf4ee' if theme == 'light' else '#4f5357',
    ))
    home_page = HomePage([PostsPage, ProblemsPage, USACOProblemsPage])
    home_page.showMaximized()
    sys.exit(app.exec_())

