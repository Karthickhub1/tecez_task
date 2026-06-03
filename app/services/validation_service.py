from app.utils.logger import logger

REQUIRED_ORDER_FIELDS = [
    "order_id",
    "customer",
    "line_items",
    "total"
]


def validate_order(order):

    for field in REQUIRED_ORDER_FIELDS:
        if field not in order:
            raise ValueError(f"Missing field: {field}")

    calculated_total = 0

    for item in order["line_items"]:

        qty = item.get("quantity")
        price = item.get("unit_price")

        if qty is None or price is None:
            raise ValueError("Invalid line item")

        if qty <= 0 or price <= 0:
            raise ValueError("Quantity/Price must be positive")

        calculated_total += qty * price

    given_total = order["total"]

    if round(calculated_total, 2) != round(given_total, 2):
        logger.error(
            f"Total mismatch Order={order['order_id']} "
            f"Expected={calculated_total} Given={given_total}"
        )

        raise ValueError("Order total mismatch")

    return calculated_total