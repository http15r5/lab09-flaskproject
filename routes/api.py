from flask import Blueprint, request, jsonify
from models import (
    register_client, verify_client, get_products,
    add_order, get_orders, get_order_details,
    update_order_status, delete_order,
    get_all_feedbacks, delete_feedback, get_feedbacks_by_email,
    get_db_connection
)
from werkzeug.exceptions import BadRequest

api_v1 = Blueprint("api_v1", __name__)


def validate_json(keys, data):
    if not all(k in data for k in keys):
        raise BadRequest(f"Missing keys: {', '.join(k for k in keys if k not in data)}")


# -- замолвення -- 
@api_v1.get("/products")
def api_get_products():
    """
    Отримати всі продукти
    ---
    tags:
      - Products
    responses:
      200:
        description: Список продуктів
    """
    rows = get_products()
    return jsonify([{k: r[k] for k in r.keys()} for r in rows]), 200


#  --  закази  --
@api_v1.post("/orders")
def api_add_order():
    """
    Створити нове замовлення
    ---
    tags:
      - Orders
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            email:
              type: string
            address:
              type: string
            product_id:
              type: integer
            quantity:
              type: integer
    responses:
      201:
        description: Замовлення створено
    """
    data = request.get_json() or {}
    validate_json(["email", "address", "product_id", "quantity"], data)

    conn = get_db_connection()
    product = conn.execute("SELECT price FROM products WHERE id = ?", (data["product_id"],)).fetchone()

    if not product:
        return jsonify({"error": "Product not found"}), 404

    cart = {
        "1": {
            "id": data["product_id"],
            "quantity": data["quantity"],
            "price": product["price"]
        }
    }

    conn.close()
    add_order(data["email"], data["address"], cart)
    return jsonify({"created": True}), 201


@api_v1.get("/orders")
def api_get_orders():
    """
    Отримати всі замовлення
    ---
    tags:
      - Orders
    responses:
      200:
        description: Список замовлень
    """
    rows = get_orders()
    return jsonify([{k: r[k] for k in r.keys()} for r in rows]), 200


@api_v1.get("/orders/<int:order_id>")
def api_get_order(order_id):
    """
    Отримати деталі замовлення
    ---
    tags:
      - Orders
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Деталі замовлення
      404:
        description: Не знайдено
    """
    order, items = get_order_details(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    return jsonify({
        "order": {k: order[k] for k in order.keys()},
        "items": [{k: r[k] for k in r.keys()} for r in items]
    }), 200


@api_v1.put("/orders/<int:order_id>")
def api_update_order(order_id):
    """
    Оновити статус замовлення
    ---
    tags:
      - Orders
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        schema:
          properties:
            status:
              type: string
    responses:
      200:
        description: Статус оновлено
    """
    data = request.get_json() or {}
    validate_json(["status"], data)
    update_order_status(order_id, data["status"])
    return jsonify({"updated": True}), 200


@api_v1.delete("/orders/<int:order_id>")
def api_delete_order(order_id):
    """
    Видалити замовлення
    ---
    tags:
      - Orders
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Замовлення видалено
    """
    delete_order(order_id)
    return jsonify({"deleted": True}), 200


# -- відгуки --
@api_v1.post("/feedback")
def api_add_feedback():
    """
    Створити відгук
    ---
    tags:
      - Feedback
    parameters:
      - name: body
        in: body
        schema:
          properties:
            name:
              type: string
            email:
              type: string
            message:
              type: string
    responses:
      201:
        description: Відгук створено
    """
    data = request.get_json() or {}
    validate_json(["name", "email", "message"], data)

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO feedback (name, email, message) VALUES (?, ?, ?)",
        (data["name"], data["email"], data["message"])
    )
    conn.commit()
    conn.close()

    return jsonify({"created": True}), 201


@api_v1.get("/feedback")
def api_get_feedback_all():
    """
    Отримати всі відгуки
    ---
    tags:
      - Feedback
    responses:
      200:
        description: Список усіх відгуків
    """
    rows = get_all_feedbacks()
    return jsonify([{k: r[k] for k in r.keys()} for r in rows]), 200


@api_v1.delete("/feedback/<int:feedback_id>")
def api_delete_feedback(feedback_id):
    """
    Видалити відгук
    ---
    tags:
      - Feedback
    parameters:
      - name: feedback_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Відгук видалено
    """
    conn = get_db_connection()
    conn.execute("DELETE FROM feedback WHERE id = ?", (feedback_id,))
    conn.commit()
    conn.close()
    return jsonify({"deleted": True}), 200


