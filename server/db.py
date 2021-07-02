import sqlite3
from hashlib import sha256
from random import choice
import shared_functions
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
            account_type INTEGER NOT NULL CHECK (account_type > 0 AND account_type < 5),
            amount INTEGER NOT NULL CHECK (amount >= 0),
            conf_label INTEGER NOT NULL CHECK (conf_label > 0 AND conf_label < 5),  -- 4:TS  1:U 
            int_label INTEGER NOT NULL CHECK (int_label > 0 AND int_label < 5)      -- 4:VT  1:U
        );
    ''')

    # account_id should be a 10 digit number
    cur.execute('''
        INSERT INTO account(account_id, account_type, amount, conf_label, int_label) VALUES (999999999, 1, 1, 1, 1);
    ''')

    cur.execute('''
        DELETE FROM account WHERE account_id = 999999999;
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS account_users (
            user_id INTEGER,
            account_id INTEGER,
            pending INTEGER,
            user_conf_label INTEGER CHECK (user_conf_label >= 0 AND user_conf_label < 5), -- TS:4   U:1  0: pending
            user_int_label INTEGER CHECK (user_int_label >= 0 AND user_int_label < 5),  -- VT:4   U:1     0: pending
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

    cur.execute('''
        CREATE TABLE IF NOT EXISTS transfer (
            transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_account_id INTEGER NOT NULL,
            to_account_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            date VARCHAR(30),
            FOREIGN KEY (from_account_id) REFERENCES account (account_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (to_account_id) REFERENCES account (account_id)
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
    salt = shared_functions.generate_random_string(6)
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

def get_user_labels_in_account(user_id, account_id):
    cur.execute('SELECT user_conf_label, user_int_label FROM account_users WHERE user_id=? AND account_id = ?',
                (user_id, account_id))
    return cur.fetchone()

def add_auth_code(user_id, auth_code=None):
    # gets a user_id and an auth_code. adds it into auth_codes table
    if auth_code is None:
        auth_code = sha256(shared_functions.generate_random_string(20).encode()).hexdigest()
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

def add_user_account(user_id, account_id, pending, user_conf_label=4, user_int_label=4):
    # adds a new account_user record
    cur.execute('INSERT INTO account_users(user_id, account_id, pending, user_conf_label, user_int_label) VALUES (?, ?, ?, ?, ?)',
                (user_id, account_id, pending, user_conf_label, user_int_label))
    con.commit()

def check_account_exists(account_id):
    cur.execute('SELECT account_id FROM account WHERE account_id=?', (account_id, ))
    return cur.fetchone()

def check_userid_exists_in_accounts(user_id, account_id):
    cur.execute('SELECT user_id FROM account_users WHERE user_id = ? AND account_id = ?', (user_id, account_id))
    return cur.fetchone()

def is_owner(user_id, account_id):
    # checks whether user_id is an acitve owner of account_id or not
    cur.execute('SELECT user_id FROM account_users WHERE user_id = ? AND account_id = ? AND pending=0',
                (user_id, account_id))
    return cur.fetchone()

def get_account_labels(account_id):
    cur.execute('SELECT conf_label, int_label FROM account WHERE account_id=?', (account_id, ))
    return cur.fetchone()

def get_join_requests(account_id):
    cur.execute('''
        SELECT username FROM
            account_users JOIN user ON user.user_id = account_users.user_id
            WHERE account_id = ? AND pending=1    
    ''', (account_id, ))
    return cur.fetchall()

def has_user_requested(username, account_id):
    # if user with supplied user name requested to join to an account this function returns user_id
    cur.execute('''
        SELECT user.user_id FROM account_users
            JOIN user ON user.user_id = account_users.user_id
            WHERE username = ? AND account_id = ? AND pending = 1;
    ''', (username, account_id))
    return cur.fetchone()

def remove_pending_status(user_id, account_id,  conf_label, int_label):
    cur.execute('UPDATE account_users SET pending=0, user_conf_label=?, user_int_label=? WHERE user_id=? AND account_id=?',
                (conf_label, int_label, user_id, account_id))
    con.commit()

def get_all_accounts(user_id):
    cur.execute('SELECT account_id FROM account_users WHERE user_id = ? AND pending=0', (user_id, ))
    return cur.fetchall()

def get_account_amount(account_id):
    cur.execute('SELECT amount FROM account WHERE account_id = ?', (account_id, ))
    return cur.fetchone()

def add_transfer(from_, to, amount):
    now = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    cur.execute('''
        INSERT INTO transfer(from_account_id, to_account_id, amount, date) VALUES (?, ?, ?, ?);
    ''', (from_, to, amount, now))
    con.commit()

def change_amount(acc_id, amount):
    cur.execute('UPDATE account SET amount = amount + ? WHERE account_id = ?', (amount, acc_id))
    con.commit()


