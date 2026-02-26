from flask import Blueprint, request, jsonify
from sqlalchemy import null
from app.application.services.order_validator import validate_order_items, validate_order_ownership
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

    orders_serialized = [
        {
            "id": order.id,
            "total_amount": order.total_amount
        }
        for order in orders_user
    ]

    return jsonify({
        "user_id": current_user.id,
        "email": current_user.email,
        "orders": orders_serialized
    })

@order_bp.route("/orders/<int:order_id>", methods=["GET"])
@token_required
def list_itens_in_orders(current_user, order_id):

    asking_order = Order.query.get(order_id)

    validation_error = validate_order_ownership(asking_order, current_user)
    if validation_error:
        return jsonify(validation_error[0]), validation_error[1]

    itens = OrderItem.query.filter_by(order_id=asking_order.id).all()
    
    itens_serialized = [
        {
            "product_name": item.product_name,
            "quantity": item.quantity,
            "unit_price": item.unit_price
        }
        for item in itens
    ]

    return jsonify({
        "id": asking_order.id,
        "total_amount": asking_order.total_amount,
        "items": itens_serialized
    })


@order_bp.route("/orders/<int:order_id>/items", methods=["POST"])
@token_required
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

@order_bp.route("/orders/<int:order_id>", methods=["DELETE"])
@token_required
def delete_order(current_user, order_id):

    order = Order.query.get(order_id)

    validation_error = validate_order_ownership(order, current_user)
    if validation_error:
        return jsonify(validation_error[0]), validation_error[1]

    db.session.delete(order)
    db.session.commit()

    return jsonify({"message": "Order deleted sucessfully"}), 200

@order_bp.route("/orders/<int:order_id>", methods=["PUT"])
@token_required
def update_item_in_orders(current_user, order_id):

    data = request.json
    try:
        validate_order_items(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 422

    order = Order.query.get(order_id)
    validation_error = validate_order_ownership(order, current_user)
    if validation_error:
        return jsonify(validation_error[0]), validation_error[1]
    
    if order.status != "PENDING":
        return jsonify({"message": "Order cannot be update"}), 422

    order.items.clear()

    total_amount = 0
    for item_data in data["items"]:
        item_quantity = item_data["quantity"]
        item_price = item_data["unit_price"]
        item_amount = item_quantity * item_price
        total_amount += item_amount
        new_item = OrderItem(
            product_name=item_data["product_name"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
        )

        order.items.append(new_item)

    order.total_amount = total_amount

    db.session.commit()

    return jsonify({"message": "Order updated successfully", "total": total_amount})
