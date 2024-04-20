import psycopg2
from db_config import DB_CONFIG

def upload_delivery_plan():
        
    # Establish connection to PostgreSQL database
    conn = psycopg2.connect(
        host = DB_CONFIG['host'],
        database = DB_CONFIG['database'],
        user = DB_CONFIG['user'],
        password = DB_CONFIG['password']
    )
    cur = conn.cursor()

    # Create a new table to store the ordered data if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS INFI.delivery_plan (
            due_date INTEGER PRIMARY KEY,
            p5_quantity INTEGER,
            p6_quantity INTEGER,
            p7_quantity INTEGER,
            p9_quantity INTEGER
        );
    """)

    # Query to retrieve data from orders table and calculate total quantities for each piece type and due date
    query = """
        SELECT due_date,
            SUM(CASE WHEN workpiece = 'P5' THEN quantity ELSE 0 END) AS p5_quantity,
            SUM(CASE WHEN workpiece = 'P6' THEN quantity ELSE 0 END) AS p6_quantity,
            SUM(CASE WHEN workpiece = 'P7' THEN quantity ELSE 0 END) AS p7_quantity,
            SUM(CASE WHEN workpiece = 'P9' THEN quantity ELSE 0 END) AS p9_quantity
        FROM INFI.orders
        GROUP BY due_date
        ORDER BY due_date;
    """

    # Execute the query
    cur.execute(query)

    # Insert the ordered data into the new table
    for row in cur.fetchall():
        due_date, p5_quantity, p6_quantity, p7_quantity, p9_quantity = row
        cur.execute("""
            INSERT INTO INFI.delivery_plan (due_date, p5_quantity, p6_quantity, p7_quantity, p9_quantity)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (due_date) DO UPDATE
            SET p5_quantity = delivery_plan.p5_quantity + excluded.p5_quantity,
                p6_quantity = delivery_plan.p6_quantity + excluded.p6_quantity,
                p7_quantity = delivery_plan.p7_quantity + excluded.p7_quantity,
                p9_quantity = delivery_plan.p9_quantity + excluded.p9_quantity;
        """, (due_date, p5_quantity, p6_quantity, p7_quantity, p9_quantity))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print("Data inserted into delivery_plan table.")
