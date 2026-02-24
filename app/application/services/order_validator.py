def validate_order_items(data):
    if "items" not in data or not isinstance(data["items"], list) or not data["items"]:
        raise ValueError("Items must be a non-empty list")

    for item in data["items"]:
        if "quantity" not in item or not isinstance(item["quantity"], int) or item["quantity"] <= 0:
            raise ValueError("Invalid quantity")

        if "unit_price" not in item or not isinstance(item["unit_price"], (int, float)) or item["unit_price"] <= 0:
            raise ValueError("Invalid unit price")

        if "product_name" not in item or not isinstance(item["product_name"], str) or not item["product_name"].strip():
            raise ValueError("Invalid product name")
        
def validate_order_ownership(order, current_user):
    if order is None:
        return {"message": "Order doesn't exist"}, 404
    # Necessário implementar caso a ordem nao exista 403
    if order.user_id != current_user.id:
        return {"message": "User don't have this order"}, 403
    
    return None