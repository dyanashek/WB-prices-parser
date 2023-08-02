import sqlite3
import logging
import config

database = sqlite3.connect("db.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
cursor = database.cursor()

try:
    # creates table with new users and their referrals
    cursor.execute(f'''CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        user_id TEXT,
        counter INTEGER DEFAULT {config.FREE_REQUESTS},
        subscribe BOOLEAN DEFAULT FALSE,
        valid_till TIMESTAMP,
        autorenew BOOLEAN DEFAULT FALSE,
        payment_method_id TEXT,
        referral TEXT,
        balance REAL DEFAULT 0
    )''')
except Exception as ex:
    logging.error(f'Users table already exists. {ex}')


try:
    # creates table with new users and their referrals
    cursor.execute('''CREATE TABLE payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        amount REAL,
        days INTEGER,
        referral TEXT,
        payment_id TEXT,
        finished BOOLEAN DEFAULT FALSE,
        success BOOLEAN,
        message_id TEXT,
        payment_time TIMESTAMP 
    )''')
except Exception as ex:
    logging.error(f'Payments table already exists. {ex}')

# cursor.execute("DELETE FROM referrals WHERE id<>1000")
# database.commit()