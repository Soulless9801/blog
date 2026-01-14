# Firestore Utilities

## Requirements

A `service_account.json` file containing the Firestore admin service account key used by `interface.py` and `problems.py`.

## Description

Load, update, and create Firestore documents containing data intended to be used in a blog format. Data includes title, body text, creation and modification timestamps, and a code snippet. 

Additionally write data to a local JSON file.

## Instructions

### Installation

To install the required libraries, run the following commands

```
npm install
pip install -r requirements.txt
```

## Field Description

```json
{
    "id": "Document ID (string)",
    "title": "Post Title (string)",
    "body": "Post Content (string)",
    "created": "Creation Time (Timestamp)",
    "updated": "Last Updated (Timestamp)",
    "submission": "Raw Code (string, optional)",
    "language": "Code Language (string, optional)", 
}
```

## Usage

To perform operations on normal data (title, body, timestamps) run

```
python3 interface.py --collection COLLECTION_NAME
```

To perform operations with code data (optional) run

```
python3 problems.py --collection COLLECTION_NAME
```

To write collection data to a local file run

```
python3 write.py --collection COLLECTION_NAME --path LOCAL_PATH
```

## Credits

### Mathematical Typesetting

- [Katex](https://github.com/KaTeX/KaTeX)

### Syntax Highlighting

- [Shiki](https://github.com/shikijs/shiki)

### UI Render

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)

### Google APIs

- [firebase](https://github.com/googleapis/python-firestore)
- [service_account](https://github.com/googleapis/google-auth-library-python)

All third-party software are used in accordance with their respective licenses as listed on project websites or repositories.
