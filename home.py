import sys
from posts import CollectionEditorApp
from problems import SolutionEditorApp
from PyQt5 import QtWidgets, QtCore

from datetime import datetime

Timestamp = datetime

from check import get_collections, validate_collection

collectionSchema = {
    "title": str,
    "body": str,
    "created": Timestamp,   
    "updated": Timestamp
}

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

class CollectionPage(QtWidgets.QWidget):

    def __init__(self, types):
        super().__init__()

        self.resize(1200, 800)

        self.stack = QtWidgets.QStackedWidget()

        self.pages = {}
        self.routes = []
    
        for collection in get_collections():
            collection_name = collection.id
            if not validate_collection(collection_name, collectionSchema):
                continue
            self.pages[collection_name] = CollectionEditorApp(collection_name)
            self.stack.addWidget(self.pages[collection_name])
            self.routes.append({ "label": collection_name, "route": collection_name })

        self.pages["new"] = CollectionEditorApp(None)
        self.stack.addWidget(self.pages["new"])
        self.routes.append({ "label": "+ New", "route": "new" })

        self.pages["new"].collectionCreated.connect(self.refresh_menu)
        
        self.menu_label = QtWidgets.QLabel("Collections")

        self.menu = CollectionMenu(self.routes)

        self.menu.pageRequested.connect(self.navigate)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.menu_label)
        vbox.addWidget(self.menu)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addLayout(vbox)
        layout.addWidget(self.stack)

        self.stack.setCurrentWidget(self.pages[self.routes[0]["route"]])
    
    def refresh_menu(self, msg):
        page = msg["id"]
        self.pages[page] = CollectionEditorApp(page, msg["doc_id"])
        self.stack.addWidget(self.pages[page])
        self.routes.append({ "label": page, "route": page })

        self.menu.add({ "label": page, "route": page })

        self.stack.setCurrentWidget(self.pages[page])

    def navigate(self, route):
        page = self.pages.get(route)
        if page:
            self.stack.setCurrentWidget(page)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    collection_page = CollectionPage()
    collection_page.show()
    sys.exit(app.exec_())

