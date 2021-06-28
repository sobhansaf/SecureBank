import sqlite3
from hashlib import sha256
from random import choice
from shared_functions import generate_random_string
from datetime import datetime

con, cur = None, None


def db_init():
    global con, cur
    db_name = 'secure.db'
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS user (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(30) NOT NULL,
                password CHAR(70) NOT NULL   -- 64 character for result of sha256 and first 6 character for salt.
            );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS account (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_type INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            conf_label INTEGER NOT NULL,
            int_label INTEGER NOT NULL
        );
    ''')

    # account_id should be a 10 digit number
    cur.execute('''
        INSERT INTO account(account_id, account_type, amount, conf_label, int_label) VALUES (999999999, 0, 0, 0, 0);
    ''')

    cur.execute('''
        DELETE FROM account WHERE account_id = 999999999;
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS account_users (
            user_id INTEGER,
            account_id INTEGER,
            pending INTEGER,
            FOREIGN KEY (user_id) REFERENCES user (user_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (account_id) REFERENCES account (account_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS auth_codes (
            auth_id INTEGER PRIMARY KEY AUTOINCREMENT,
            auth_code CHAR(64) NOT NULL,
            user_id INTEGER NOT NULL,       
            creation_date_time VARCHAR(30),
            FOREIGN KEY (user_id) REFERENCES user(user_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );
    ''')

    con.commit()


def check_username_exists(username):
    cur.execute('SELECT user_id FROM user WHERE username=?', (username,))
    if cur.fetchone():
        # there exists a user with specified username
        return True
    return False


def insert_user(user_name, password):
    # adds a new user
    salt = generate_random_string(6)
    cur.execute('insert into user(username, password) values(?, ?)', 
                (user_name, salt + sha256((salt + password).encode()).hexdigest()))
    con.commit()


def validate_user(username, password):
    cur.execute('SELECT password, user_id FROM user WHERE username=?', (username,))
    user_data = cur.fetchone()
    if not user_data:
        # no user with supplied username
        return False
    hashed_salted_pass = user_data[0]
    salt = hashed_salted_pass[:6]
    if sha256((salt + password).encode()).hexdigest() == hashed_salted_pass[6:]:
        # right password
        return user_data[1]  # returns user_id
    else:
        return False


def get_user_id_with_auth(auth_code):
    # gets an auth code. returns its matched user_id and creation date of the auth code
    cur.execute('SELECT user_id, creation_date_time FROM auth_codes WHERE auth_code=?', (auth_code,))
    return cur.fetchone()


def add_auth_code(user_id, auth_code=None):
    # gets a user_id and an auth_code. adds it into auth_codes table
    if auth_code is None:
        auth_code = sha256(generate_random_string(20).encode()).hexdigest()
    now = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    cur.execute('INSERT INTO auth_codes(auth_code, user_id, creation_date_time) VALUES (?, ?, ?)', (auth_code, user_id, now))
    con.commit()
    return auth_code


def delete_auth_code(auth_code):
    cur.execute('DELETE FROM auth_codes WHERE auth_code=?', (auth_code, ))
    con.commit()


def add_account(account_type, amount, conf_label, int_label):
    # adds a new account in database
    cur.execute('INSERT INTO account(account_type, amount, conf_label, int_label) VALUES (?, ?, ?, ?)',
                (account_type, amount, conf_label, int_label))
    con.commit()
    return cur.lastrowid


def add_user_account(user_id, account_id, pending):
    # adds a new account_user record
    cur.execute('INSERT INTO account_users(user_id, account_id, pending) VALUES (?, ?, ?)', (user_id, account_id, pending))
    con.commit()



