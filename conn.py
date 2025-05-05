import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        # Replace the below with your actual MySQL database connection details
        connection = mysql.connector.connect(
            host='localhost',       # Host of your MySQL server
            database='PeakhotelDb',  # Your database name
            user='root',          # Your MySQL username
            password='Anitha$123'   # Your MySQL password
        )

        if connection.is_connected():
            print("Successfully connected to the database")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

def close_connection(connection):
    if connection and connection.is_connected():
        connection.close()
        print("Connection closed")

# Example usage:
connection = create_connection()

if connection:
    # You can now perform queries here
    cursor = connection.cursor()
    cursor.execute("SELECT DATABASE();")
    record = cursor.fetchone()
    print(f"You're connected to database: {record}")

    # Don't forget to close the connection
    close_connection(connection)
