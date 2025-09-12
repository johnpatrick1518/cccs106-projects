import mysql.connector

def connect_db():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",   # localhost (IP avoids socket issues)
            user="root",        
            password="admin123",
            database="fletapp",
            port=3307
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

# Test block
if __name__ == "__main__":
    conn = connect_db()
    if conn:
        print("✅ Connected successfully to fletapp database!")
        conn.close()
    else:
        print("❌ Connection failed.")
