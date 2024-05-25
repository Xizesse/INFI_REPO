import math
import psycopg2 
from db_config import *
from classes.order import Order

def calculate_production_start(new_order):
  
    print(f"\nOrder: {new_order}")

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

    due_date = new_order.due_date
    workpiece = new_order.piece
    quantity = new_order.quantity
           
    time_to_produce = quantity * avg_prod_time[workpiece]
    time_to_produce = time_to_produce / available_lines[workpiece]
    start_date = due_date - math.ceil(time_to_produce)

    current_date = get_current_date()
    if start_date < current_date:    # if start date is invalid
        start_date = current_date   

    prod_plan = (start_date, workpiece, quantity)
    print(f"Production plan: {prod_plan}")

    return prod_plan

def insert_production_plan(conn, order_prod_plan):

    start_date, workpiece, quantity = order_prod_plan

    cur = conn.cursor()

    try: 
        # Create the production_plan table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS infi.production_plan (
                start_date INTEGER PRIMARY KEY,
                p5_quantity INTEGER,
                p6_quantity INTEGER,
                p7_quantity INTEGER,
                p9_quantity INTEGER
            );
        """)
    except Exception as e:
        print("Error:", e)
        conn.rollback()
        return

    # Initialize quantities for each piece type
    quantities = {
        'P5': 0,
        'P6': 0,
        'P7': 0,
        'P9': 0
    }

    # Set the quantity for the corresponding piece type
    quantities[workpiece] = quantity
    
    # Insert the ordered data into the new table
    cur.execute("""
        INSERT INTO INFI.production_plan (start_date, p5_quantity, p6_quantity, p7_quantity, p9_quantity)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (start_date) DO UPDATE
        SET p5_quantity = production_plan.p5_quantity + excluded.p5_quantity,
            p6_quantity = production_plan.p6_quantity + excluded.p6_quantity,
            p7_quantity = production_plan.p7_quantity + excluded.p7_quantity,
            p9_quantity = production_plan.p9_quantity + excluded.p9_quantity;
        """, (start_date, quantities['P5'], quantities['P6'], quantities['P7'], quantities['P9']))

    # Commit changes 
    conn.commit()

    #print("Production schedule inserted into production_plan table.")



    