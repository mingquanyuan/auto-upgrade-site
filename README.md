# AutoUpgrade Garage (Flask Website)

A multi-page website for an auto-upgrade shop built with Python Flask, HTML, and CSS.

## Pages

- Home: `/`
- About Us: `/about`
- Services: `/services`
- Contact Us: `/contact`

## Project Structure

```text
auto-upgrade/
├── app.py
├── requirements.txt
├── static/
│   └── css/
│       └── styles.css
└── templates/
    ├── base.html
    ├── home.html
    ├── about.html
    ├── services.html
    └── contact.html
```

## Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open: `http://127.0.0.1:5000`

## Common Error: `ModuleNotFoundError: No module named 'flask'`

This means Flask is not installed in the same Python environment used to run `app.py`.

Use:

```bash
python -m pip install -r requirements.txt
```

Then verify:

```bash
python -m pip show Flask
python app.py
```
