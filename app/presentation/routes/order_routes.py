from flask import Blueprint, request, jsonify
from sqlalchemy import null
from app.application.services.order_service import (
    update_order, 
    create_order as create_order_service, 
    list_orders as list_orders_service, 
    list_itens_in_orders as list_itens_in_orders_services, 
    add_item as add_item_service,
    delete_order as delete_order_service)
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
def add_item(current_user, order_id):

    data = request.json

    result, status = add_item_service(current_user, order_id, data)
    return jsonify(result), status


@order_bp.route("/orders/<int:order_id>", methods=["DELETE"])
@token_required
def delete_order(current_user, order_id):

    result, status = delete_order_service(current_user, order_id)
    return jsonify(result), status

@order_bp.route("/orders/<int:order_id>", methods=["PUT"])
@token_required
def update_item_in_orders(current_user, order_id):

    data = request.json

    result, status = update_order(data, current_user, order_id)
    return jsonify(result), status