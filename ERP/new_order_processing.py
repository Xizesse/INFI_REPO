import psycopg2
import xml.etree.ElementTree as ET

def process_new_order():
    
    # Parse XML data from file
    tree = ET.parse('new_order.xml')
    root = tree.getroot()

    # Extract client data
    client_name = root.find('Client').get('NameId')

    # Extract orders from XML
    orders = []
    for order_elem in root.findall('Order'):
        order = {
            'client': client_name,
            'number': order_elem.get('Number'),
            'workpiece': order_elem.get('WorkPiece'),
            'quantity': int(order_elem.get('Quantity')),
            'due_date': int(order_elem.get('DueDate')),
            'late_pen': int(order_elem.get('LatePen')),
            'early_pen': int(order_elem.get('EarlyPen')),
        }
        orders.append(order)

    # Establish connection to PostgreSQL database
    conn = psycopg2.connect(
        host='db.fe.up.pt',
        database='infind202410',
        user='infind202410',
        password='DWHyIHTiPP'
    )

    cur = conn.cursor()

    # Create orders table
    cur.execute('''CREATE TABLE IF NOT EXISTS infi.orders
                 (client TEXT, number TEXT, workpiece TEXT, quantity INTEGER, due_date INTEGER,
                 late_pen INTEGER, early_pen INTEGER)''')

    # Insert orders into the database
    for order in orders:
        cur.execute("INSERT INTO INFI.orders VALUES (%s, %s, %s, %s, %s, %s, %s)",
                  (order['client'], 
                   order['number'],
                   order['workpiece'],
                   order['quantity'],
                   order['due_date'], 
                   order['late_pen'], 
                   order['early_pen']))  

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print("Orders inserted into database.")