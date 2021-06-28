from db import get_user_id_with_auth, delete_auth_code, add_account, add_user_account
from shared_functions import check_expiration
from datetime import datetime


def create_account(account_type, amount, conf_label, int_label, auth_code):
    # creates a new account for user related with auth_code

    # if user exists following function returns user_id related to auth_code
    # and the time when auth code was given to user
    # expiration time for auth_code is 30 minutes 
    user_data = get_user_id_with_auth(auth_code)
    if user_data is None:
        # authcode is wrong.
        return [11]   # code for users which are not loged in
    
    date = datetime.strptime(user_data[1], '%d-%m-%Y %H:%M:%S')
    now = datetime.now()
    
    if not check_expiration(date, now, 30 * 60):
        delete_auth_code(auth_code)
        return [11]

    user_id = user_data[0]

    account_id = add_account(account_type, amount, conf_label, int_label)
    add_user_account(user_id, account_id, 0)   # pending is 0 because it is creation of account not request for an account
    return [0, account_id]

    





