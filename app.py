import os
from datetime import datetime, timezone
from functools import lru_cache
from uuid import uuid4

from azure.cosmos import CosmosClient
from flask import Flask, render_template, request

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}


@lru_cache(maxsize=1)
def get_cosmos_container():
    endpoint = os.getenv("COSMOS_ENDPOINT")
    key = os.getenv("COSMOS_KEY")
    database_name = os.getenv("COSMOS_DATABASE_NAME")
    container_name = os.getenv("COSMOS_CONTAINER_NAME")

    if not all([endpoint, key, database_name, container_name]):
        raise RuntimeError(
            "Cosmos DB settings are missing. Set COSMOS_ENDPOINT, COSMOS_KEY, "
            "COSMOS_DATABASE_NAME, and COSMOS_CONTAINER_NAME."
        )

    client = CosmosClient(endpoint, credential=key)
    database = client.get_database_client(database_name)
    return database.get_container_client(container_name)


def save_contact_submission(name, email, phone, message):
    container = get_cosmos_container()
    normalized_email = email.strip().lower()
    # Partition strategy: "<portal>#<subject>" keeps data grouped by actor while
    # allowing future portals (public/employee/admin) in the same container.
    partition_key = f"public#{normalized_email}"
    item = {
        "id": str(uuid4()),
        "pk": partition_key,
        "type": "contact_submission",
        "portal": "public",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "name": name,
        "email": email,
        "phone": phone,
        "message": message,
    }
    container.create_item(body=item)


@app.route('/')
def home():
    return render_template('home.html', page='home')


@app.route('/about')
def about():
    return render_template('about.html', page='about')


@app.route('/services')
def services():
    return render_template('services.html', page='services')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form_data = {"name": "", "email": "", "phone": "", "message": ""}
    form_error = None
    form_success = None

    if request.method == 'POST':
        form_data = {
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "message": request.form.get("message", "").strip(),
        }

        if not form_data["name"] or not form_data["email"] or not form_data["message"]:
            form_error = "Please fill in Name, Email, and Project Details."
        else:
            try:
                save_contact_submission(
                    form_data["name"],
                    form_data["email"],
                    form_data["phone"],
                    form_data["message"],
                )
                form_success = "Thanks. Your message has been saved and our team will contact you soon."
                form_data = {"name": "", "email": "", "phone": "", "message": ""}
            except Exception:
                form_error = "We could not save your message right now. Please try again shortly."

    return render_template(
        'contact.html',
        page='contact',
        form_data=form_data,
        form_error=form_error,
        form_success=form_success,
    )


if __name__ == '__main__':
    debug = os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=debug)
