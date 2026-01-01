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

## Post Format:

```json
[
    {
        'id': Document ID (String),
        'title': Post Title (String),
        'body': Post Content (String),
        'timestamp': Creation Timestamp (UTC String),
        'updated': Last Updated Timestamp (UTC String)
    }
]
```

## Credits

### Mathematical Typesetting

- [Katex](github.com/KaTeX/KaTeX)

### UI Render

- PyQt5
- PyQt5WebEngine

### APIs

- Firebase
- Google APIs
