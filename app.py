import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flasgger import Swagger
from routes.feedback import feedback_bp
from admin import admin_bp
from routes.shop import shop_bp
from routes.client import client_bp
from routes.api import api_v1
from models import init_db, get_db_connection


DATABASE_PATH = os.environ.get("DATABASE_PATH", "data/database.db")


app = Flask(__name__, static_folder='static')


os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)


log_path = os.environ.get("LOG_PATH", "logs/app.log")
os.makedirs(os.path.dirname(log_path), exist_ok=True)
handler = RotatingFileHandler(log_path, maxBytes=5*1024*1024, backupCount=5)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)

app.logger.setLevel(logging.INFO)
app.logger.addHandler(handler)

app.secret_key = 'secret-key'

swagger_config = {
    "headers": [],
    "title": "Flask Shop API",
    "version": "1.0.0",
    "description": "API для управління продуктами, замовленнями та відгуками",
    "termsOfService": "",
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,

    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],

    "specs_route": "/docs/"
}

swagger = Swagger(app, config=swagger_config)


init_db()

app.register_blueprint(api_v1, url_prefix="/api/v1")
try:
    app.register_blueprint(admin_bp)
except Exception:
    pass
try:
    app.register_blueprint(shop_bp)
except Exception:
    pass
try:
    app.register_blueprint(client_bp)
except Exception:
    pass
try:
    app.register_blueprint(feedback_bp)
except Exception:
    pass

@app.before_request
def log_request_info():
    app.logger.info(f"{request.method} {request.path} - from {request.remote_addr}")


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')


# ---- Admin login ----
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '123'

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['is_admin'] = True
            flash('Вхід успішний!', 'success')
            return redirect(url_for('admin.admin_panel'))
        else:
            flash('Невірний логін або пароль', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('Будь ласка, увійдіть у свій акаунт')
        return redirect(url_for('login'))
    return render_template('dashboard.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    session.pop('admin_user', None)
    return redirect(url_for('home'))


@app.route('/logout')
def client_logout():
    session.pop('is_client', None)
    session.pop('client_user', None)
    return redirect(url_for('home'))


@app.route("/api_demo")
def api_demo():
    return render_template("api_demo.html")


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(500)
def internal(e):
    return jsonify({"error": "Internal server error"}), 500

@app.route("/health")
def health():
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        return {"status": "ok", "database": "connected"}, 200
    except Exception as e:
        app.logger.exception("Healthcheck failed")
        return {"status": "error", "error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
