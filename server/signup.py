from db import *
import re
import sqlite3
from random import choice
from shared_data import letters


def check_password_strength(password):
    result = list()   # a list of weaknesses of password. thie variable will be returned
    
    # 1. dictionary
    con = sqlite3.connect('passwords.sqlite3')
    cur = con.cursor()
    cur.execute('select * from password where password = ?', (password, ))
    
    if cur.fetchone():
        result.append(3)
    con.close()

    # 2. lower case
    if not re.search('[a-z]', password):
        result.append(4)

    # 3. upper case
    if not re.search('[A-Z]', password):
        result.append(5)   

    # 4. special characters
    if not re.search(r'[~!@#$%^&*()_+=\-{\[}\]|\\\/:;"\'<>,.?]', password):
        result.append(6)

    # 5. digits
    if not re.search('\d', password):
        result.append(7)
    
    # 6. password length
    if len(password) <= 8:
        result.append(8)

    # 7. same consecutive charachters
    if re.search(r'(.)\1{2,}', password):
        result.append(9)

    return result
    
    

def sign_up(username, password):
    # gets a username and a password. returns a user object after logging in.

    # 1. check username
    if check_username_exists(username):
        return [1]
    
    if len(username) > 30:
        return [2]
    
    pass_weaknesses = check_password_strength(password)
    if pass_weaknesses:
        # if there was an item in pass strength
        return pass_weaknesses

    insert_user(username, password)

    return True

