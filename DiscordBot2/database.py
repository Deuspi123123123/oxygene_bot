import sqlite3
import time

DB_NAME = "database.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS custom_permissions (
        user_id INTEGER,
        command TEXT,
        PRIMARY KEY (user_id, command)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invites (
        user_id INTEGER PRIMARY KEY,
        count INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS founder_bl (
        user_id INTEGER,
        founder_id INTEGER,
        PRIMARY KEY(user_id, founder_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ban_details (
        case_id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER,
        user_id INTEGER,
        moderator_id INTEGER,
        reason TEXT,
        channel_id INTEGER,
        message_id INTEGER,
        timestamp REAL,
        active INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blacklist (
        user_id INTEGER PRIMARY KEY,
        added_by INTEGER,
        reason TEXT,
        timestamp REAL,
        founder_count INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sanctions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        moderator_id INTEGER,
        type TEXT,
        reason TEXT,
        timestamp REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    conn.commit()
    conn.close()

def add_founder_bl(user_id, founder_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO founder_bl (user_id, founder_id) VALUES (?,?)",
        (user_id, founder_id)
    )

    conn.commit()
    conn.close()


def remove_founder_bl(user_id, founder_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM founder_bl WHERE user_id=? AND founder_id=?",
        (user_id, founder_id)
    )

    conn.commit()
    conn.close()

def add_custom_permission(user_id, command):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO custom_permissions (user_id, command) VALUES (?,?)",
        (user_id, command)
    )

    conn.commit()
    conn.close()


def remove_custom_permission(user_id, command):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM custom_permissions WHERE user_id=? AND command=?",
        (user_id, command)
    )

    conn.commit()
    conn.close()


def has_custom_permission(user_id, command):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM custom_permissions WHERE user_id=? AND command=?",
        (user_id, command)
    )

    data = cursor.fetchone()
    conn.close()

    return data is not None


def add_ban_detail(guild_id, user_id, mod_id, reason, channel_id, message_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO ban_details (
        guild_id, user_id, moderator_id,
        reason, channel_id, message_id,
        timestamp, active
    )
    VALUES (?,?,?,?,?,?,?,?)
    """, (
        guild_id,
        user_id,
        mod_id,
        reason,
        channel_id,
        message_id,
        time.time(),
        1
    ))

    conn.commit()
    conn.close()


def get_active_ban(guild_id, user_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT case_id, moderator_id, reason,
           channel_id, timestamp
    FROM ban_details
    WHERE guild_id=? AND user_id=? AND active=1
    ORDER BY case_id DESC
    LIMIT 1
    """, (guild_id, user_id))

    data = cursor.fetchone()
    conn.close()

    return data


def deactivate_ban(guild_id, user_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE ban_details
    SET active=0
    WHERE guild_id=? AND user_id=? AND active=1
    """, (guild_id, user_id))

    conn.commit()
    conn.close()


def add_sanction(user_id, mod_id, s_type, reason):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO sanctions (user_id, moderator_id, type, reason, timestamp)
    VALUES (?,?,?,?,?)
    """, (user_id, mod_id, s_type, reason, time.time()))

    conn.commit()
    conn.close()


def get_sanctions(user_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, type, reason, moderator_id
    FROM sanctions
    WHERE user_id=?
    ORDER BY id ASC
    """, (user_id,))

    data = cursor.fetchall()
    conn.close()

    return data


def delete_all_sanctions(user_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM sanctions WHERE user_id=?",
        (user_id,)
    )

    conn.commit()
    conn.close()


def add_blacklist(user_id, mod_id, reason, founder=False):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT founder_count FROM blacklist WHERE user_id=?",
        (user_id,)
    )

    data = cursor.fetchone()

    if not data:

        founder_count = 1 if founder else 0

        cursor.execute("""
        INSERT INTO blacklist (user_id, added_by, reason, timestamp, founder_count)
        VALUES (?,?,?,?,?)
        """, (user_id, mod_id, reason, time.time(), founder_count))

    else:

        current = data[0]

        if founder:
            cursor.execute("""
            UPDATE blacklist
            SET founder_count = ?, added_by=?, reason=?, timestamp=?
            WHERE user_id=?
            """, (current + 1, mod_id, reason, time.time(), user_id))

    conn.commit()
    conn.close()


def remove_blacklist(user_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM blacklist WHERE user_id=?",
        (user_id,)
    )

    conn.commit()
    conn.close()


def get_blacklist(user_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT added_by, reason, timestamp, founder_count
    FROM blacklist
    WHERE user_id=?
    """, (user_id,))

    data = cursor.fetchone()
    conn.close()

    return data


def get_all_blacklist():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT user_id, added_by, reason, timestamp, founder_count
    FROM blacklist
    """)

    data = cursor.fetchall()
    conn.close()

    return data