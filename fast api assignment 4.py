from fastapi import FastAPI, Query, Response, status, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

 

# ══ PYDANTIC MODELS ═══════════════════════════════════════════════

 

class OrderRequest(BaseModel):                          # Day 2
    customer_name:    str = Field(..., min_length=2, max_length=100)
    product_id:       int = Field(..., gt=0)
    quantity:         int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)

 

class NewProduct(BaseModel):                            # Day 4
    name:     str  = Field(..., min_length=2, max_length=100)
    price:    int  = Field(..., gt=0)
    category: str  = Field(..., min_length=2)
    in_stock: bool = True

class CheckoutRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2, max_length=100)
    delivery_address: str = Field(..., min_length=10)

@app.get("/cart")
def view_cart():
    grand_total = sum(item["subtotal"] for item in cart)
    return{"cart":cart, "grand_total": grand_total}



 

# ══ DATA ══════════════════════════════════════════════════════════

 

products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'stock': 20},
    {'id': 2, 'name': 'Notebook',       'price':  99, 'category': 'Stationery',  'stock': 15},
    {'id': 3, 'name': 'USB Hub',        'price': 799, 'category': 'Electronics', 'stock': 0},
    {'id': 4, 'name': 'Pen Set',        'price':  49, 'category': 'Stationery',  'stock': 30},

]

 

orders        = []
order_counter = 1

cart=[]

 

# ══ HELPER FUNCTIONS ══════════════════════════════════════════════

 

def find_product(product_id: int):
    """Search products list by ID. Returns product dict or None."""
    for p in products:
        if p['id'] == product_id:
            return p
    return None

 

def calculate_total(product: dict, quantity: int) -> int:
    """Multiply price by quantity and return total."""
    return product['price'] * quantity

 

def filter_products_logic(category=None, min_price=None,
                          max_price=None, in_stock=None):
    """Apply filters and return matching products."""
    result = products
    if category  is not None:
        result = [p for p in result if p['category'] == category]
    if min_price is not None:
        result = [p for p in result if p['price'] >= min_price]
    if max_price is not None:
        result = [p for p in result if p['price'] <= max_price]
    if in_stock  is not None:
        result = [p for p in result if p['in_stock'] == in_stock]
    return result

 

# ══ ENDPOINTS ═════════════════════════════════════════════════════

@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}

@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}

 
@app.get('/products/filter')
def filter_products(
    category:  str  = Query(None, description='Electronics or Stationery'),
    min_price: int  = Query(None, description='Minimum price'),
    max_price: int  = Query(None, description='Maximum price'),
    in_stock:  bool = Query(None, description='True = in stock only'),

):
    result = filter_products_logic(category, min_price, max_price, in_stock)
    return {'filtered_products': result, 'count': len(result)}

 
@app.get('/products/compare')
def compare_products(
    product_id_1: int = Query(..., description='First product ID'),
    product_id_2: int = Query(..., description='Second product ID'),

):
    p1 = find_product(product_id_1)
    p2 = find_product(product_id_2)
    if not p1:
        return {'error': f'Product {product_id_1} not found'}
    if not p2:
        return {'error': f'Product {product_id_2} not found'}
    cheaper = p1 if p1['price'] < p2['price'] else p2
    return {
        'product_1':    p1,
       'product_2':    p2,
        'better_value': cheaper['name'],
        'price_diff':   abs(p1['price'] - p2['price']),
    }

 

@app.post('/products')
def add_product(new_product: NewProduct, response: Response):
    # Check for duplicate name (case-insensitive)
    existing_names = [p['name'].lower() for p in products]
    if new_product.name.lower() in existing_names:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Product with this name already exists'}


    next_id = max(p['id'] for p in products) + 1
    product = {
        'id':       next_id,
        'name':     new_product.name,
        'price':    new_product.price,
        'category': new_product.category,
        'stock': new_product.stock,
    }
    products.append(product)
    response.status_code = status.HTTP_201_CREATED
    return {'message': 'Product added', 'product': product}

 

@app.put('/products/{product_id}')
def update_product(

   product_id: int,
    response:   Response,
    stock:   bool = Query(None, description='Update stock status'),
    price:      int  = Query(None, description='Update price'),

):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}

 
    if stock is not None:     # must use 'is not None' — False is a valid value
        product['stock'] = stock
    if price is not None:
        product['price'] = price

    return {'message': 'Product updated', 'product': product}

@app.delete('/products/{product_id}')
def delete_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}

    products.remove(product)
    return {'message': f"Product '{product['name']}' deleted"}

@app.get('/products/{product_id}')
def get_product(product_id: int):
    product = find_product(product_id)
    if not product:
        return {'error': 'Product not found'}
    return {'product': product}

 

@app.post('/orders')
def place_order(order_data: OrderRequest):
    global order_counter

    product = find_product(order_data.product_id)
    if not product:
        return {'error': 'Product not found'}
    if not product['stock']:
        return {'error': f"{product['name']} is out of stock"}

    total = calculate_total(product, order_data.quantity)
    order = {
        'order_id':         order_counter,
        'customer_name':    order_data.customer_name,
        'product':          product['name'],
        'quantity':         order_data.quantity,
        'delivery_address': order_data.delivery_address,
        'total_price':      total,
        'status':           'confirmed',
    }
    orders.append(order)
    order_counter += 1
    return {'message': 'Order placed successfully', 'order': order}

@app.get('/orders')
def get_all_orders():
    return {'orders': orders, 'total_orders': len(orders)}


#Question: 1

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int):
    product = next((p for p in products if p['id'] == product_id), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product["stock"] == 0:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")
    
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * product["price"]

            return {
                "message": "Cart updated",
                "cart_item": item
            }

    subtotal = quantity * product["price"]

    cart_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": subtotal
    }

    cart.append(cart_item)

    return {
        "message": "Added to cart",
        "cart_item": cart_item
    }
    
#Question :2
@app.get("/cart")
def view_cart():
    total_amount = sum(item["subtotal"] for item in cart)
    return {
        "cart_items": cart,
        "total_amount": total_amount
    }


#Question: 5
@app.delete("/cart/remove/{item_id}")
def remove_item(item_id: int):
    for item in cart:
        if item["id"] == item["id"]:
            cart.remove(item)
            return {
                "message": "Item removed successfully ✅",
                "remaining_cart": cart
            }

    return {"message": "Item not found in cart ❌"}

@app.post("/checkout")
def checkout():
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty 🛒")

    
    total = sum(item.price for item in cart)

    # Clear cart after checkout
    cart.clear()

    return {
        "message": "Checkout successful 🎉",
        "total_amount": total
    }

