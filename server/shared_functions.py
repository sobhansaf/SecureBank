from shared_data import letters
from random import choice


def generate_random_string(length):
    # generates a random string which its length is as input
    res = ''.join([choice(letters) for _ in range(length)])
    return res


