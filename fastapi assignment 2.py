from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# Sample Data
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

orders = []
feedback = []

# ======================
# Q1 Filter Products
# ======================

@app.get("/products/filter")
def filter_products(
    category: Optional[str] = None,
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = None
):

    result = products

    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]

    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    return {"products": result}


# ======================
# Q2 Product Price
# ======================

@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):

    for p in products:
        if p["id"] == product_id:
            return {"name": p["name"], "price": p["price"]}

    return {"error": "Product not found"}


# ======================
# Q3 Feedback
# ======================

class Feedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


@app.post("/feedback")
def submit_feedback(data: Feedback):

    feedback.append(data.dict())

    return {
        "message": "Feedback submitted",
        "total_feedback": len(feedback)
    }


# ======================
# Q4 Product Summary
# ======================

@app.get("/products/summary")
def product_summary():

    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]

    expensive = max(products, key=lambda p: p["price"])
    cheapest = min(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock": len(in_stock),
        "out_of_stock": len(out_stock),
        "most_expensive": expensive["name"],
        "cheapest": cheapest["name"]
    }


# ======================
# Q5 Bulk Order
# ======================

class OrderItem(BaseModel):
    product_id: int
    quantity: int


class BulkOrder(BaseModel):
    company_name: str
    contact_email: str
    items: List[OrderItem]


@app.post("/orders/bulk")
def bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    total = 0

    for item in order.items:

        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})

        elif not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": "Out of stock"})

        else:
            subtotal = product["price"] * item.quantity
            total += subtotal

            confirmed.append({
                "product": product["name"],
                "quantity": item.quantity,
                "subtotal": subtotal
            })

    return {
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": total
    }


# ======================
# BONUS Place Order
# ======================

class Order(BaseModel):
    product_id: int
    quantity: int


@app.post("/orders")
def place_order(order: Order):

    product = next((p for p in products if p["id"] == order.product_id), None)

    if not product:
        return {"error": "Product not found"}

    total = product["price"] * order.quantity

    new_order = {
        "order_id": len(orders) + 1,
        "product": product["name"],
        "quantity": order.quantity,
        "total_price": total
    }

    orders.append(new_order)

    return new_order
