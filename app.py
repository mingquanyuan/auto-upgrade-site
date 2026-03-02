import os

from flask import Flask, render_template

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}


@app.route('/')
def home():
    return render_template('home.html', page='home')


@app.route('/about')
def about():
    return render_template('about.html', page='about')


@app.route('/services')
def services():
    return render_template('services.html', page='services')


@app.route('/contact')
def contact():
    return render_template('contact.html', page='contact')


if __name__ == '__main__':
    debug = os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=debug)
