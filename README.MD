# Blog Firestore Interface

## Requirements

A `service_account.json` containing the admin service account key

## Description

You can choose to Load and Update pre-existing posts, as well as Create and Store new ones. Automatically stores/updates creation time and last time updated. 

## Instructions

### Prerequisites

Python3

### Installation

To install the required libraries, run the following command

```
pip install -r requirements.txt
```

## Post Format:

Document ID (Blank = Random) - String

Title - String

Body - String

Timestamp - Timestamp Object

Updated - Timestamp Object