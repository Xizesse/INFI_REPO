import math
import psycopg2 
from db_config import DB_CONFIG
from classes.order import Order

def calculate_production_start(new_order):
    # Establish connection to PostgreSQL database
    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        database=DB_CONFIG['database'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    cur = conn.cursor()

    # Query to retrieve data from orders table for the specified order number
    query = """
        SELECT due_date, workpiece, quantity
        FROM infi.orders
        WHERE number=%s
    """

    # Execute the query with the specified order number
    cur.execute(query, (new_order.number,))

    order = cur.fetchone()  # fetch row (order)

    print(f"\nOrder: {order}")

    avg_prod_time = {   # average production time for each piece type
    "P5": 1.58,
    "P6": 1.58,
    "P7": 1,
    "P9": 1.5
    }

    due_date, workpiece, quantity = order
           
    time_to_produce = quantity * avg_prod_time[workpiece]
    start_date = due_date - math.ceil(time_to_produce)

    if start_date <= 0:    # if start date is invalid
        start_date = 1          #-------IN THE FUTURE SHOULD BE CURRENT DATE      

    # Close connection
    conn.close()

    prod_plan = (start_date, workpiece, quantity)
    print(f"Production plan: {prod_plan}")

    return prod_plan


def insert_production_plan(conn, order_prod_plan):

    start_date, workpiece, quantity = order_prod_plan

    cur = conn.cursor()

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

if __name__ == '__main__':

    prod_start = calculate_production_start(42)
    print(f"Production plan: {prod_start}")
    insert_production_plan(prod_start)


    