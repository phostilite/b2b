import uuid
from datetime import datetime

def generate_order_number():
    """Generate a unique order number"""
    return str(uuid.uuid4())

def generate_order_name(order_number):
    """Generate a name for the order using the order number"""
    return f'Order {order_number}'

def generate_order_description():
    """Generate a description for the order with the current date and time"""
    return f'Order created on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'