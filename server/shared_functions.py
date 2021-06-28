from shared_data import letters
from random import choice
from datetime import datetime


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
