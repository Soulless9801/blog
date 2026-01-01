# Firestore Utilities

## Requirements

A `service_account.json` file containing the admin service account key used by `interface.py`.

A `.env` file containing the variable(s) `LOCAL_PATH` denoting the JSON file where `write.py` will write data to.

## Description

You can choose to load and update pre-existing posts, as well as create and store new ones to a Firebase Firestore. Automatically creates/updates creation time and last time updated. 

Supports reading the current datastore and writing data to a local JSON file.

## Instructions

### Prerequisites

Python3

### Installation

To install the required libraries, run the following command

```
pip install -r requirements.txt
```

## Post Format

```json
{
    "id": "Document ID (string)",
    "title": "Post Title (string)",
    "body": "Post Content (string)",
    "timestamp": "Creation Timestamp (UTC string)",
    "updated": "Last Updated Timestamp (UTC string)"
}
```

## Credits

### Mathematical Typesetting

- [Katex](github.com/KaTeX/KaTeX)

### UI Render

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)

### Google APIs

- [firebase](https://github.com/googleapis/python-firestore)
- [service_account](https://github.com/googleapis/google-auth-library-python)

All third-party software are used in accordance with their respective licenses as listed on project websites or repositories.
