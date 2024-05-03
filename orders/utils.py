import uuid
import random
from datetime import datetime

def generate_order_number():
    """Generate a unique 6 character order number"""
    return str(random.randint(100000, 999999))

def generate_order_name(order_number):
    """Generate a name for the order using the order number"""
    return f'Order {order_number}'

def generate_order_description(order_items):
    """Generate a description for the order with the current date and time, item names, and quantities"""
    item_descriptions = [f"{item.product.title} (Quantity: {item.quantity})" for item in order_items]
    item_descriptions_str = ", ".join(item_descriptions)
    return f'Order created on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}. Items ordered: {item_descriptions_str}'