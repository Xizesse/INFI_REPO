import psycopg2
import xml.etree.ElementTree as ET
from classes.order import Order

def parse_new_orders(new_orders_file):
    
    # Parse XML data from file
    tree = ET.parse(new_orders_file)
    root = tree.getroot()

    # Extract client data
    client_name = root.find('Client').get('NameId')

    new_orders = []
    
    for order in root.findall('Order'):
        new_order = Order.parse_order(order, client_name)
        new_orders.append(new_order)

    return new_orders



def insert_new_orders(conn, new_orders):

    cur = conn.cursor()

    # Create orders table
    cur.execute('''CREATE TABLE IF NOT EXISTS infi.orders
                 (client TEXT,
                 number INTEGER NOT NULL PRIMARY KEY, 
                 workpiece TEXT NOT NULL,
                 quantity INTEGER NOT NULL,
                 due_date INTEGER NOT NULL,
                 late_pen INTEGER,
                 early_pen INTEGER)
                ''')

    # Insert orders into the database
    for order in new_orders:
        cur.execute("INSERT INTO infi.orders VALUES (%s, %s, %s, %s, %s, %s, %s)",
                  (order.client, order.number, order.piece, order.quantity, order.due_date, order.late_pen, order.early_pen))  

    # Commit changes 
    conn.commit()

    print("Orders inserted into database.")
