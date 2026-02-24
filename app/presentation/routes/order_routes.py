from flask import Blueprint, request, jsonify
from sqlalchemy import null
from app.application.services.order_validator import validate_order_items
from app.infrastructure.database.db import db
from app.infrastructure.database.models import Order, OrderItem
from app.infrastructure.security.auth_middleware import token_required

order_bp = Blueprint("orders", __name__)

@order_bp.route("/orders", methods=["POST"])
@token_required
def create_order(current_user):
    data = request.json

    try:
        validate_order_items(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 422

    order = Order(user_id=current_user.id)
    db.session.add(order)
    db.session.flush()

    total_amount = 0
    
    for item_data in data["items"]:
        item_quantity = item_data["quantity"]
        item_price = item_data["unit_price"]
        item_amount = item_quantity * item_price
        total_amount += item_amount
        item = OrderItem(
            order_id=order.id,
            product_name=item_data["product_name"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
        )
        db.session.add(item)

    order.total_amount = total_amount

    db.session.commit()

    return jsonify({"message": "Item added", "total": total_amount, "order_id": order.id}), 201


@order_bp.route("/orders", methods=["GET"])
@token_required
def list_orders(current_user):
    orders_user = Order.query.filter_by(user_id=current_user.id).all()

    return jsonify({
        "message": "Authenticated",
        "user_id": current_user.id,
        "email": current_user.email,
        "orders": orders_user
    })

@order_bp.route("/orders/<id>", methods=["GET"])
@token_required
def list_itens_in_orders(current_user, order_id):
    asking_order = Order.query.get(id=order_id)
    if asking_order is null:
        return jsonify({"message": "Order doesn't exist"}), 403
    # Necessário implementar caso a ordem nao exista 403
    if asking_order.user_id != current_user.id:
        return jsonify({"message": "User don't have this order"}), 403
    itens = OrderItem.query.get(order_id=asking_order.id).all()
    return jsonify({
        "id": asking_order.id,
        "total_amount": asking_order.total_amount,
        "items": [itens]
    })

@order_bp.route("/orders/<int:order_id>/items", methods=["POST"])
def add_item(order_id):
    data = request.json

    item = OrderItem(
        order_id=order_id,
        product_name=data["product_name"],
        quantity=data["quantity"],
        unit_price=data["unit_price"],
    )

    db.session.add(item)

    items = OrderItem.query.filter_by(order_id=order_id).all()
    total = sum(i.quantity * i.unit_price for i in items)
    total += data["quantity"] * data["unit_price"]

    order = Order.query.get(order_id)
    order.total_amount = total

    db.session.commit()

    return jsonify({"message": "Item added", "total": total})