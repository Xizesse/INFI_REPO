import psycopg2
from psycopg2 import extras

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
        due_date = row['due_date']
        for column, value in row.items():
            if column.startswith(item_prefix) and value is not None:
                item_number = int(column.lstrip(item_prefix).split('_')[0])
                for _ in range(value):
                    expanded_data.append((due_date, item_number))
    return expanded_data

    

def get_production_schedule(table_name, due_date_col, columns):
    """
    Fetches and expands production numbers sorted by a due date from a PostgreSQL database.

    Args:
    db_connection_str (str): Connection string for the PostgreSQL database.
    table_name (str): The name of the table from which to fetch the data.
    due_date_col (str): The name of the column used to sort the data.
    columns (list of str): The names of the columns to fetch.

    Returns:
    list of tuples: Each tuple contains the due date and expanded item numbers based on the quantities.
    """
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host='db.fe.up.pt',
        database='infind202410',
        user='infind202410',
        password='DWHyIHTiPP'
    )
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Prepare the SQL query
    columns_str = ", ".join([extras.quote_ident(col, cursor) for col in [due_date_col] + columns])  # Safely quote identifiers
    query = f"SELECT {columns_str} FROM {table_name} ORDER BY {due_date_col} ASC"
    
    try:
        # Execute the query
        cursor.execute(query)
        # Fetch all rows as a list of dictionaries
        results = cursor.fetchall()
        # Expand the data
        expanded_results = expand_values(results)
        return expanded_results
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        # Close the connection to the database
        cursor.close()
        conn.close()

# Usage example
table_name = 'infi.delivery_plan'
due_date_col = 'due_date'
columns = ['p5_quantity', 'p6_quantity', 'p7_quantity', 'p9_quantity']  # Example column names
schedule = get_production_schedule(table_name, due_date_col, columns)
for row in schedule:
    print(row)