from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import get_products, add_order
import json
from flask import Blueprint, render_template
from models import get_products
import sqlite3
from functools import wraps

def get_db_connection():
    conn = sqlite3.connect("db.sqlite")
    conn.row_factory = sqlite3.Row
    return conn

shop_bp = Blueprint('shop', __name__, url_prefix='/shop')

                                                          # зробив (Діма Чаркін) доробив (Мельник Станіслав)


                                                                 # магазин

shop_bp = Blueprint('shop', __name__)

@shop_bp.route('/shop')
def shop():
    query = request.args.get('q', '').strip().lower()
    sort = request.args.get('sort', '').strip()

    conn = get_db_connection()

    sql = "SELECT * FROM products"
    params = []

                                                                 # пошук
    if query:
        sql += " WHERE LOWER(name) LIKE ?"
        params.append(f"%{query}%")

                                                               # сортування
    if sort == "asc":
        sql += " ORDER BY price ASC"
    elif sort == "desc":
        sql += " ORDER BY price DESC"

    products = conn.execute(sql, params).fetchall()
    conn.close()

    return render_template('shop.html', products=products)


                                                            # додавання товару
@shop_bp.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    products = get_products()
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        cart = session.get('cart', {})
        if str(product_id) in cart:
            cart[str(product_id)]['quantity'] += 1
        else:
            cart[str(product_id)] = {
                'id': product_id,
                'name': product['name'],
                'price': product['price'],
                'quantity': 1
            }
        session['cart'] = cart
        flash(f"Товар «{product['name']}» додано до кошика 🛒", "success")
    return redirect(url_for('shop.shop'))

                                                              # кошик
@shop_bp.route('/cart')
def cart():
    cart = session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    discount = session.get('discount', 0)
    if discount:
        discounted_total = round(total * (1 - discount / 100), 2)
    else:
        discounted_total = total

    return render_template(
        'cart.html',
        cart=cart,
        total=total,
        discounted_total=discounted_total,
        discount=discount
    )

                                                                 # видалення товару
@shop_bp.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        removed_item = cart.pop(str(product_id))
        session['cart'] = cart
        flash(f"Товар «{removed_item['name']}» видалено з кошика 🗑️", "info")
    return redirect(url_for('shop.cart'))

                                                                   # промокоди
@shop_bp.route('/apply_promo', methods=['POST'])
def apply_promo():
    code = request.form.get('promo_code', '').strip().upper()
    if not code:
        flash("Введіть промокод!", "warning")
        return redirect(url_for('shop.cart'))

    try:
        with open('promocodes.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        flash("Файл промокодів не знайдено!", "danger")
        return redirect(url_for('shop.cart'))

    if code in data:
        discount = data[code]
        session['promo_code'] = code
        session['discount'] = discount
        flash(f"Промокод {code} застосовано! Знижка {discount}%", "success")
    else:
        session.pop('promo_code', None)
        session.pop('discount', None)
        flash("Невірний промокод", "danger")

    return redirect(url_for('shop.cart'))

def add_order(email, address, cart, total_price, promo_code=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO orders (email, address, total_price, status, date, promo_code)
        VALUES (?, ?, ?, ?, datetime('now', 'localtime'), ?)
    """, (email, address, total_price, 'Нове', promo_code))

    order_id = cursor.lastrowid

    for item_id, item in cart.items():
        cursor.execute("""
            INSERT INTO order_products (order_id, product_id, quantity)
            VALUES (?, ?, ?)
        """, (order_id, item_id, item['quantity']))

    conn.commit()
    conn.close()

@shop_bp.route('/checkout', methods=['POST'])
def checkout():
    if not session.get('is_client') or 'client_email' not in session:
        flash('Будь ласка, увійдіть у свій акаунт, щоб оформити замовлення', 'warning')
        return redirect(url_for('client.login', next=request.path))

    cart = session.get('cart', {})
    if not cart:
        flash('Ваш кошик порожній 🛒', 'warning')
        return redirect(url_for('shop.shop'))

    email = session['client_email']
    address = request.form['address']

    promo_code = session.get('promo_code')
    discount = session.get('discount', 0)

    total = sum(item['price'] * item['quantity'] for item in cart.values())
    discounted_total = round(total * (1 - discount / 100), 2)

    add_order(email, address, cart, total_price=discounted_total, promo_code=promo_code)

    session['cart'] = {}
    session.pop('promo_code', None)
    session.pop('discount', None)

    flash(f"Ваше замовлення успішно оформлено ✅ Сума до сплати: {discounted_total} $", "success")
    return redirect(url_for('client.client_dashboard'))



