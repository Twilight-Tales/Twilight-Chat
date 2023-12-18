import streamlit as st
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('bookclub.db')
c = conn.cursor()

# Create the books table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS books
             (avatar_name TEXT, book_contents TEXT, voice_speed INTEGER, reference_code TEXT)''')

# Retrieve data from the database
c.execute("SELECT avatar_name, book_contents, voice_speed, reference_code FROM bookclub")
books = c.fetchall()

# Display the information using Streamlit
st.title("Book Club App")
st.write("Here are the books in the database:")

for book in books:
    st.write(f"Avatar Name: {book[0]}")
    st.write(f"Book Contents: {book[1]}")
    st.write(f"Voice Speed: {book[2]}")
    st.write(f"Reference Code: {book[3]}")
    st.write("---")

# Close the database connection
conn.close()
