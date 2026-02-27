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
