from flask import Blueprint, render_template, request, session, redirect, url_for, flash, g, request, jsonify
from models import get_all_feedbacks, get_feedbacks_by_email, delete_feedback, register_client, verify_client, get_db_connection
import sqlite3

                                             # зробив та оформив (Мельник Станіслав)

db = sqlite3.connect('db.sqlite')
db.row_factory = sqlite3.Row
DATABASE = 'db.sqlite'


client_bp = Blueprint('client', __name__, template_folder='templates')

                                                            # реєстрація
@client_bp.route("/client/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if register_client(email, password):
            flash("Реєстрація успішна! Тепер увійдіть.", "success")
            return redirect(url_for("client.login"))
        else:
            flash("Ця пошта вже зареєстрована!", "warning")

    return render_template("client_register.html")


                                                 # Вхід
@client_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if verify_client(email, password):
            session['is_client'] = True
            session['client_email'] = email
            flash("✅ Ви успішно увійшли до акаунту!", "success")
            return redirect(url_for('client.client_dashboard'))
        else:
            flash("❌ Невірна пошта або пароль!", "danger")

    return render_template('client_login.html')


                                                  # вихід
@client_bp.route("/client/logout")
def logout():
    session.pop("client_email", None)
    session.pop("is_client", None)
    flash("Ви вийшли із системи.", "info")
    return redirect(url_for("client.login"))


                                              # панель клієнта
@client_bp.route('/client/dashboard')
def client_dashboard():
    if not session.get('client_email'):
        flash("Будь ласка, увійдіть у свій акаунт.", "warning")
        return redirect(url_for("client.login"))

    user_email = session['client_email']
    feedbacks = get_feedbacks_by_email(user_email)

                                   # замовлення користувача
    conn = get_db_connection()
    orders = conn.execute("""
        SELECT 
            id,
            address,
            total_price,
            status,
            date,
            promo_code
        FROM orders
        WHERE email = ?
        ORDER BY date DESC
    """, (user_email,)).fetchall()
    conn.close()

    return render_template(
        'client.html',
        feedbacks=feedbacks,
        user_email=user_email,
        orders=orders
    )

                                                 # ---видалення власного відгуку---
@client_bp.route('/client/delete/<int:feedback_id>', methods=['POST'])
def client_delete_feedback(feedback_id):
    user_email = session.get('client_email')
    if not user_email:
        flash('Увійдіть, щоб видаляти свої відгуки', 'error')
        return redirect(url_for('client.login'))

    delete_feedback(feedback_id, user_email)
    flash('Відгук успішно видалено!', 'success')
    return redirect(url_for('client.client_dashboard'))


def get_db():
    if '_database' not in g:
        g._database = sqlite3.connect('db.sqlite')
        g._database.row_factory = sqlite3.Row
    return g._database


@client_bp.route('/cancel_order/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", ("Скасовано", order_id))
    db.commit()

    return jsonify({'success': True})

@client_bp.route('/delete_order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    db = get_db()
    db.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    db.commit()
    return jsonify({'success': True})

@client_bp.route('/order_details/<int:order_id>')
def order_details(order_id):
    conn = get_db_connection()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        conn.close()
        return jsonify({'success': False, 'error': 'Order not found'}), 404

    products = conn.execute("""
        SELECT p.name, p.price, op.quantity
        FROM order_products op
        JOIN products p ON p.id = op.product_id
        WHERE op.order_id = ?
    """, (order_id,)).fetchall()

    conn.close()

    product_list = [
        {'name': p['name'], 'price': p['price'], 'quantity': p['quantity']}
        for p in products
    ]

    order_dict = {
        'id': order['id'],
        'address': order['address'],
        'total_price': order['total_price'],
        'status': order['status'],
        'date': order['date'],
        'promo_code': order['promo_code'],
        'products': product_list
    }

    return jsonify({'success': True, 'order': order_dict})

@client_bp.route("/reviews")
def reviews():
    conn = get_db_connection()
    feedbacks = conn.execute("SELECT * FROM feedback").fetchall()
    conn.close()

    is_logged_in = session.get('is_client', False)

    return render_template("reviews.html", feedbacks=feedbacks, is_logged_in=is_logged_in)
