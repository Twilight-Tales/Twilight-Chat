import streamlit as st
import sqlite3
# Connect to the SQLite database
conn = sqlite3.connect('bookclub.db')
c = conn.cursor()

# Create a table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS bookclub (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                avatar_name TEXT,
                book_contents TEXT,
                voice_speed INTEGER,
                reference_code TEXT
            )''')

def generate_reference_code():
    # Generate a 6-digit reference code
    return "ABC123"

def save_to_database(avatar_name, book_contents, voice_speed, reference_code):
    # Insert the data into the table
    c.execute('''INSERT INTO bookclub (avatar_name, book_contents, voice_speed, reference_code)
                VALUES (?, ?, ?, ?)''', (avatar_name, book_contents, voice_speed, reference_code))
    conn.commit()

def main():
    # Set page title
    st.set_page_config(page_title="Book Club UI")

    # Dropdown menu for avatar names
    avatar_names = ["Avatar 1", "Avatar 2", "Avatar 3"]
    selected_avatar = st.selectbox("Select Avatar", avatar_names)

    # Input box for book contents
    book_contents = st.text_area("Enter Book Contents")

    # Dial for voice speed
    voice_speed = st.slider("Voice Speed", min_value=0, max_value=10, step=1)

    # Submit button
    if st.button("Submit"):
        # Generate reference code
        reference_code = generate_reference_code()

        # Save the data to the database
        save_to_database(selected_avatar, book_contents, voice_speed, reference_code)

        # Display reference code
        st.write("Reference Code:", reference_code)

if __name__ == "__main__":
    main()
