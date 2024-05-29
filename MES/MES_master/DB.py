import psycopg2
from psycopg2 import extras
from Orders import Order
from Piece_to_produce import Piece_to_produce

def connect_to_db():
    conn = None
    while True:
        try:
            conn = psycopg2.connect(
                host='db.fe.up.pt',
                database='infind202410',
                user='infind202410',
                password='DWHyIHTiPP'
            )
        except psycopg2.Error as e:
            print(f"Error connecting to the database: {e}")
            continue
        else:
            break
    return conn

def expand_values(data, item_prefix='p'):
    """
    Expand values based on item quantities indicated in the column names.
    
    Args:
    data (list of dict): List of dictionaries, each containing the due date and item quantities.
    item_prefix (str): Prefix used to identify item columns.

    Returns:
    list of tuples: Each tuple contains the due date followed by expanded item numbers.
    """
    expanded_data = []
    for row in data:
        expanded_row = []
        for column, value in row.items():
            if column.startswith(item_prefix) and value is not None:
                item_number = int(column.lstrip(item_prefix).split('_')[0])
                expanded_row.extend([item_number] * value)
        expanded_data.append(tuple(expanded_row))
    return expanded_data

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
        
        except psycopg2.ProgrammingError as e:
            if "no results to fetch" in str(e):
                results = []
            else:
                print(f"Programming Error: {e}")
            break
            
        except Exception as e:
            print(f"An error occurred: {e}")
            results = []
            break
    
    try:
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error committing and closing the connection: {e}")

    return results

def get_purchasing_queue(day):
    """
    Fetches and expands production numbers sorted by a due date from a PostgreSQL database.

    Args:
    day (int or str): Day to get delivery data for.

    Returns:
    list of tuples: Each tuple contains the due date and expanded item numbers based on the quantities.
    """
    if isinstance(day, int):
        day = str(day)  # Convert integer to string

    query = """SELECT 
                    SUM(CASE WHEN workpiece = 'P1' THEN quantity ELSE 0 END) AS p1_quantity,
                    SUM(CASE WHEN workpiece = 'P2' THEN quantity ELSE 0 END) AS p2_quantity
                FROM infi.purchasing_plan
                WHERE arrival_date = %s
                GROUP BY arrival_date
                ORDER BY arrival_date ASC;"""

    results = execute_query(query, (day,))

    expanded_results = expand_values(results)

    piece_queue = [item for sublist in expanded_results for item in sublist]

    return piece_queue

def get_production_queue(day):
    """
    Fetches and expands production numbers sorted by a due date from a PostgreSQL database.

    Args:
    day (int or str): Day to get delivery data for.

    Returns:
    list of tuples: Each tuple contains the due date and expanded item numbers based on the quantities.
    (p5, p6, p7, p9)
    """
    if isinstance(day, int):
        day = str(day)  # Convert integer to string

    query = """SELECT start_date, order_id, workpiece,quantity,due_date
                FROM infi.production_plan
                JOIN infi.orders ON order_id = number
                WHERE start_date = %s;"""

    results = execute_query(query, (day,))

    piece_queue = [] 
    for row in results:
        order_id = row['order_id']
        workpiece = row['workpiece']
        quantity = row['quantity']
        due_date = row['due_date']


        workpiece = int(workpiece[1:])

        for i in range(quantity):
            print(f"Order ID: {order_id}, Workpiece: {workpiece}, Due Date: {due_date}")
            piece_queue.append(Piece_to_produce(order_id, workpiece, due_date))     

    return piece_queue    

def get_deliveries():
    """
    Fetches and expands production orders from a PostgreSQL database for all days.

    Returns:
    list of Order objects: Each object represents an order with attributes quantity, final_type, order_id, and delivery_day.
    """

    query = f"SELECT number, workpiece, quantity, due_date FROM infi.orders ORDER BY number ASC"

    results = execute_query(query)

    orders = []
    # Iterate over the fetched data and create Order objects
    for row in results:
        # Extracting data from the row
        order_id = row['number']
        final_type_str = row['workpiece']
        quantity_str = row['quantity']
        due_date_col = row['due_date']

        final_type_number = int(final_type_str[1:])

        # Convert quantity to integer if possible
        try:
            quantity = int(quantity_str)
        except ValueError:
            print(f"Invalid quantity value: {quantity_str} for order ID: {order_id}")
            continue
            
        if quantity > 0:  # Ignore orders with quantity <= 0
            order = Order(quantity, final_type_number, order_id, due_date_col)
            orders.append(order)
    return orders   
    
def set_current_date(current_date):
    """
    Set the current date in the database.
    """

    # Try to create the table if it doesn't exist
    create_table_query = """
    CREATE TABLE IF NOT EXISTS infi.todays_date (
        date INTEGER PRIMARY KEY
    );
    """

    execute_query(create_table_query)

    # Delete any existing rows to ensure only one row exists
    delete_existing_query = "DELETE FROM infi.todays_date;"
    
    execute_query(delete_existing_query)

    # Insert the new current date
    insert_query = "INSERT INTO infi.todays_date (date) VALUES (%s);"
    
    execute_query(insert_query, (current_date,))

def set_dispatch_date(order_id, dispatch_date):
    """
    Set the dispatch date in the database.
    """

    #Tries to create table if it doesn't exist
    query = "CREATE TABLE IF NOT EXISTS infi.dispatches (order_id INTEGER PRIMARY KEY, dispatch_date INTEGER);"
    
    execute_query(query)

    #Inserts dispatch date for new dispatched order
    query = "INSERT INTO infi.dispatches (order_id, dispatch_date) VALUES (%s, %s);"

    execute_query(query, (order_id, dispatch_date))

if __name__ == '__main__':
    
    # Example usage of the functions

    current_date = 10
    delivery = (905, 10) # Order ID and dispatch date

    set_current_date(current_date)
    set_dispatch_date(delivery[0], delivery[1])

    print("Purchasing queue: ",get_purchasing_queue(2))
    print("Production queue: ",get_production_queue(5))
    print("Deliveries: ",get_deliveries())


