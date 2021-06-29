from db import add_account, add_user_account, check_account_exists
from db import check_userid_exists_in_accounts
from shared_functions import check_auth_code
from datetime import datetime


def create_account(account_type, amount, conf_label, int_label, auth_code):
    # creates a new account for user related with auth_code

    user_id = check_auth_code(auth_code)
    if user_id is None:
        # no user with supplied auth code
        return [11]

    account_id = add_account(account_type, amount, conf_label, int_label)
    add_user_account(user_id, account_id, 0)   # pending is 0 because it is creation of account not request for an account
    return [0, account_id]


def join(account_id, auth_code):
    # joins user_id related to auth_code in account with id account_id

    user_id = check_auth_code(auth_code)
    if user_id is None:
        return [11]
    
    if not check_account_exists(account_id):
        return [12]

    if check_userid_exists_in_accounts(user_id, account_id):
        return [12]
    
    add_user_account(user_id, account_id, 1, 0, 0)  # pending status is 1
    return [0]


def list_join_requests():
    pass
    

