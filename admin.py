from flask import Blueprint, render_template, redirect, url_for, request
from models import get_db_connection, get_orders, get_order_details, update_order_status, delete_order
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import get_db_connection, get_all_feedbacks, get_orders, get_products, delete_order

from datetime import datetime


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

                                            # зробив (Діма Чаркін) полагодив та оформив (Стас Мельник, Максим Пахольчук)

@admin_bp.route('/')
def admin_panel():
    if not session.get('is_admin'):
        flash('Увійдіть як адміністратор', 'error')
        return redirect(url_for('admin_login'))

    orders = get_orders()
    feedbacks = get_all_feedbacks()
    products = get_products()

    return render_template('admin.html', orders=orders, feedback=feedbacks, products=products)

                                                 # додавання товару
@admin_bp.route('/add_product', methods=['POST'])
def add_product():
    if not session.get('is_admin'):
        flash('Увійдіть як адміністратор', 'error')
        return redirect(url_for('admin_login'))

    name = request.form.get('name', '').strip()
    price = request.form.get('price', '').strip()
    image = request.form.get('image', '').strip()

    if not name or not price:
        flash('Заповніть усі поля', 'warning')
        return redirect(url_for('admin.admin_panel'))

    try:
        price_val = float(price)
    except ValueError:
        flash('Ціна має бути числом', 'danger')
        return redirect(url_for('admin.admin_panel'))

    conn = get_db_connection()
    conn.execute('INSERT INTO products (name, price, image) VALUES (?, ?, ?)', (name, price_val, image))
    conn.commit()
    conn.close()

    flash('✅ Товар додано', 'success')
    return redirect(url_for('admin.admin_panel'))


                                                    # видалення товару

@admin_bp.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):

    if not session.get('is_admin'):
        flash('Увійдіть як адміністратор', 'error')
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()

    flash('🗑️ Товар видалено', 'success')
    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/admin/delete_feedback/<int:id>', methods=['POST'])
def delete_feedback(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM feedback WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/admin/order/<int:order_id>')
def order_details(order_id):
    conn = get_db_connection()

    order = conn.execute("""
        SELECT id, email, address, total_price, status, date, promo_code
        FROM orders WHERE id = ?
    """, (order_id,)).fetchone()

    if not order:
        conn.close()
        flash("Замовлення не знайдено", "danger")
        return redirect(url_for('admin.admin_panel'))

    items = conn.execute("""
        SELECT p.name, p.price, op.quantity
        FROM order_products op
        JOIN products p ON p.id = op.product_id
        WHERE op.order_id = ?
    """, (order_id,)).fetchall()

    conn.close()

    return render_template('order_details.html', order=order, items=items)

@admin_bp.route('/admin/update_order_status/<int:order_id>', methods=['POST'])
def update_order(order_id):
    status = request.form['status']
    update_order_status(order_id, status)
    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/admin/delete_order/<int:order_id>', methods=['POST'])
def delete_order_route(order_id):
    delete_order(order_id)
    return redirect(url_for('admin.admin_panel'))