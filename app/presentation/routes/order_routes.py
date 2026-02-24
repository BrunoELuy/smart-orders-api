from flask import Blueprint, request, jsonify
from sqlalchemy import null
from app.infrastructure.database.db import db
from app.infrastructure.database.models import Order, OrderItem
from app.infrastructure.security.auth_middleware import token_required

order_bp = Blueprint("orders", __name__)

@order_bp.route("/orders", methods=["POST"])
@token_required
def create_order(current_user):
    data = request.json

    if "items" not in data or not isinstance(data["items"], list) or not data["items"]:
        return jsonify({"message": "Data error"}), 422
    else:
        for item_data in data["items"]:
            if "quantity" not in item_data or not isinstance(item_data["quantity"], int) or not item_data["quantity"]:
                return jsonify({"message": "Data error"}), 422
            elif "unit_price" not in item_data or not isinstance(item_data["unit_price"], (int, float)) or not item_data["unit_price"]:
                return jsonify({"message": "Data error"}), 422
            elif "product_name" not in item_data or not isinstance(item_data["product_name"], str) or not item_data["product_name"]:
                return jsonify({"message": "Data error"}), 422

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

    items = OrderItem.query.filter_by(order_id=order_id).all()
    total = sum(i.quantity * i.unit_price for i in items)
    total += data["quantity"] * data["unit_price"]

    order = Order.query.get(order_id)
    order.total_amount = total

    db.session.commit()

    return jsonify({"message": "Item added", "total": total})