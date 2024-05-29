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

def connect_to_db():

    conn = None

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
            break
    return conn

def execute_query(query, params=None, fetch_all=True):

    conn = connect_to_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    while True:
        try:
            if params is not None:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if fetch_all:
                results = cursor.fetchall()
            else:
                results = cursor.fetchone()
            break

        except psycopg2.InterfaceError as e:    
            print(f"Error: {e}")
            conn = connect_to_db()
            cursor = conn.cursor()
            continue

        except psycopg2.OperationalError as e:
            print(f"Operational Error: {e}")
            conn = connect_to_db()
            cursor = conn.cursor()
            continue
            
        except Exception as e:
            print(f"An error occurred: {e}")
            results = []
            break

    conn.commit()
    cursor.close()
    conn.close()

    return results

def get_current_date():

    conn = connect_to_db()
    cur = conn.cursor()
    
    try:

        query = """
            SELECT date
            FROM infi.todays_date
        """

        cur.execute(query)

        # Fetch current date
        current_date = cur.fetchone()

        if current_date:
            current_date = int(current_date[0])
        else:
            current_date = 0

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        current_date = None

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return current_date

def get_orders():

    conn = connect_to_db()
  
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    query = """SELECT client, number, workpiece, quantity, due_date, late_pen, early_pen
            FROM infi.orders 
            ORDER BY due_date ASC;"""

    try:
        cur.execute(query)
        results = cur.fetchall() # Fetch all orders

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
        orders = None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return orders

def get_production_plan():

    conn = connect_to_db()

    production_plan = []

    try:

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = "SELECT * FROM infi.production_plan ORDER BY start_date ASC"

        cur.execute(query)
        results = cur.fetchall() # Fetch all production plan entries

        for row in results:
            
            order_id = row['order_id']
            start_date = row['start_date']
            
            order_prod_plan = ProductionPlan(order_id, start_date, None, None)
            production_plan.append(order_prod_plan)

    except Exception as e:
        print(f"An error occurred: {e}")
        production_plan = None
    
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return production_plan

def get_prod_quantities():

    conn = connect_to_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

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

        cur.execute(query)
        results = cur.fetchall() # Fetch all production plan entries

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
        prod_quantities = None
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    return prod_quantities

def get_purchasing_plan():

    conn = connect_to_db()

    purchasing_plan = []

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = "SELECT * FROM infi.purchasing_plan ORDER BY arrival_date ASC"

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
        purchasing_plan = None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return purchasing_plan

