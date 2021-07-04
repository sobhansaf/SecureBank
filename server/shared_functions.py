from shared_data import letters
from random import choice
from datetime import datetime
import db


def generate_random_string(length):
    # generates a random string which its length is as input
    res = ''.join([choice(letters) for _ in range(length)])
    return res


def check_expiration(first, second, limit):
    # first and second is two datetime objects
    # this function checks whether the difference between first and second is less than
    # limit or not
    # limit is an integer representing the limited seconds.
    # returns true if difference of first an second is less than limit in seconds

    return (second - first).seconds < limit


def check_auth_code(auth_code):
    # if user with auth_code exists this function returns user_id related to auth_code
    # expiration time for auth_code is 30 minutes 

    user_data = db.get_user_id_with_auth(auth_code)  # returns None if nothing was found
    if user_data is None:
        return None
    
    date = datetime.strptime(user_data[1], '%d-%m-%Y %H:%M:%S')
    now = datetime.now()
    
    if not check_expiration(date, now, 30 * 60):
        # auth_code is expired
        db.delete_auth_code(auth_code)
        return None

    return user_data[0]  # returns user _id