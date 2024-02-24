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

### Added Tables: User, Book Library table, Book Reading History table, Book Reading History table, and Chat History table
c.execute('''
    CREATE TABLE User (
    user_id INTEGER PRIMARY KEY,
    username STRING NOT NULL,
    password STRING NOT NULL, -- Assuming encryption is handled in application layer
    session_token STRING,
    session_expiration DATETIME,
    update_token STRING UNIQUE
);
''')


# Book Library table
c.execute('''
    CREATE TABLE BookLibrary (
        book_id INTEGER PRIMARY KEY,
        book_title STRING NOT NULL,
        author STRING,
        genre STRING,
        link_to_text STRING -- Assuming this is a URL to the text
    );
''')


#Book Reading History table
c.execute('''
    CREATE TABLE BookReadingHistory (
        reading_id INTEGER PRIMARY KEY,
        book_title STRING NOT NULL,
        chapter_title STRING,
        p_id INTEGER,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES User(user_id)
        -- Assuming a link to BookLibrary is needed, we need a foreign key to book_id
        -- FOREIGN KEY (p_id) REFERENCES BookLibrary(book_id)
    );
''')


#Chat History table
c.execute('''
    CREATE TABLE ChatHistory (
        ch_id INTEGER PRIMARY KEY,
        time DATETIME NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    );
''')


#Assuming that the relationship between Book Reading History and Chat History
#is many-to-many, we need an association table
c.execute('''
    CREATE TABLE ReadingChatAssociation (
        ch_id INTEGER,
        reading_id INTEGER,
        PRIMARY KEY (ch_id, reading_id),
        FOREIGN KEY (ch_id) REFERENCES ChatHistory(ch_id),
        FOREIGN KEY (reading_id) REFERENCES BookReadingHistory(reading_id)
    );
''')


# Close the database connection
conn.close()
