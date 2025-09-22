# database.py
import sqlite3

def init_db():
    conn = sqlite3.connect('contacts.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
                   id INTEGER PRIMARY KEY AUTOINCREMENT, 
                   name TEXT NOT NULL, 
                   phone TEXT, 
                   email TEXT)
    ''')
    conn.commit()
    return conn

def add_contact_db(conn, name, phone, email):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)",
        (name, phone, email)
    )
    conn.commit()

def get_all_contacts_db(conn, search_term=""):
    cursor = conn.cursor()
    if search_term:
        cursor.execute("SELECT id, name, phone, email FROM contacts WHERE name LIKE ?",(f"%{search_term}%",),)
    else:
        cursor.execute("SELECT id, name, phone, email FROM contacts")
    return cursor.fetchall()

def update_contact_db(conn, contact_id, name, phone, email):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE contacts SET name = ?, phone = ?, email = ? WHERE id = ?",
        (name, phone, email, contact_id)
    )
    conn.commit()

def delete_contact_db(conn, contact_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    conn.commit()
