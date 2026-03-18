from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI(title="FastAPI — Day 6 Assignment (Search, Sort, Paginate)")

# ==========================================
# INITIAL DATA
# ==========================================
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

# Pre-populated orders so you can test Q4 and Bonus immediately
orders = [
    {"order_id": 1, "customer_name": "Rahul Sharma", "product": "Wireless Mouse"},
    {"order_id": 2, "customer_name": "Anita Desai", "product": "Notebook"},
    {"order_id": 3, "customer_name": "Rahul Kumar", "product": "USB Hub"},
    {"order_id": 4, "customer_name": "Priya Singh", "product": "Pen Set"},
    {"order_id": 5, "customer_name": "Amit Patel", "product": "Wireless Mouse"}
]

# ==========================================
# ROOT ENDPOINT
# ==========================================
@app.get("/")
def home():
    return {
        "message": "Welcome to the Search & Pagination Assignment!", 
        "instruction": "Add /docs to the URL to see the Swagger UI testing page."
    }

# ==========================================
# BASE ENDPOINTS (For Q1, Q2, Q3)
# ==========================================

# --- Q1: Basic Search ---
@app.get('/products/search')
def basic_search(keyword: str):
    results = [p for p in products if keyword.lower() in p['name'].lower()]
    if not results:
        return {"message": f"No products found for: {keyword}"}
    return {"keyword": keyword, "total_found": len(results), "products": results}

# --- Q2: Basic Sort ---
@app.get('/products/sort')
def basic_sort(sort_by: str = "price", order: str = "asc"):
    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}
    reverse = (order == 'desc')
    result = sorted(products, key=lambda p: p[sort_by], reverse=reverse)
    return {"sort_by": sort_by, "order": order, "products": result}

# --- Q3: Basic Pagination ---
@app.get('/products/page')
def basic_page(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    return {
        "page": page,
        "limit": limit,
        "total_pages": -(-len(products) // limit),
        "products": products[start : start + limit]
    }


# ==========================================
# NEW ENDPOINTS (For Q4, Q5, Q6, Bonus)
# ==========================================

# --- Q4: Search the Orders List ---
@app.get('/orders/search')
def search_orders(customer_name: str = Query(..., description="Name to search for")):
    results = [
        o for o in orders
        if customer_name.lower() in o['customer_name'].lower()
    ]
    if not results:
        return {'message': f'No orders found for: {customer_name}'}
    return {'customer_name': customer_name, 'total_found': len(results), 'orders': results}


# --- Q5: Sort Products by Category Then Price ---
@app.get('/products/sort-by-category')
def sort_by_category():
    # Sorts first by category (A-Z), then by price (Low to High)
    result = sorted(products, key=lambda p: (p['category'], p['price']))
    return {'products': result, 'total': len(result)}


# --- Q6: Search + Sort + Paginate in One Endpoint ---
@app.get('/products/browse')
def browse_products(
    keyword: Optional[str] = Query(None),
    sort_by: str = Query('price'),
    order:   str = Query('asc'),
    page:    int = Query(1, ge=1),
    limit:   int = Query(4, ge=1, le=20),
):
    # Step 1: Search
    result = products
    if keyword:
        result = [p for p in result if keyword.lower() in p['name'].lower()]

    # Step 2: Sort
    if sort_by in ['price', 'name']:
        result = sorted(result, key=lambda p: p[sort_by], reverse=(order=='desc'))

    # Step 3: Paginate
    total  = len(result)
    start  = (page - 1) * limit
    paged  = result[start : start + limit]

    return {
        'keyword':     keyword, 
        'sort_by':     sort_by, 
        'order':       order,
        'page':        page,  
        'limit':       limit, 
        'total_found': total,
        'total_pages': -(-total // limit) if limit > 0 else 0,
        'products':    paged,
    }

# --- BONUS: Paginate the Orders List ---
@app.get('/orders/page')
def get_orders_paged(
    page:  int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=20),
):
    start = (page - 1) * limit
    return {
        'page':        page,
        'limit':       limit,
        'total':       len(orders),
        'total_pages': -(-len(orders) // limit),
        'orders':      orders[start : start + limit],
    }

# Make sure this catch-all dynamic route stays at the very bottom!
@app.get('/products/{product_id}')
def get_single_product(product_id: int):
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return {"error": "Product not found"}
    return product