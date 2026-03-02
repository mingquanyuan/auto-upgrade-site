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

## Cosmos DB Configuration

The contact form backend stores submitted entries in Azure Cosmos DB.
Set these environment variables before running:

- `COSMOS_ENDPOINT`
- `COSMOS_KEY`
- `COSMOS_DATABASE_NAME`
- `COSMOS_CONTAINER_NAME`

Example:

```bash
export COSMOS_ENDPOINT="https://<account>.documents.azure.com:443/"
export COSMOS_KEY="<primary-or-secondary-key>"
export COSMOS_DATABASE_NAME="auto-upgrade-db"
export COSMOS_CONTAINER_NAME="contact-submissions"
```

### Partition key design (important)

Use container partition key path: `/pk`

Current contact submissions are written with:

- `pk = "public#<normalized-email>"`

Why this works for future portals:

- Keeps related records for the same actor in one logical partition.
- Supports high cardinality (better scale than low-cardinality keys like `portal` only).
- Extends cleanly for future writes:
  - Employee portal: `pk = "employee#<employee-id>"`
  - Admin portal: `pk = "admin#<admin-id>"`

## Azure App Service Deployment

This repo is ready for Azure App Service (Linux, Python).

### Required runtime details

- WSGI app entrypoint: `wsgi:app`
- Production server: `gunicorn` (already in `requirements.txt`)
- Startup command (set in App Service):  
  `gunicorn --bind=0.0.0.0 --timeout 600 wsgi:app`

### Create and deploy with Azure CLI

```bash
# Login and set subscription
az login
az account set --subscription "<your-subscription-name-or-id>"

# Variables
RG="rg-auto-upgrade"
PLAN="plan-auto-upgrade"
APP="<unique-app-name>"
LOCATION="eastus"

# Resource group + App Service plan + web app
az group create --name "$RG" --location "$LOCATION"
az appservice plan create --name "$PLAN" --resource-group "$RG" --sku B1 --is-linux
az webapp create --resource-group "$RG" --plan "$PLAN" --name "$APP" --runtime "PYTHON|3.12"

# Configure startup command
az webapp config set --resource-group "$RG" --name "$APP" --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 wsgi:app"

# Deploy from local git repo
az webapp up --name "$APP" --resource-group "$RG" --runtime "PYTHON:3.12"
```

### App settings (optional)

- `FLASK_DEBUG=0` for production.

## Docker

### Build and run locally

```bash
docker build -t auto-upgrade-site:latest .
docker run --rm -p 8000:8000 auto-upgrade-site:latest
```

Open: `http://127.0.0.1:8000`

### Deploy container to Azure App Service

```bash
# Login and set subscription
az login
az account set --subscription "<your-subscription-name-or-id>"

# Variables
RG="rg-auto-upgrade"
PLAN="plan-auto-upgrade"
APP="<unique-app-name>"
ACR="<unique-acr-name>"
LOCATION="eastus"

# Create Azure resources
az group create --name "$RG" --location "$LOCATION"
az acr create --resource-group "$RG" --name "$ACR" --sku Basic --admin-enabled true
az appservice plan create --name "$PLAN" --resource-group "$RG" --sku B1 --is-linux
az webapp create --resource-group "$RG" --plan "$PLAN" --name "$APP" --deployment-container-image-name "nginx"

# Build and push image to ACR
az acr build --registry "$ACR" --image auto-upgrade-site:latest .

# Point Web App to your image
ACR_SERVER=$(az acr show --name "$ACR" --resource-group "$RG" --query loginServer -o tsv)
az webapp config container set \
  --name "$APP" \
  --resource-group "$RG" \
  --docker-custom-image-name "$ACR_SERVER/auto-upgrade-site:latest"

# Tell App Service which port the container listens on
az webapp config appsettings set \
  --name "$APP" \
  --resource-group "$RG" \
  --settings WEBSITES_PORT=8000
```

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
