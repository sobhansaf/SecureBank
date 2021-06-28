from db import validate_user, add_auth_code, db_init
from shared_functions import generate_random_string
from hashlib import sha256

def login(username, password):
    # returns false if credential is invalid, and returns a user_id if matched with credentials
    user_id = validate_user(username, password)
    if not user_id:
        # credentials don't exist or are wrong
        return 10
    
    auth_code = sha256(generate_random_string(20).encode()).hexdigest()
    add_auth_code(user_id, auth_code)
    return 0, auth_code