def get_raw_material_arrivals():

    conn = connect_to_db()

    raw_material_arrivals = []

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = """SELECT 
                        arrival_date,
                        SUM(CASE WHEN workpiece = 'P1' THEN quantity ELSE 0 END) AS p1_quantity,
                        SUM(CASE WHEN workpiece = 'P2' THEN quantity ELSE 0 END) AS p2_quantity
                    FROM infi.purchasing_plan
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
        raw_material_arrivals = None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return raw_material_arrivals

def get_raw_order_leftovers(workpiece):

    conn = connect_to_db()

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        #Leftover per raw_order_id
        query = """SELECT raw_order_id, SUM(quantity) - SUM(used_quantity) AS leftover  
           FROM infi.raw_order_plan
           JOIN infi.purchasing_plan USING(raw_order_id)
           WHERE workpiece = %s
           GROUP BY raw_order_id"""

        cursor.execute(query, (workpiece,))

        raw_order_leftovers = cursor.fetchall() # Fetch all raw order plan entries

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        raw_order_leftovers = None
        return []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return raw_order_leftovers

def get_order(order_id):

    conn = connect_to_db()

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = """SELECT * FROM infi.orders WHERE number = %s"""

        cursor.execute(query, (order_id,))

        order = cursor.fetchone()

        order = Order(order['client'], order['number'], order['workpiece'], order['quantity'], order['due_date'], order['late_pen'], order['early_pen'])

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        order = None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return order

def get_dispatch_date(order_id):

    conn = connect_to_db()

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = """SELECT dispatch_date FROM infi.dispatches WHERE order_id = %s"""

        cursor.execute(query, (order_id,))

        dispatch_date = cursor.fetchone()

        if dispatch_date:
            dispatch_date = int(dispatch_date[0])

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        dispatch_date = None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return dispatch_date

def check_dispatched_orders(current_date):
    
    conn = connect_to_db()

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
    conn.close()

    return dispatched_orders

def dispatches():
    
    conn = connect_to_db()

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = """SELECT order_id, dispatch_date FROM infi.dispatches
                   ORDER BY dispatch_date ASC"""

        cursor.execute(query)

        dispatched_orders = cursor.fetchall()

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []

    finally:
        cursor.close()
        conn.close()

    return dispatched_orders

def insert_new_orders(new_orders):

    conn = connect_to_db()
    cur = conn.cursor()

    # Create orders table
    while True:
        try:
            cur.execute("""CREATE TABLE IF NOT EXISTS infi.orders (
                client TEXT NOT NULL,
                number INTEGER PRIMARY KEY,
                workpiece TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                due_date INTEGER NOT NULL,
                late_pen INTEGER NOT NULL,
                early_pen INTEGER NOT NULL
            );
            """)
            break
        except psycopg2.InterfaceError as e:        # Error like "server closed unexpectedly"
            print(f"Error: {e}")
            conn = connect_to_db()                  #Connect to db again
            cur = conn.cursor()
        
        except psycopg2.OperationalError as e:      
            print(f"Operational Error: {e}")
            conn = connect_to_db()
            cur = conn.cursor()

        except Exception as e:  # Error like duplicate pkey -> ignore order
                print("Error:", e)
                conn.rollback()     
                break
        
    conn.commit()

    inserted_orders = []

    for order in new_orders:

        while True:
            try:
                print(f"Inserting order {order.number}")
                cur.execute("INSERT INTO infi.orders VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (order.client, order.number, order.piece, order.quantity, order.due_date, order.late_pen, order.early_pen))
                
                print(f"Order inserted: {order}")   # Successfully inserted
                inserted_orders.append(order)
                break                               # Next order
                
            except psycopg2.InterfaceError as e:        # Error like "server closed unexpectedly"
                print(f"Error: {e}")
                conn = connect_to_db()                  #Connect to db again
                cur = conn.cursor()         
                continue                                # Try to insert it again
            
            except psycopg2.OperationalError as e:
                print(f"Operational Error: {e}")
                conn = connect_to_db()  # Reconnect to the database
                cur = conn.cursor()
                continue

            except Exception as e:  # Error like duplicate pkey -> ignore order
                print("Error:", e)
                conn.rollback()     
                break

    conn.commit()   
    
    # At the end close connection and cursor
    cur.close()
    conn.close()

    return inserted_orders

def insert_production_plan(order_prod_plan):

    conn = connect_to_db()
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

    
    while True:

        try:
            # Insert the ordered data into the new table
            cur.execute("INSERT INTO infi.production_plan VALUES (%s, %s)", (order_prod_plan.order_id, order_prod_plan.start_date))
            break
        except psycopg2.InterfaceError as e :        # Error like "server closed unexpectedly"
                print(f"Error: {e}")
                conn = connect_to_db()                  #Connect to db again
                cur = conn.cursor()         
                continue                                # Try to insert it again
    
        except psycopg2.OperationalError as e:
                print(f"Operational Error: {e}")
                conn = connect_to_db()  # Reconnect to the database
                cur = conn.cursor()
                continue    
            
        except Exception as e:  # Error like duplicate pkey -> ignore order
                print("Error:", e)
                conn.rollback()     
                break   
    
    conn.commit()
    cur.close()
    conn.close()

def insert_purchasing_plan(purchase_plan):

    if purchase_plan is None:
        return None

    conn = connect_to_db()
    cur = conn.cursor()

    try: 
        # Create the production_plan table if it doesn't exist
        cur.execute("""
                CREATE TABLE IF NOT EXISTS infi.purchasing_plan (
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
    except Exception as e:
        print("Error:", e)
        conn.rollback()
        return

    new_id = None

    while True:
        try:
            # Insert
            cur.execute("""
                INSERT INTO infi.purchasing_plan (
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
            
            new_id = cur.fetchone()[0]

            break
        except psycopg2.InterfaceError as e:        # Error like "server closed unexpectedly"
                print(f"Error: {e}")
                conn = connect_to_db()                  #Connect to db again
                cur = conn.cursor()         
                continue                                # Try to insert it again
        
        except psycopg2.OperationalError as e:
                print(f"Operational Error: {e}")
                conn = connect_to_db()  # Reconnect to the database
                cur = conn.cursor()
                continue
        
        except Exception as e:  # Error like duplicate pkey -> ignore order
                print("Error:", e)
                conn.rollback()     
                break   
    
    conn.commit()
    cur.close()
    conn.close()

    return new_id

def insert_raw_order_plan(raw_order_plan):

    conn = connect_to_db()
    cur = conn.cursor()

    try:
        # Create the production_plan table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS infi.raw_order_plan (
                plan_id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES infi.orders(number) NOT NULL,
                raw_order_id INTEGER REFERENCES infi.purchasing_plan(raw_order_id) NOT NULL,
                used_quantity INTEGER NOT NULL
            );
        """)
    except Exception as e:
        print("Error:", e)
        conn.rollback()
        return 

    while True:
        try:
            cur.execute("INSERT INTO infi.raw_order_plan (order_id, raw_order_id, used_quantity) VALUES (%s, %s, %s)", 
                        (raw_order_plan.order_id, raw_order_plan.raw_order_id, raw_order_plan.used_quantity))
            break
        except psycopg2.InterfaceError as e:        # Error like "server closed unexpectedly"
                    print(f"Error: {e}")
                    conn = connect_to_db()                  #Connect to db again
                    cur = conn.cursor()         
                    continue                                # Try to insert it again
                
        except Exception as e:  # Error like duplicate pkey -> ignore order
                    print("Error:", e)
                    conn.rollback()     
                    break       
    
    # Commit changes 
    conn.commit()

    #Close connection and cursor
    cur.close()
    conn.close()

def update_raw_order_plan(plan_id, new_used_quantity):

    conn = connect_to_db()

    cur = conn.cursor()

    # Create the production_plan table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS infi.raw_order_plan (
            plan_id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES infi.orders(number) NOT NULL,
            raw_order_id INTEGER REFERENCES infi.purchasing_plan(raw_order_id) NOT NULL,
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
    conn.close()

def get_order_raw_cost_info(order_id):

    query = """SELECT arrival_date, used_quantity, price_pp
                FROM infi.purchasing_plan 
                JOIN infi.raw_order_plan USING(raw_order_id)
                WHERE order_id = %s
                ORDER BY arrival_date ASC """
    
    raw_cost_info = execute_query(query, (order_id,))

    return raw_cost_info

def insert_costs(order_id, total_cost, unit_cost):

    conn = connect_to_db()

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
        cur.execute("INSERT INTO infi.order_costs VALUES (%s, %s, %s) ON CONFLICT (order_id) DO NOTHING", (order_id, total_cost, unit_cost))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        conn.rollback()

    cur.close()
    conn.close()

def get_order_costs():
    conn = connect_to_db()

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = """SELECT order_id, total_cost, unit_cost FROM infi.order_costs"""

        cursor.execute(query)

        order_costs = cursor.fetchall()

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []

    finally:
        cursor.close()
        conn.close()

    return order_costs

def clear_all_tables():
    conn = None
    cur = None
    tables = [
        "infi.raw_order_plan",
        "infi.purchasing_plan",
        "infi.production_plan",
        "infi.todays_date",
        "infi.order_costs",
        "infi.dispatches",
        "infi.orders"
    ]

    try:
        conn = connect_to_db()
        cur = conn.cursor()
        
        for table in tables:
            try:
                cur.execute(f"DELETE FROM {table}")
            except psycopg2.Error as e:
                print(f"Database error while deleting from {table}: {e}")
                conn.rollback()
                continue

        conn.commit()  # Commit all deletions if no errors occur
        print("All tables cleared.")

    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        if conn:
            conn.rollback()

    finally:
        cur.close()
        conn.close()
    
if __name__ == '__main__':
    # Example usage:
    dispatchs = dispatches()
    print("Dispatches:")
    for dispatch in dispatchs:
        print(f"Order ID: {dispatch['order_id']}, Dispatch Date: {dispatch['dispatch_date']}")
    # Example usage:
    order_costs = get_order_costs()
    print("Order Costs:")
    for order_cost in order_costs:
        print(f"Order ID: {order_cost['order_id']}, Total Cost: {order_cost['total_cost']}, Unit Cost: {order_cost['unit_cost']}")