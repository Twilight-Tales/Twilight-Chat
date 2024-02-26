import streamlit as st
import sqlite3
import hashlib

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

        #Debugging purposes I reset the tables 
        self.c.execute("DROP TABLE IF EXISTS Users;")
        self.c.execute("DROP TABLE IF EXISTS Books;")
        self.c.execute("DROP TABLE IF EXISTS BookReadingHistory;")
        self.c.execute("DROP TABLE IF EXISTS ChatHistory;")
        self.c.execute("DROP TABLE IF EXISTS BooksHistoryAssociation;")

        self.create_user_table()
        self.create_book_library_table()
        self.create_book_history_table()
        self.create_chat_history_table()
        self.create_library_history_assoctable()

    def create_user_table(self):
        """Create a database of users
        """
        # TODO: do you want tokens?
        # session_token TEXT UNIQUE NOT NULL,
        #         session_expiration DATETIME NOT NULL,
        #         update_token TEXT UNIQUE,
        try:
            self.c.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                ch_id TEXT,
                FOREIGN KEY (ch_id) REFERENCES ChatHistory(ch_id)
            );
        ''')
        except Exception as e:
            print("Error creating table: ", e)
            raise e

    #TODO: chapter database
    def create_chapter_table(self):
        """
        """
        try:
            self.c.execute('''
            CREATE TABLE IF NOT EXISTS Chapter(
                chapter_id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_content TEXT NOT NULL,
            );
            ''')
        except Exception as e:
            print("Error creating table: ", e)
            raise e


    #TODO: need pages field, how to connect to contents
    def create_book_library_table(self):
        """
        Create the books table if it doesn't exist
        
        """
        try:
            self.c.execute(
            '''CREATE TABLE IF NOT EXISTS Books(
                book_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                author TEXT NOT NULL,
                book_title TEXT NOT NULL,
                reference_code TEXT NOT NULL,
                chapter_id INTEGER,
                FOREIGN KEY (chapter_id) REFERENCES Chapter(chapter_id)
                );
            ''')
        except Exception as e:
            print("Error creating table: ", e)
            raise e
        
    def create_chat_history_table(self):
        """
        Create a chat history table
        """
        #Chat History table
        try:
            self.c.execute(
            '''CREATE TABLE IF NOT EXISTS ChatHistory (
                ch_id INTEGER PRIMARY KEY,
                time DATETIME NOT NULL,
                reading_id INTEGER NOT NULL UNIQUE,
                FOREIGN KEY (reading_id) REFERENCES BookReadingHistory (reading_id)
            );'''
            )
        except Exception as e:
            print("Error creating table: ", e)
            raise e
        
    def create_book_history_table(self):
        """
        Book Reading History table
        #TODO: what exactly do we want chapter_pid to be?
        """
        
        try:
            self.c.execute(
            '''CREATE TABLE IF NOT EXISTS BookReadingHistory  (
                reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_title TEXT NOT NULL,
                current_chapter INTEGER NOT NULL,
                current_page INTEGER NOT NULL,
                time DATETIME NOT NULL
            );
            ''')
        except Exception as e:
            print("Error creating table: ", e)
            raise e

    def create_library_history_assoctable(self):
        """
        Association table between book library and
        books 
        """
        try:
            self.c.execute('''
                CREATE TABLE IF NOT EXISTS BooksHistoryAssociation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    reading_id INTEGER NOT NULL,
                    FOREIGN KEY (book_id) REFERENCES Books(book_id),
                    FOREIGN KEY (reading_id) REFERENCES BookReadingHistory(reading_id)
                );'''
            )
        except Exception as e:
            print("Error creating table: ", e)
            raise e
    
    def get_all_books(self):
        """
        Get all books in the database
        """
        cursor = self.c.execute("SELECT * FROM Books;")
        books = []
        #Retrieve data from the database
        for row in cursor:
            books.append({
                "Avatar Name": row[1],
                "Book Contents": row[4],
                "Voice Speed": row[5],
                "Reference Code": row[6]
            })
        return books

    #Getting Most Recent Book History 
    # user id --> most recent chat history --> return most recent book history ?
    
    def get_user_by_id(self):
        pass
    
    def get_chat_history(self):
        pass

    def get_book_history(self):
        pass

    def create_user(self, username, password):
        """
        Create a user
        Requires an username and password
        """
        cursor = self.c.cursor()

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cursor.execute('INSERT INTO Users (username, password) VALUES (?, ?)', (username, hashed_password))

        self.c.commit()
        
        return cursor.lastrowid 

    def login_user(self, username, password):
        """
        Login an user
        Requires username and password
        """
        cursor = self.c.cursor()

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, hashed_password))
        user = cursor.fetchone()

        if user:
            return True, user
        else:
            return False, None 
    


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
