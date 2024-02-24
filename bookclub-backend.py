import streamlit as st
import sqlite3

#one database driver within app
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance

class DatabaseDriver(object):
    """
    Databse driver for the bookclub app.
    Handles with reading and writing data
    within the database
    """
    def __init__(self):
        """
        Secure a connction w/ the database
        and store it into the instance 'c'
        """
        # Connect to the SQLite database
        self.c = sqlite3.connect('bookclub.db', check_same_thread = False)

        self.create_user_table()
        self.create_book_library_table()
        self.create_book_history_table()
        self.create_chat_history_table()
        self.create_library_history_assoctable()
        #self.c.close() TODO: Where to close

    def create_user_table(self):
        """Create a database of users
        """
        # TODO:Assuming encryption is handled in application layer 
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id String PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            ch_id TEXT NOT NULL,
            FOREIGN KEY (ch_id) REFERENCES ChatHistory(ch_id));
            session_token TEXT NOT NULL,
            session_expiration DATETIME NOT NULL,
            update_token TEXT UNIQUE
        );
        ''')

    def create_book_library_table(self):
        """
        Create the books table if it doesn't exist
        
        """
        #TODO: what is avatar_name, is that the author? 
        #TODO: are we divding text files by chapter of a specific book, or just by the book 

        self.c.execute(
        '''CREATE TABLE IF NOT EXISTS Books(
            book_id INTEGER PRIMARY KEY AUTOINCREMENT
            avatar_name TEXT NOT NULL, 
            author TEXT NOT NULL,
            book_title TEXT NOT NULL,
            book_contents TEXT NOT NULL, 
            voice_speed INTEGER NOT NULL, 
            reference_code TEXT NOT NULL
        ''')

    def create_book_history_table(self):
        """
        Book Reading History table
        #TODO: what exactly do we want chapter_pid to be?
        """
        
        # Assuming a link to Book_Library is needed, we need a foreign key to book_id  
        self.c.execute(
        '''CREATE TABLE BookReadingHistory (
            reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_title TEXT NOT NULL,
            chapter_pid TEXT NOT NULL,
            time DATETIME NOT NULL
        ''')

    def create_chat_history_table(self):
        """
        Create a chat history table
        """
        #Chat History table
        self.c.execute(
        '''CREATE TABLE ChatHistory (
            ch_id INTEGER PRIMARY KEY,
            time DATETIME NOT NULL
            reading_id INTEGER NOT NULL UNIQUE,
            FOREIGN KEY (reading_id) REFERENCES BookReadingHistory (reading_id)
        ''')
    def create_library_history_assoctable(self):
        """
        Association table between book library and
        books 
        """
        self.c.execute('''
            CREATE TABLE BooksHistoryAssociation (
                id INTEGER PRIMARY KEY AUTOINCREMENT
                book_id INTEGER NOT NULL,
                reading_id INTEGER NOT NULL,
                FOREIGN KEY (book_id) REFERENCES Books(book_id),
                FOREIGN KEY (reading_id) REFERENCES BookReadingHistory(reading_id)
            );'''
        )
    
    def get_all_books(self):
        """
        Get all books in the database
        """
        cursor = self.c.execute("SELECT * FROM Books;")
        books = []
        #Retrieve data from the database
        for row in books:
            books.append({
                "Avatar Name": row[1],
                "Book Contents": row[4],
                "Voice Speed": row[5],
                "Reference Code": row[6]
            })
        return books

"""
# Retrieve data from the database
c.execute("SELECT avatar_name, book_contents, voice_speed, reference_code FROM bookclub")
books = c.fetchall()

# Display the information using Streamlit
st.title("Book Club App")
st.write("Here are the books in the database:")
"""

#TODO: turn into somesort of api thingy? 
"""
for book in books:
    st.write(f"Avatar Name: {book[0]}")
    st.write(f"Book Contents: {book[1]}")
    st.write(f"Voice Speed: {book[2]}")
    st.write(f"Reference Code: {book[3]}")
    st.write("---")
"""


DatabaseDriver = singleton(DatabaseDriver)
