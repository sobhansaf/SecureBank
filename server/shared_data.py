# letters is used to generate random strings for salt and authorization code
letters = 'qwertyuiopasdfghjklzxcvbnm'
letters += letters.upper()
letters += '0123456789'
letters += '~!@#$%^&*()_+=-{[}]|\\/:;"\'<>,.?'


# error codes
errors = {
    0: 'Successful',
    # sign up--------
    1: 'Username exists',
    2: 'Long username',
    3: 'Dictionary password',
    4: 'No lower case',
    5: 'No upper case',
    6: 'No special character',
    7: 'No digits',
    8: 'Less than 8 character',
    9: 'Same 3 or more consecutive characters',
    # -------------------
    # login -------------
    10: 'Wrong credentials',
    11: 'User not loged in',
    # -------------------
    # accouont-----------
    12: 'Could not join',
    13: 'No permission',
    14: 'User has not requested to join',
    15: 'Invalid amount',
    16: 'From_account_id is wrong',   # in deposit
    17: 'To_account_id is wrong',
    18: 'Not enough amount'
}