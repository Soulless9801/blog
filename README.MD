# Firestore Utilities

## Requirements

A `service_account.json` file containing the Firestore admin service account key.

## Description

Load, update, and create Firestore documents containing data with a customizable format. Supports custom web view rendering using Firestore fields. 

Supports writing data to a local JSON file with `write.py`.

## Instructions

python3 and pip3 required.

### Installation

To install the required libraries, run the following command

```
pip install -r requirements.txt
```

## Usage

A virtual environment is recommended.

### Collection Editing

Run `python3 home.py` to access collection editors

Current presets include
- `pages.PostsPage` contains fields `title` and `body`, typical of blog posts.
- `pages.ProblemsPage` contains fields `language` and `submission`, typical of a program snippet.

To create your own custom collection editor, create a new child class of `pages.CollectionEditorPage`.

The parent class accepts the following parameters:

- `collection` denotes the ID of the collection. If no collection is found with that ID, defaults to create mode.
- `doc_id` denotes the ID of the initial document to be loaded.
- `theme` denotes a theme preset that can be used to style web view.
- `fields` denotes a dictionary mapping Firestore fields to corresponding schema.
- `title` denotes the name of the page.

### `fields` Example 

```python
fields = {
    'title': {
        'type': 'lineedit',
        'label': 'Title',
    },
    'body': {
        'type': 'textedit',
        'label': 'Body',
        'on_change': self.render_markdown,
    },
    'language': {
        'type': 'dropdown',
        'label': 'Language',
        'options': ["English", "Spanish"],
        'on_change': self.render_markdown,
    },
}
```

### Local Writing

Run `python3 write.py --collection COLLECTION_ID --path LOCAL_PATH` to write the contents of firestore collection with if `COLLECTION_ID` to a loca file with path `LOCAL_PATH`.

## Credits

All third-party software are used in accordance with their respective licenses as listed on project websites or repositories.

### Mathematical Typesetting

- [Katex](https://github.com/KaTeX/KaTeX)

### Syntax Highlighting

- [Shiki](https://github.com/shikijs/shiki)

### UI Render

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)

### Google APIs

- [firebase](https://github.com/googleapis/python-firestore)
- [service_account](https://github.com/googleapis/google-auth-library-python)
