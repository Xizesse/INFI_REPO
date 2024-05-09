import psycopg2
from psycopg2 import extras
from Orders import Order

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

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host='db.fe.up.pt',
        database='infind202410',
        user='infind202410',
        password='DWHyIHTiPP'
    )
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    table_name = 'infi.production_plan'
    start_date_col = 'start_date'
    columns = ['p5_quantity', 'p6_quantity', 'p7_quantity', 'p9_quantity']

    # Prepare the SQL query with a WHERE clause to filter by the desired day
    columns_str = ", ".join([extras.quote_ident(col, cursor) for col in [start_date_col] + columns])  # Safely quote identifiers
    query = f"SELECT {columns_str} FROM {table_name} WHERE {start_date_col} = %s ORDER BY {start_date_col} ASC"

    try:
        cursor.execute(query, (day,))
        # Fetch all rows as a list of dictionaries
        results = cursor.fetchall()

        # Expand the data
        expanded_results = expand_values(results)

        # Flatten the list of tuples into a single list
        piece_queue = [item for sublist in expanded_results for item in sublist]
        return piece_queue
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        # Close the connection to the database
        cursor.close()
        conn.close()

schedule = get_production_queue(8)
print(schedule)

def get_deliveries():
    """
    Fetches and expands production orders from a PostgreSQL database for all days.

    Returns:
    list of Order objects: Each object represents an order with attributes quantity, final_type, order_id, and delivery_day.
    """
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host='db.fe.up.pt',
        database='infind202410',
        user='infind202410',
        password='DWHyIHTiPP'
    )
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    table_name = 'infi.orders'
    columns = ['number', 'workpiece', 'quantity', 'due_date']

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
            order_id = row['number']
            final_type = row['workpiece']
            quantity_str = row['quantity']
            due_date_col = row['due_date']

            # Convert quantity to integer if possible
            try:
                quantity = int(quantity_str)
            except ValueError:
                print(f"Invalid quantity value: {quantity_str} for order ID: {order_id}")
                continue
            
            if quantity > 0:  # Ignore orders with quantity <= 0
                order = Order(quantity, final_type, order_id, due_date_col)
                orders.append(order)
        return orders
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        # Close the connection to the database
        cursor.close()
        conn.close()

# Example usage:
orders = get_deliveries()
for order in orders:
    print(f"Order ID: {order.order_id}, Quantity: {order.quantity}, Type: {order.final_type}, Delivery Date: {order.delivery_day}")
