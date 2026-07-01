import sqlite3
import json

DB_PATH = "bingo.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            current_board TEXT,
            card_rerolls_left INTEGER DEFAULT 3,
            square_rerolls_left INTEGER DEFAULT 0,
            is_locked BOOLEAN DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def get_user_state(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "user_id": row["user_id"],
            "current_board": json.loads(row["current_board"]),
            "card_rerolls_left": row["card_rerolls_left"],
            "square_rerolls_left": row["square_rerolls_left"],
            "is_locked": bool(row["is_locked"])
        }
    return None

def create_or_reset_user(user_id, board):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, current_board, card_rerolls_left, square_rerolls_left, is_locked)
        VALUES (?, ?, 3, 0, 0)
        ON CONFLICT(user_id) DO UPDATE SET
            current_board=excluded.current_board,
            card_rerolls_left=3,
            square_rerolls_left=0,
            is_locked=0
    """, (user_id, json.dumps(board)))
    conn.commit()
    conn.close()

def lock_board(user_id):
    state = get_user_state(user_id)
    if not state or state["is_locked"]:
        return False # Already locked or doesn't exist

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Any unused card_rerolls_left are converted 1:1 into square_rerolls_left
    new_square_rerolls = state["square_rerolls_left"] + state["card_rerolls_left"]

    cursor.execute("""
        UPDATE users
        SET is_locked = 1,
            square_rerolls_left = ?,
            card_rerolls_left = 0
        WHERE user_id = ?
    """, (new_square_rerolls, user_id))
    conn.commit()
    conn.close()
    return True

def reroll_card(user_id, new_board):
    state = get_user_state(user_id)
    if not state or state["is_locked"] or state["card_rerolls_left"] <= 0:
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET current_board = ?,
            card_rerolls_left = card_rerolls_left - 1
        WHERE user_id = ?
    """, (json.dumps(new_board), user_id))
    conn.commit()
    conn.close()
    return True

def reroll_square(user_id, square_index, new_task):
    state = get_user_state(user_id)
    if not state or not state["is_locked"] or state["square_rerolls_left"] <= 0:
        return False

    board = state["current_board"]
    if square_index < 0 or square_index >= len(board):
        return False

    board[square_index] = new_task

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET current_board = ?,
            square_rerolls_left = square_rerolls_left - 1
        WHERE user_id = ?
    """, (json.dumps(board), user_id))
    conn.commit()
    conn.close()
    return True
