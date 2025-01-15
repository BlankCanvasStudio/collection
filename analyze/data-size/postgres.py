#!/bin/python3

import psycopg2, sys

# Set up postgres connection
host = "10.10.10.3"
port = "5432"
database = "Discern"
user = "postgres"
password = "*Something*"

print()

try:
    # Connect to PostgreSQL database
    connection = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
    
    # Create a cursor object
    cursor = connection.cursor()
    
    # Execute a query
    cursor.execute("SELECT * FROM AnsiblePlaybook;")
    
    rows = cursor.fetchall()

    print("ansible playbooks:")
    for row in rows:
        print(row)
    print()

    # Execute a query
    cursor.execute("SELECT * FROM AnsibleConfig;")
    
    rows = cursor.fetchall()

    print("ansible configs:")
    for row in rows:
        print(row)
    print()

    # Execute a query
    cursor.execute("SELECT * FROM JupyterNotebook;")
    
    rows = cursor.fetchall()

    print("Jupyter Notebooks:")
    for row in rows:
        print(row)
    print()

    # Execute a query
    cursor.execute("SELECT * FROM Logs;")
    
    rows = cursor.fetchall()


    logs_size = 0
    for row in rows:
        hash_size = sys.getsizeof(row[0])
        content_size = sys.getsizeof(row[1])
        
        logs_size += hash_size + content_size

    print(f"Num Log Entries: {len(rows)}")
    print(f"Logs Size: {logs_size} Bytes")

    cursor.close()
    connection.close()


except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL database: {e}")
    raise

