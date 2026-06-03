from fastapi import FastAPI, HTTPException

from app.services.order_service import process_orders
from app.models import CustomerCreate, ProductCreate, OrderCreate
from app.services.pdf_service import generate_invoice
from app.services.validation_service import validate_order
from app.utils.logger import logger
from app.database import (
    customers_collection,
    products_collection,
    orders_collection
)
import os
DISCOUNT_THRESHOLD = float(os.getenv("DISCOUNT_THRESHOLD", 5000))
DISCOUNT_PERCENTAGE = float(os.getenv("DISCOUNT_PERCENTAGE", 10))

app = FastAPI(
    title="ERP Sales Order Processor"
)


@app.post("/process-orders")
def process_sales_orders():

    result = process_orders(
        "salesorders_data.json"
    )

    return {
        "message": "Orders processed successfully",
        "processed_orders": len(result),
        "orders": result
    }

@app.post("/create_customer")
def create_customer(customer: CustomerCreate):

    customers_collection.insert_one(customer.dict())

    return {
        "message": "Customer created successfully"
    }

@app.post("/create_product")
def create_product(product: ProductCreate):

    products_collection.insert_one(product.dict())

    return {
        "message": "Product created successfully"
    }

@app.post("/create_order")
async def create_order(order: OrderCreate):

    try:

        # Customer Validation
        customer = customers_collection.find_one(
            {"customer_id": order.customer_id}
        )

        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        total = 0
        order_items = []

        # Product Validation & Total Calculation
        for item in order.line_items:

            product = products_collection.find_one(
                {"item_id": item.item_id}
            )

            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product {item.item_id} not found"
                )

            amount = item.quantity * product["unit_price"]

            total += amount

            order_items.append({
                "item_id": product["item_id"],
                "description": product["description"],
                "quantity": item.quantity,
                "unit_price": product["unit_price"]
            })

        # Build Validation Object
        validation_order = {
            "order_id": order.order_id,
            "customer": {
                "name": customer["name"],
                "address": customer["address"],
                "email": customer["email"],
                "contact": customer["contact"]
            },
            "line_items": order_items,
            "total": total
        }

        # Reuse Existing Validation Logic
        subtotal = validate_order(validation_order)

        # Discount Logic
        discount = 0

        if subtotal > DISCOUNT_THRESHOLD:
            discount = round(
                subtotal * (DISCOUNT_PERCENTAGE / 100),
                2
            )

        final_amount = round(
            subtotal - discount,
            2
        )

        # Generate PDF Invoice
        pdf_path = generate_invoice(
            validation_order,
            subtotal,
            discount,
            final_amount
        )

        # Mongo Document
        order_doc = {
            "order_id": order.order_id,
            "customer_id": order.customer_id,
            "customer": validation_order["customer"],
            "line_items": order_items,
            "subtotal": subtotal,
            "discount": discount,
            "final_amount": final_amount,
            "invoice_path": pdf_path
        }

        result = orders_collection.insert_one(
            order_doc
        )

        logger.info(
            f"Order created successfully: {order.order_id}"
        )

        return {
            "message": "Order created successfully",
            "mongo_id": str(result.inserted_id),
            "order_id": order.order_id,
            "subtotal": subtotal,
            "discount": discount,
            "final_amount": final_amount,
            "invoice_path": pdf_path
        }

    except HTTPException:
        raise

    except Exception as e:

        logger.error(
            f"Create Order Failed - {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )