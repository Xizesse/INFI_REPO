import math
import psycopg2 
from db_config import *
from classes.order import Order

def calculate_production_start(new_order):

    avg_prod_time = {   # average production time for each piece type
    "P5": 1.58,
    "P6": 1.58,
    "P7": 1,
    "P9": 1.5
    }

    available_lines = { # assuming u can make 3 of each type at the same time
        "P5": 3,
        "P6": 3,
        "P7": 3,
        "P9": 3
    }
           
    time_to_produce = new_order.quantity * avg_prod_time[new_order.piece]
    time_to_produce = time_to_produce / available_lines[new_order.piece]
    start_date = new_order.due_date - math.ceil(time_to_produce)

    current_date = get_current_date()
    if start_date < current_date:    # if start date is invalid
        start_date = current_date   

    prod_plan = (new_order.number, start_date, new_order.piece, new_order.quantity)
    print(f"Production plan: {prod_plan}")

    return prod_plan

def insert_production_plan(conn, order_prod_plan):

    order_id, start_date, piece, quantity = order_prod_plan

    cur = conn.cursor()

    try: 
        # Create the production_plan table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS infi.new_production_plan (
                order_id INTEGER REFERENCES infi.orders(number) PRIMARY KEY,
                start_date INTEGER NOT NULL
            );
        """)
    except Exception as e:
        print("Error:", e)
        conn.rollback()
        return

    
    # Insert the ordered data into the new table
    cur.execute("INSERT INTO infi.new_production_plan VALUES (%s, %s)", (order_id, start_date))

    # Commit changes 
    conn.commit()



    