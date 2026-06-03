from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

import os

os.makedirs("invoices", exist_ok=True)


def generate_invoice(order, subtotal, discount, final_amount):

    pdf_file = f"invoices/{order['order_id']}.pdf"

    doc = SimpleDocTemplate(pdf_file)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            f"<b>Invoice - {order['order_id']}</b>",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 10))

    customer = order["customer"]

    elements.append(
        Paragraph(
            f"""
            <b>Customer:</b> {customer['name']}<br/>
            <b>Contact:</b> {customer['contact']}<br/>
            <b>Email:</b> {customer['email']}<br/>
            <b>Address:</b> {customer['address']}
            """,
            styles["BodyText"]
        )
    )

    elements.append(Spacer(1, 10))

    data = [
        ["Item", "Description", "Qty", "Price", "Amount"]
    ]

    for item in order["line_items"]:

        amount = item["quantity"] * item["unit_price"]

        data.append([
            item["item_id"],
            item["description"],
            item["quantity"],
            f"${item['unit_price']:.2f}",
            f"${amount:.2f}"
        ])

    table = Table(data)

    table.setStyle(
        TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)
        ])
    )

    elements.append(table)

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"""
            <b>Subtotal:</b> ${subtotal:.2f}<br/>
            <b>Discount:</b> ${discount:.2f}<br/>
            <b>Final Amount:</b> ${final_amount:.2f}
            """,
            styles["BodyText"]
        )
    )

    doc.build(elements)

    return pdf_file