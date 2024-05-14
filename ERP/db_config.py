import psycopg2

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

