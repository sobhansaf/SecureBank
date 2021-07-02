from db import *
from shared_functions import check_auth_code
from datetime import datetime


# todo: users with low security level can't add users with high security levels



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


def list_join_requests(account_id, auth_code):
    # lists user_ids which has requested to join to an account

    user_id = check_auth_code(auth_code)
    if user_id is None:
        return [11]

    if not is_owner(user_id, account_id):
        # user is not the owner of the account.
        return [13]

    res = list()
    res.append(0)
    requests = get_join_requests(account_id)
    if not requests:
        # There is no join requests for joining the account
        return res
    requests = list(map(lambda x: x[0], requests))
    res.extend(requests)
    return res

def accept_join_request(user_name, account_id, conf_label, int_label, auth_code):
    # adds a new user to the owners of the account

    user_id = check_auth_code(auth_code)   # this is the user_id of the user who wants to accept the join request
    if user_id is None:
        return [11]

    if not is_owner(user_id, account_id):
        # user is not the owner of the account.
        return [13]

    user_id = has_user_requested(user_name, account_id)  # this is the user_id of the user who requested to join
    if not user_id:
        # user has not requested for joining
        return [14]

    user_id = user_id[0]
    
    remove_pending_status(user_id, account_id, int(conf_label), int(int_label))
    return [0]

def show_my_account(auth_code):
    # returns all account information for user with given auth_code

    user_id = check_auth_code(auth_code)   
    if user_id is None:
        return [11]

    accounts = get_all_accounts(user_id)
    if accounts is None:
        # user has no account
        return [0]

    accounts.insert(0, 0)
    return accounts

def transfer(from_acc_id, to_acc_id, amount, auth_code):
    # fransfers from from_acc_id to to_acc_id with amount
    user_id = check_auth_code(auth_code)   
    if user_id is None:
        return [11]

    if not is_owner(user_id, from_acc_id):
        # user is not the owner of the account.
        return [13]

    # user's integrity label should be higher than account
    account_labels = get_account_labels(from_acc_id)
    user_labels = get_user_labels_in_account(user_id, from_acc_id)

    if user_labels[1] < account_labels[1]:  # index one of labels are related to integrity label
        # user is not authorized to deposit.
        return [13]

    errors = list()
    if amount < 1:
        errors.append(15)
    
    current_amount = get_account_amount(from_acc_id)  # returns current amount of account of depositor
    if current_amount is None:
        # from_acc_id doesn't exist
        errors.append(16)

    if not check_account_exists(to_acc_id):
        # to_acc_id doesn't exist
        errors.append(17)
    
    current_amount = current_amount[0]   # current amount is returning value of fetchone() which is a tuple

    if current_amount < amount:
        # not enough amount in from_acc_id
        errors.append(18)

    if errors:
        return errors

    change_amount(from_acc_id, -amount)
    change_amount(to_acc_id, amount)
    
    add_transaction(from_acc_id, -amount)
    add_transaction(to_acc_id, amount)
    return [0]

def deposit(to_account_id, amount, auth_code):
    # deposits amount unit of money to to_account_id
    user_id = check_auth_code(auth_code)   
    if user_id is None:
        return [11]

    if not check_account_exists(to_account_id):
        # to_account_id doesn't exist
        return [17]

    if amount < 1:
        return [15]

    change_amount(to_account_id, amount)
    add_transaction(to_account_id, amount)
    
    return [0]

    
