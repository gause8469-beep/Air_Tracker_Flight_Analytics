from db_connection import get_connection

connection = get_connection()
cursor = connection.cursor()

cursor.execute("SHOW TABLES")
for row in cursor.fetchall():
    print(row[0])

cursor.close()
connection.close()

