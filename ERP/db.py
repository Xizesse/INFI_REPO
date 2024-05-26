import psycopg2
import psycopg2.extras
import sys
from classes.Order import Order
from classes.Raw_order import Raw_order
from classes.ProductionPlan import ProductionPlan, Prod_Quantities
from classes.PurchasingPlan import PurchasingPlan, Raw_material_arrivals

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

    if current_date:
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
            
            order_prod_plan = ProductionPlan(order_id, start_date, None, None)
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

        query = "SELECT * FROM infi.new_purchasing_plan ORDER BY arrival_date ASC"

        cursor.execute(query)
        results = cursor.fetchall() # Fetch all purchasing plan entries

        for row in results:
            
            arrival_date = row['arrival_date']
            quantity = row['quantity']
            workpiece = row['workpiece']
            supplier = row['supplier']
            price_pp = row['price_pp']
            delivery_days = row['delivery_days']
            min_quantity = row['min_quantity']

            raw_order = Raw_order(supplier, workpiece, min_quantity, price_pp, delivery_days)

            purchasing_plan_entry = PurchasingPlan(raw_order, arrival_date, quantity) 
            purchasing_plan.append(purchasing_plan_entry)

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        connect_to_db()

    cursor.close()

    return purchasing_plan

def get_raw_material_arrivals():

    global conn

    raw_material_arrivals = []

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = """SELECT 
                        arrival_date,
                        SUM(CASE WHEN workpiece = 'P1' THEN quantity ELSE 0 END) AS p1_quantity,
                        SUM(CASE WHEN workpiece = 'P2' THEN quantity ELSE 0 END) AS p2_quantity
                    FROM infi.new_purchasing_plan
                    GROUP BY arrival_date
                    ORDER BY arrival_date;"""

        cursor.execute(query)
        results = cursor.fetchall() # Fetch all raw material arrival entries

        for row in results:
            
            arrival_date = row['arrival_date']
            p1_quantity = row['p1_quantity']
            p2_quantity = row['p2_quantity']

            raw_material_arrival = Raw_material_arrivals(arrival_date, p1_quantity, p2_quantity)
            raw_material_arrivals.append(raw_material_arrival)

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        connect_to_db()

    cursor.close()

    return raw_material_arrivals

def insert_new_orders(new_orders):

    global conn
    
    cur = conn.cursor()

    # Create orders table
    try: 
        cur.execute('''CREATE TABLE IF NOT EXISTS infi.orders
                    (client TEXT,
                    number INTEGER NOT NULL PRIMARY KEY, 
                    workpiece TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    due_date INTEGER NOT NULL,
                    late_pen INTEGER,
                    early_pen INTEGER)
                    ''')
    except Exception as e:
        print("Error:", e)
        return []

    inserted_orders = []

    for order in new_orders:
        
        try:
            print(f"Inserting order {order.number}")
            cur.execute("INSERT INTO infi.orders VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (order.client, order.number, order.piece, order.quantity, order.due_date, order.late_pen, order.early_pen))
        except Exception as e:
            print("Error:", e)
            conn.rollback()
            continue

        else: 
            print(f"Order inserted: {order}")
            inserted_orders.append(order)
            conn.commit()

    return inserted_orders

def insert_production_plan(order_prod_plan):

    global conn

    cur = conn.cursor()

    try: 
        # Create the production_plan table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS infi.production_plan (
                order_id INTEGER REFERENCES infi.orders(number) PRIMARY KEY,
                start_date INTEGER NOT NULL
            );
        """)
    except Exception as e:
        print("Error:", e)
        conn.rollback()
        return

    
    # Insert the ordered data into the new table
    cur.execute("INSERT INTO infi.production_plan VALUES (%s, %s)", (order_prod_plan.order_id, order_prod_plan.start_date))

    # Commit changes 
    conn.commit()

def insert_purchasing_plan(purchase_plan):

    global conn
    
    if purchase_plan is None:
        return
        
    cur = conn.cursor()

    # Create the production_plan table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS infi.new_purchasing_plan (
            raw_order_id SERIAL PRIMARY KEY,
            arrival_date INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            workpiece TEXT NOT NULL,
            supplier TEXT NOT NULL,
            price_pp FLOAT NOT NULL,
            delivery_days INTEGER NOT NULL,
            min_quantity INTEGER NOT NULL
        );
    """)

    cur.execute("""
        INSERT INTO infi.new_purchasing_plan (
            arrival_date, 
            quantity, 
            workpiece, 
            supplier, 
            price_pp, 
            delivery_days, 
            min_quantity
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)""", 
        (purchase_plan.arrival_date, 
         purchase_plan.quantity, 
         purchase_plan.raw_order.piece, 
         purchase_plan.raw_order.supplier, 
         purchase_plan.raw_order.price_pp, 
         purchase_plan.raw_order.delivery_days, 
         purchase_plan.raw_order.min_quantity))
    
    conn.commit()

    #print("Purchasing schedule inserted into purchasing_plan table.")

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
        try: 
            cur.execute("DELETE FROM infi.todays_date")
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
        conn.commit()
        cur.close()
        close_db_connection()
        print("All tables cleared.")
        exit()
