from flask import Blueprint, request, jsonify
from sqlalchemy import null
from app.application.services.order_service import update_order
from app.application.services.order_service import create_order as create_order_service
from app.application.services.order_service import list_orders as list_orders_service
from app.application.services.order_service import list_itens_in_orders as list_itens_in_orders_services
from app.application.validators.order_validator import validate_order_items, validate_order_ownership
from app.infrastructure.database.db import db
from app.infrastructure.database.models import Order, OrderItem
from app.infrastructure.security.auth_middleware import token_required

order_bp = Blueprint("orders", __name__)

@order_bp.route("/orders", methods=["POST"])
@token_required
def create_order(current_user):
    data = request.json

    result, status = create_order_service(current_user, data)
    return jsonify(result), status


@order_bp.route("/orders", methods=["GET"])
@token_required
def list_orders(current_user):
    result, status = list_orders_service(current_user)
    return jsonify(result), status

@order_bp.route("/orders/<int:order_id>", methods=["GET"])
@token_required
def list_itens_in_orders(current_user, order_id):

    result, status = list_itens_in_orders_services(current_user, order_id)
    return jsonify(result), status


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

    result, status = update_order(data, current_user, order_id)
    return jsonify(result), status