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

        self.resize(1200, 800)
        self.setWindowTitle("Firestore Interface")

        layout = QtWidgets.QHBoxLayout(self)

        menu = QtWidgets.QHBoxLayout()
        menu.setContentsMargins(10, 10, 10, 10) # TODO styling

        collection_menu = QtWidgets.QVBoxLayout()

        collection_label = QtWidgets.QLabel("Collection Name")

        collection_menu.addWidget(collection_label)

        self.cbox = QtWidgets.QVBoxLayout()

        for collection in get_collections():
            btn = QtWidgets.QPushButton(collection.id)
            btn.clicked.connect(lambda _, c=collection.id: self.refresh_page({"id": c}))
            self.cbox.addWidget(btn)
        
        new_collection_btn = QtWidgets.QPushButton("+ New")
        new_collection_btn.clicked.connect(lambda _: self.refresh_page({"id": None}))
        self.cbox.addWidget(new_collection_btn)

        self.cbox.addStretch()

        collection_menu.addLayout(self.cbox)

        menu.addLayout(collection_menu)

        vbox = QtWidgets.QVBoxLayout()

        self.stack = QtWidgets.QStackedWidget()

        self.pages = {}
        self.routes = []
    
        for type in types:
            page = type()
            self.pages[page.title] = page
            self.stack.addWidget(page)
            page.collectionCreated.connect(self.add_collection)
            self.routes.append({ "label": page.title, "route": page.title })
        
        type_label = QtWidgets.QLabel("Collection Types")

        self.type_menu = CollectionMenu(self.routes)

        self.type_menu.pageRequested.connect(self.navigate)

        vbox.addWidget(type_label)
        vbox.addWidget(self.type_menu)

        menu.addLayout(vbox)

        layout.addLayout(menu)

        self.stack.setCurrentWidget(self.pages[self.routes[0]["route"]])

        layout.addWidget(self.stack)
    
    def add_collection(self, msg):
        btn = QtWidgets.QPushButton(msg.get("id"))
        btn.clicked.connect(lambda _, c=msg: self.refresh_page({"id": c.get("id")}))
        self.cbox.insertWidget(self.cbox.count() - 2, btn)
        self.refresh_page(msg)
        widget = self.stack.currentWidget()
        widget.message(f"Note: Add {msg.get('id')} to Intended Collections for page \"{widget.title}\"")

    def refresh_page(self, msg):
        widget = self.stack.currentWidget()
        widget.set_collection(msg)

    def navigate(self, route):
        page = self.pages.get(route)
        collection = self.stack.currentWidget().collection
        doc = self.stack.currentWidget().doc_id_input.currentText().strip()
        if page:
            self.stack.setCurrentWidget(page)
            self.refresh_page({ "id": collection, "doc_id": doc })

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    home_page = HomePage([PostsPage, ProblemsPage, USACOProblemsPage])
    home_page.show()
    sys.exit(app.exec_())

