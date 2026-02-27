from app.application.validators.order_validator import validate_order_items, validate_order_ownership
from app.infrastructure.database.db import db
from app.infrastructure.database.models import Order, OrderItem


def update_order(data, current_user, order_id):
    order = Order.query.get(order_id)
    validation_error = validate_order_ownership(order, current_user)
    if validation_error:
        return validation_error[0], validation_error[1]
    
    if order.status != "PENDING":
        return {"message": "Order cannot be update"}, 422
    
    try:
        validate_order_items(data)
    except ValueError as e:
        return {"error": str(e)}, 422
    
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
    return {"message": "Order updated succesfully", "total": total_amount}, 200


def create_order(current_user, data):
    try:
        validate_order_items(data)
    except ValueError as e:
        return {"error": str(e)}, 422
    
    order = Order(user_id=current_user.id)

    total_amount = 0

    for item_data in data["items"]:
        item_quantity = item_data["quantity"]
        item_price = item_data["unit_price"]
        item_amount = item_quantity * item_price
        total_amount += item_amount

        new_item = OrderItem(
            product_name=item_data["product_name"],
            quantity=item_quantity,
            unit_price=item_price,
        )

        order.items.append(new_item)

    order.total_amount = total_amount

    db.session.add(order)
    db.session.commit()

    return {"message": "Item added", "total": total_amount, "order_id": order.id}, 201


def list_orders(current_user):
    orders_user = Order.query.filter_by(user_id=current_user.id).all()

    orders_serialized = [
        {
            "id": order.id,
            "total_amount": order.total_amount
        }
        for order in orders_user
    ]

    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "orders": orders_serialized
    }, 200


def list_itens_in_orders(current_user, order_id):
    asking_order = Order.query.get(order_id)
    if not asking_order:
        return {"error": "Order not found"}, 404

    validation_error = validate_order_ownership(asking_order, current_user)
    if validation_error:
        return validation_error[0], validation_error[1]
    
    itens_serialized = [
        {
            "product_name": item.product_name,
            "quantity": item.quantity,
            "unit_price": item.unit_price
        }
        for item in asking_order.items
    ]
    
    return {
        "id": asking_order.id,
        "total_amount": asking_order.total_amount,
        "items": itens_serialized
    }, 200


def add_item(current_user, order_id, data):
    order = Order.query.get(order_id)

    if not order:
        return {"error": "Order not found"}, 404

    new_item = OrderItem(
        product_name=data["product_name"],
        quantity=data["quantity"],
        unit_price=data["unit_price"],
    )

    order.items.append(new_item)

    order.total_amount = sum(
        item.quantity * item.unit_price
        for item in order.items
    )

    db.session.commit()

    return {"message": "Item added", "total": order.total_amount}, 200

def delete_order(current_user, order_id):

    order = Order.query.get(order_id)

    if not order:
        return {"error": "Order not found"}, 404

    validation_error = validate_order_ownership(order, current_user)
    if validation_error:
        return validation_error[0], validation_error[1]

    db.session.delete(order)
    db.session.commit()

    return {"message": "Order deleted successfully"}, 200