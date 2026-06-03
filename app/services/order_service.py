import json

from app.database import orders_collection
from app.services.validation_service import validate_order
from app.services.pdf_service import generate_invoice
from app.utils.logger import logger
import os
DISCOUNT_THRESHOLD = float(os.getenv("DISCOUNT_THRESHOLD", 5000))
DISCOUNT_PERCENTAGE = float(os.getenv("DISCOUNT_PERCENTAGE", 10))

def process_orders(json_file):

    with open(json_file, "r") as file:
        data = json.load(file)

    processed_orders = []

    for order in data["orders"]:

        try:
            # Validate total
            subtotal = validate_order(order)

            # Apply discount
            discount = 0

            if subtotal > DISCOUNT_THRESHOLD:
                discount = subtotal * (DISCOUNT_PERCENTAGE / 100)

            final_amount = subtotal - discount

            # Generate PDF
            pdf_path = generate_invoice(
                order,
                subtotal,
                discount,
                final_amount
            )

            # Data to save in MongoDB
            mongo_doc = {
                "order_id": order["order_id"],
                "customer": order["customer"],
                "line_items": order["line_items"],
                "subtotal": subtotal,
                "discount": discount,
                "final_amount": final_amount,
                "invoice_path": pdf_path
            }

            result = orders_collection.insert_one(mongo_doc)

            # Response object (NO ObjectId)
            response_order = {
                "mongo_id": str(result.inserted_id),
                "order_id": order["order_id"],
                "subtotal": subtotal,
                "discount": discount,
                "final_amount": final_amount,
                "invoice_path": pdf_path
            }

            processed_orders.append(response_order)

            logger.info(
                f"Order processed successfully: {order['order_id']}"
            )

        except Exception as e:

            logger.error(
                f"Order processing failed: {order.get('order_id')} - {str(e)}"
            )

    return processed_orders