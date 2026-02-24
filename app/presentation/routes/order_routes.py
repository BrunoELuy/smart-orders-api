from flask import Blueprint, request, jsonify
from app.infrastructure.database.db import db
from app.infrastructure.database.models import Order, OrderItem
from app.infrastructure.security.auth_middleware import token_required

order_bp = Blueprint("orders", __name__)

@order_bp.route("/orders", methods=["POST"])
def create_order():
    data = request.json

    order = Order(user_id=data["user_id"])
    db.session.add(order)
    db.session.commit()

    return jsonify({"order_id": order.id}), 201


@order_bp.route("/orders", methods=["GET"])
@token_required
def list_orders(current_user):
    return jsonify({
        "message": "Authenticated",
        "user_id": current_user.id,
        "email": current_user.email
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

    items = OrderItem.query.filter_by(oder_id=order_id).all()
    total = sum(i.quantity * i.unit_price for i in items)
    total += data["quantity"] * data["unit_price"]

    order = Order.query.get(order_id)
    order.total_amount = total

    db.session.commit()

    return jsonify({"message": "Item added", "total": total})