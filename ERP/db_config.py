import psycopg2
from psycopg2 import extras
from classes.order import Order
from classes.plan_production import production_plan
from classes.plan_purchasing import purchasing_plan

DB_CONFIG = {
    "host": "db.fe.up.pt",
    "database": "infind202410",
    "user": "infind202410",
    "password": "DWHyIHTiPP"
}

def connect_to_db():
    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        database=DB_CONFIG['database'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    return conn

def close_db_connection(conn):
    conn.close()

def get_current_date():

    date_conn = connect_to_db()
    cur = date_conn.cursor()

    query = """
        SELECT date
        FROM infi.todays_date
    """

    cur.execute(query)

    #Fetch current date
    current_date = cur.fetchone()
    current_date = int(current_date[0])
    close_db_connection(date_conn)

    return current_date

def get_purchasing_plan():
    """
    Fetches purchasing plan data from the 'infi.purchasing_plan' table in the 'infind202410' database.

    Returns:
        list: A list of dictionaries containing purchasing plan information. Each dictionary
              has keys corresponding to table columns (e.g., 'arrival_date', 'p1_quantity').
              If an error occurs, an empty list is returned.
    """

    purchasing_plan = []

    try:
        # Connect to the PostgreSQL database
        conn = connect_to_db()

        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Define table name and columns
        table_name = 'infi.purchasing_plan'
        columns = ['arrival_date', 'p1_quantity', 'p2_quantity']

        # Safely quote identifiers
        columns_str = ", ".join([psycopg2.extensions.quote_ident(col, cursor) for col in columns])

        # Prepare the SQL query
        query = f"SELECT {columns_str} FROM {table_name} ORDER BY {columns[0]} ASC"

        cursor.execute(query)

        # Check for empty results and return early
        results = cursor.fetchall()
        if not results:
            return purchasing_plan  # Return empty list if no rows found

        for row in results:
            purchasing_plan_entry = {}  # Create a dictionary for each purchasing plan entry

            # Extract data from the row
            for col, value in row.items():
                purchasing_plan_entry[col] = value

            # Convert quantity columns to integers (handle potential errors)
            for quantity_col in ['p1_quantity', 'p2_quantity']:
                try:
                    purchasing_plan_entry[quantity_col] = int(value)  # Use 'value' instead of nested access
                except ValueError as e:
                    print(f"Error converting quantity value '{value}' (column: {quantity_col}) to integer: {e}")
                    continue  # Skip rows with invalid quantity values

            purchasing_plan.append(purchasing_plan_entry)

    except psycopg2.Error as e:
        print(f"Database error: {e}")

    finally:
        # Close the database connection (if open)
        if cursor:
            cursor.close()
        if conn:
            close_db_connection(conn)

    return purchasing_plan

def get_production_plan():
    """
    Fetches production plan data from the 'infi.production_plan' table in the 'infind202410' database.

    Returns:
        list: A list of dictionaries containing production plan information. Each dictionary
              has keys corresponding to table columns (e.g., 'start_date', 'p5_quantity').
              If an error occurs, an empty list is returned.
    """

    production_plan = []

    try:
        # Connect to the PostgreSQL database
        conn = connect_to_db()

        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Define table name and columns
        table_name = 'infi.production_plan'
        columns = ['start_date', 'p5_quantity', 'p6_quantity', 'p7_quantity', 'p9_quantity']

        # Safely quote identifiers
        columns_str = ", ".join([psycopg2.extensions.quote_ident(col, cursor) for col in columns])

        # Prepare the SQL query
        query = f"SELECT {columns_str} FROM {table_name} ORDER BY {columns[0]} ASC"

        cursor.execute(query)

        # Fetch all rows as a list of dictionaries
        results = cursor.fetchall()

        for row in results:
            production_plan_entry = {}  # Create a dictionary for each production plan entry

            # Extract data from the row
            for col, value in row.items():
                production_plan_entry[col] = value

            # Convert quantity columns to integers (handle potential errors)
            for quantity_col in ['p5_quantity', 'p6_quantity', 'p7_quantity', 'p9_quantity']:
                try:
                    production_plan_entry[quantity_col] = int(production_plan_entry[quantity_col])
                except ValueError as e:
                    print(f"Error converting quantity value '{production_plan_entry[quantity_col]}' (column: {quantity_col}) to integer: {e}")
                    continue  # Skip rows with invalid quantity values

            production_plan.append(production_plan_entry)

    except psycopg2.Error as e:
        print(f"Database error: {e}")

    finally:
        # Close the database connection (if open)
        if cursor:
            cursor.close()
        if conn:
            close_db_connection(conn)

    return production_plan

def get_orders():
  
    # Connect to the PostgreSQL database
    conn = connect_to_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    table_name = 'infi.orders'
    columns = ['client', 'number', 'workpiece', 'quantity', 'due_date', 'late_pen', 'early_pen']

    # Prepare the SQL query
    columns_str = ", ".join([psycopg2.extensions.quote_ident(col, cursor) for col in columns])  # Safely quote identifiers
    query = f"SELECT {columns_str} FROM {table_name} ORDER BY {columns[0]} ASC"

    try:
        cursor.execute(query)
        # Fetch all rows as a list of dictionaries
        results = cursor.fetchall()

        orders = []
        # Iterate over the fetched data and create Order objects
        for row in results:
            # Extracting data from the row
            client = row['client']
            number = row['number']
            piece = row['workpiece']
            quantity_str = row['quantity']
            due_date_col = row['due_date']
            late_pen = row['late_pen']
            early_pen = row['early_pen']

            # Convert quantity to integer if possible
            try:
                quantity = int(quantity_str)
            except ValueError:
                print(f"Invalid quantity value: {quantity_str} for order ID: {number}")
                continue
            
            if quantity > 0:  # Ignore orders with quantity <= 0
                order = Order(client, quantity, piece, number, due_date_col, late_pen, early_pen)
                orders.append(order)
        return orders
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        # Close the connection to the database
        cursor.close()
        close_db_connection(conn)


# Example usage:
orders = get_orders()
for order in orders:
    print(f" Client: {order.client}, Order ID: {order.number}, Quantity: {order.quantity}, Type: {order.piece}, Delivery Date: {order.due_date}, Late Penalty: {order.late_pen}, Early Penalty: {order.early_pen}")

production_plan = get_production_plan()
for entry in production_plan:
    print(f" Start Date: {entry['start_date']}, P5 Quantity: {entry['p5_quantity']}, P6 Quantity: {entry['p6_quantity']}, P7 Quantity: {entry['p7_quantity']}, P9 Quantity: {entry['p9_quantity']}")

purchasing_plan = get_purchasing_plan()
for entry in purchasing_plan:
    print(f" Arrival Date: {entry['arrival_date']}, P1 Quantity: {entry['p1_quantity']}, P2 Quantity: {entry['p2_quantity']}")

current_date = get_current_date()
print(f"Current Date: {current_date}")