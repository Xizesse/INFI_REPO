import psycopg2
import psycopg2.extras
import sys
from classes.Order import Order
from classes.ProductionPlan import ProductionPlan, Prod_Quantities
from classes.PurchasingPlan import PurchasingPlan

DB_CONFIG = {
    "host": "db.fe.up.pt",
    "database": "infind202410",
    "user": "infind202410",
    "password": "DWHyIHTiPP"
}

conn = None

def connect_to_db():

    global conn

    while True:
        try:
            conn = psycopg2.connect(
                host=DB_CONFIG['host'],
                database=DB_CONFIG['database'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password']
            )
        except psycopg2.Error as e:
            print(f"Error connecting to the database: {e}")
            continue
        else :
            print("Connected to the database.")
            break
    return conn

def close_db_connection():
    global conn
    conn.close()

def get_current_date():

    global conn
    cur = conn.cursor()

    query = """
        SELECT date
        FROM infi.todays_date
    """

    try: 
        cur.execute(query)
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        connect_to_db()        

    #Fetch current date
    current_date = cur.fetchone()
    current_date = int(current_date[0])

    return current_date

def get_orders():

    global conn
  
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    query = """SELECT client, number, workpiece, quantity, due_date, late_pen, early_pen
            FROM infi.orders 
            ORDER BY due_date ASC;"""

    try:
        cursor.execute(query)
        results = cursor.fetchall() # Fetch all orders

        orders = []

        for row in results:
            
            client = row['client']
            number = row['number']
            piece = row['workpiece']
            quantity = int(row['quantity'])
            due_date = row['due_date']
            late_pen = row['late_pen']
            early_pen = row['early_pen']
            
            order = Order(client, number, piece, quantity, due_date, late_pen, early_pen)
            orders.append(order)
            
    
    except Exception as e:
        print(f"An error occurred: {e}")
        connect_to_db()
        cursor.close()
        return None
    else:
        cursor.close()
        return orders

def get_production_plan():

    global conn

    production_plan = []

    try:

        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = "SELECT * FROM infi.production_plan ORDER BY start_date ASC"

        cursor.execute(query)
        results = cursor.fetchall() # Fetch all production plan entries

        for row in results:
            
            order_id = row['order_id']
            start_date = row['start_date']
            
            order_prod_plan = ProductionPlan(order_id, start_date)
            production_plan.append(order_prod_plan)

    except Exception as e:
        print(f"An error occurred: {e}")
        connect_to_db()
    
    cursor.close()

    return production_plan

def get_prod_quantities():
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = """SELECT 
                start_date,
                SUM(CASE WHEN workpiece = 'P5' THEN quantity ELSE 0 END) AS p5_quantity,
                SUM(CASE WHEN workpiece = 'P6' THEN quantity ELSE 0 END) AS p6_quantity,
                SUM(CASE WHEN workpiece = 'P7' THEN quantity ELSE 0 END) AS p7_quantity,
                SUM(CASE WHEN workpiece = 'P9' THEN quantity ELSE 0 END) AS p9_quantity
            FROM infi.production_plan
            JOIN infi.orders ON order_id = number
            GROUP BY start_date
            ORDER BY start_date;"""

        cursor.execute(query)
        results = cursor.fetchall() # Fetch all production plan entries

        prod_quantities = []
        for row in results:
            
            start_date = row['start_date']
            p5_quantity = row['p5_quantity']
            p6_quantity = row['p6_quantity']
            p7_quantity = row['p7_quantity']
            p9_quantity = row['p9_quantity']

            prod_quantities_day = Prod_Quantities(start_date, p5_quantity, p6_quantity, p7_quantity, p9_quantity)
            prod_quantities.append(prod_quantities_day)
            
    except Exception as e:
        print(f"An error occurred: {e}")
        connect_to_db()
        return None
    
    return prod_quantities

def get_purchasing_plan():

    global conn

    purchasing_plan = []

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = "SELECT * FROM infi.purchasing_plan ORDER BY arrival_date ASC"

        cursor.execute(query)
        results = cursor.fetchall() # Fetch all purchasing plan entries

        for row in results:
            
            arrival_date = row['arrival_date']
            p1_quantity = row['p1_quantity']
            p2_quantity = row['p2_quantity']

            purchasing_plan_entry = PurchasingPlan(arrival_date, p1_quantity, p2_quantity)
            purchasing_plan.append(purchasing_plan_entry)

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        connect_to_db()

    cursor.close()

    return purchasing_plan


# Example usage:
if __name__ == "__main__":

    if sys.argv[1] == "delete":
        conn = connect_to_db()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM infi.purchasing_plan")
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
        try:
            cur.execute("DELETE FROM infi.production_plan")
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
        try:
            cur.execute("DELETE FROM infi.orders")
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
        conn.commit()
        cur.close()
        close_db_connection()
        print("All tables cleared.")
        exit()

    connect_to_db()

    orders = get_orders()
    for order in orders:
        print(f" Client: {order.client}, Order ID: {order.number}, Quantity: {order.quantity}, Type: {order.piece}, Delivery Date: {order.due_date}, Late Penalty: {order.late_pen}, Early Penalty: {order.early_pen}")

    production_plan = get_production_plan()
    for entry in production_plan:
        print(f" Order ID: {entry.order_id}, Start Date: {entry.start_date}")

    purchasing_plan = get_purchasing_plan()
    for entry in purchasing_plan:
        print(f" Arrival Date: {entry.arrival_date}, P1 Quantity: {entry.p1_quantity}, P2 Quantity: {entry.p2_quantity}")

    current_date = get_current_date()
    print(f"Current Date: {current_date}")

    close_db_connection()