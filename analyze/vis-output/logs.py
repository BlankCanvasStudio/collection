#!/bin/python3

import psycopg2

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
    cursor.execute("SELECT * FROM Logs LIMIT 5;")
    
    rows = cursor.fetchall()


    print("\n\nLogs:\n")
    for row in rows:
        # Convert 'contents' field from memoryview to string
        contents = row[1].tobytes().decode('utf-8') if isinstance(row[1], memoryview) else row[1]
        # Print the row with the decoded 'contents' field
        print(f"Hash: {row[0]}")
        print(f"Contents:\n{contents}")


    cursor.close()
    connection.close()


except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL database: {e}")
    raise

