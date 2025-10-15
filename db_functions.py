import sqlite3
import json

DATABASE_NAME = "users.db"


def init_db():
    """Initializes the database and creates the user_data table with all necessary columns."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    # Add a new column for search_history
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id TEXT PRIMARY KEY,
            user_tags TEXT,
            saved_questions TEXT,
            search_history TEXT
        )
    """
    )
    conn.commit()
    conn.close()


def load_user_data(user_id):
    """Loads a user's data from the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    # Select all columns
    cursor.execute(
        "SELECT user_tags, saved_questions, search_history FROM user_data WHERE user_id = ?",
        (user_id,),
    )
    data = cursor.fetchone()
    conn.close()
    if data:
        tags = json.loads(data[0]) if data[0] else []
        questions = json.loads(data[1]) if data[1] else []
        history = json.loads(data[2]) if data[2] else []
        return {"tags": tags, "questions": questions, "history": history}
    return None


def save_user_data(user_id, tags_list, saved_list, history_list):
    """Saves or updates a user's data in the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # --- FIX IS HERE ---
    # Convert any NumPy int64 types to standard Python int before saving
    # This makes the lists JSON serializable
    saved_list_py = [int(item) for item in saved_list]
    history_list_py = [int(item) for item in history_list]
    # -----------------

    tags_json = json.dumps(tags_list)
    questions_json = json.dumps(saved_list_py)  # Use the converted list
    history_json = json.dumps(history_list_py)  # Use the converted list

    # Update the query to include search_history
    cursor.execute(
        """
        INSERT OR REPLACE INTO user_data (user_id, user_tags, saved_questions, search_history)
        VALUES (?, ?, ?, ?)
    """,
        (user_id, tags_json, questions_json, history_json),
    )
    conn.commit()
    conn.close()
