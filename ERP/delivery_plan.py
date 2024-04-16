import psycopg2

def upload_delivery_plan():
        
    # Establish connection to PostgreSQL database
    conn = psycopg2.connect(
        host='db.fe.up.pt',
        database='infind202410',
        user='infind202410',
        password='DWHyIHTiPP'
    )
    cur = conn.cursor()

    # Create a new table to store the ordered data
    cur.execute("""
        CREATE TABLE IF NOT EXISTS INFI.delivery_plan (
            due_date INTEGER PRIMARY KEY,
            p5_quantity INTEGER,
            p6_quantity INTEGER,
            p7_quantity INTEGER,
            p9_quantity INTEGER
        );
    """)

    print("Table created")

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
            VALUES (%s, %s, %s, %s, %s);
        """, (due_date, p5_quantity, p6_quantity, p7_quantity, p9_quantity))

        
    # Commit changes and close connection
    conn.commit()
    conn.close()

    print("Data inserted into delivery_plan table.")
