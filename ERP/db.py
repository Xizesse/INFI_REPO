import psycopg2
import psycopg2.extras
import sys
from classes.order import Order
from classes.raw_order import Raw_order
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

def get_raw_order_leftovers(workpiece):

    global conn

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        #Leftover per raw_order_id
        query = """SELECT raw_order_id, SUM(quantity) - SUM(used_quantity) AS leftover  
           FROM infi.raw_order_plan
           JOIN infi.new_purchasing_plan USING(raw_order_id)
           WHERE workpiece = %s
           GROUP BY raw_order_id"""

        cursor.execute(query, (workpiece,))

        raw_order_leftovers = cursor.fetchall() # Fetch all raw order plan entries

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        connect_to_db()
        return []

    cursor.close()

    return raw_order_leftovers

def get_order(order_id):

    global conn

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = """SELECT * FROM infi.orders WHERE number = %s"""

        cursor.execute(query, (order_id,))

        order = cursor.fetchone()

        order = Order(order['client'], order['number'], order['workpiece'], order['quantity'], order['due_date'], order['late_pen'], order['early_pen'])

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        connect_to_db()
        return None

    cursor.close()

    return order

def get_dispatch_date(order_id):

    global conn

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = """SELECT dispatch_date FROM infi.dispatches WHERE order_id = %s"""

        cursor.execute(query, (order_id,))

        dispatch_date = cursor.fetchone()

        if dispatch_date:
            dispatch_date = int(dispatch_date[0])

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        connect_to_db()
        return None

    cursor.close()

    return dispatch_date

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
        return None
        
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
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING raw_order_id;
    """, 
    (purchase_plan.arrival_date, 
     purchase_plan.quantity, 
     purchase_plan.raw_order.piece, 
     purchase_plan.raw_order.supplier, 
     purchase_plan.raw_order.price_pp, 
     purchase_plan.raw_order.delivery_days, 
     purchase_plan.raw_order.min_quantity))
    
    new_id = cur.fetchone()[0]  # Fetching the returned primary key value
    conn.commit()

    return new_id

def insert_raw_order_plan(raw_order_plan):

    global conn

    cur = conn.cursor()

    # Create the production_plan table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS infi.raw_order_plan (
            plan_id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES infi.orders(number) NOT NULL,
            raw_order_id INTEGER REFERENCES infi.new_purchasing_plan(raw_order_id) NOT NULL,
            used_quantity INTEGER NOT NULL
        );
    """)

    # Insert the ordered data into the new table
    cur.execute("INSERT INTO infi.raw_order_plan (order_id, raw_order_id, used_quantity) VALUES (%s, %s, %s)", 
                (raw_order_plan.order_id, raw_order_plan.raw_order_id, raw_order_plan.used_quantity))

    # Commit changes 
    conn.commit()

def update_raw_order_plan(plan_id, new_used_quantity):

    global conn

    cur = conn.cursor()

    # Create the production_plan table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS infi.raw_order_plan (
            plan_id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES infi.orders(number) NOT NULL,
            raw_order_id INTEGER REFERENCES infi.new_purchasing_plan(raw_order_id) NOT NULL,
            used_quantity INTEGER NOT NULL
        );
    """)

    try:
        cur.execute("UPDATE infi.raw_order_plan SET used_quantity = %s WHERE plan_id = %s", (new_used_quantity, plan_id))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        conn.rollback()

    cur.close()

def check_dispatched_orders(current_date):
    global conn

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = """SELECT order_id FROM infi.dispatches
                WHERE dispatch_date = %s"""

        cursor.execute(query, (current_date,))

        dispatched_orders = cursor.fetchall()

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        connect_to_db()
        return []

    cursor.close()

    return dispatched_orders

def insert_costs(order_id, total_cost, unit_cost):

    global conn

    cur = conn.cursor()
    
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS infi.order_costs (
                order_id INTEGER REFERENCES infi.orders(number) PRIMARY KEY,
                total_cost FLOAT NOT NULL,
                unit_cost FLOAT NOT NULL
            );
        """)
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        conn.rollback()

    try:   
        cur.execute("INSERT INTO infi.order_costs VALUES (%s, %s, %s)", (order_id, total_cost, unit_cost))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        conn.rollback()

    cur.close()

def clear_all_tables():
    
    connection = connect_to_db()

    cur = connection.cursor()

    try: 
        cur.execute("DELETE FROM infi.raw_order_plan")
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    try:
        cur.execute("DELETE FROM infi.new_purchasing_plan")
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

    try:
        cur.execute("DELETE FROM infi.order_costs")
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    
    try: 
        cur.execute("DELETE FROM infi.dispatches")
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        conn.rollback()

    connection.commit()
    cur.close()
    connection.close()