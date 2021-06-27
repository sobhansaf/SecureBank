import sqlite3

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

    con.commit()








