import socket
import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from datetime import datetime

import re


def read_public_key(public_key_address='public_shared.pem'):
    with open(public_key_address, 'rb') as key:
        public_key = serialization.load_pem_public_key(key.read(), backend=default_backend())
    return public_key

def print_help():
    string = '''
    Available commands (case sensitive):
        Signup [username] [password]   : To use the system you shoud signup
        Login [username] [password]    : Before entering commands you should login first
        Create [account_type] [amount] [conf_label] [integrity_label]
                                       : Creates an account with specified type, initial amount,
                                         confidential label, integrity label.
                                         type is an integer between 1 and 4, also conf and int labels are
                                         integers between 1 and 4. Higher number higher security level
        Join [account_no]              : Sends a join request for account_no
        Accept [username] [account_no] [conf_label] [integrity_label]
                                       : Accepts join request of user_name with specified conf and int labels
        List [account_no]              : Lists all join requests for account_no if you are one of owners.
        Show_MyAccount                 : Prints all account numbers which you are joined.
        Show_Account [account_no]      : Prints last 5 transactions of account_no if you have correct access rights.
        Transfer [from_account_no] [to_account_no] [amount]
                                       : Transfers from from_account_no to to_account_no amount units of money.
                                         You should have correct access rights
        Deposit [to_account_no] [amount]
                                       : Deposits amount unit of money to to_account_no. No access right is needed.
        Withdraw [from_account_no] [amount]
                                       : Withdraws amount unit of money from from_account_no if you have correct access rights    
        Logout:                        : Logs out of account
    '''
    print(string)


command_args_counts = {
    'Signup': 2,
    'Login': 2,
    'Create': 4,
    'Join': 1,
    'Accept': 4,
    'List': 1,
    'Show_MyAccount': 0,
    'Show_Account': 1,
    'Transfer': 3,
    'Deposit': 2,
    'Withdraw': 2,
    'Logout': 0
}


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
    18: 'Not enough amount',
    19: 'Can\'t accept users with higher permissions than yourself',
    20: 'Low integrity labels for user',
    21: 'Low confidentiality labels for user',
    22: 'Wrong input'

}

def intepret_response(command, response):
    # interpretes response recieved from server
    # command is the request sent to server
    if command.startswith('Signup'):
        print(*(errors[int(error)] for error in response.split()), sep='\n')
    elif command.startswith('Login'):
        if response.startswith('0 '):
            print('Successful!')
        else:
            print('Wrong credentials!')
    elif command.startswith('Create'):
        if response.startswith('0 '):
            print('Successful!. account id is ' + response[2:])
        else:
            print('Please first login!')
    elif command.startswith('Join'):
        print(*(errors[int(error)] for error in response.split()), sep='\n')
    elif command.startswith('Accept'):
        print(*(errors[int(error)] for error in response.split()), sep='\n')
    elif command.startswith('List'):
        if response.startswith('0 '):
            print('Successful!')
            for item in response.split()[1:]:
                print(item)
        else:
            print(*(errors[int(error)] for error in response.split()), sep='\n')
    elif command.startswith('Show_MyAccount'):
        if response.startswith('11'):
            print('Please first login!')
        else:
            print('Successful!')
            res = re.findall(r'\((\d+),\s*\)', response[1:])
            print(*res, sep='\n')
    elif command.startswith('Show_Account'):
        if response.startswith('0 '):
            print('Successful!')
            res = re.findall(r'\((\-?\d+), \'([^\']*)\'\)', response)
            for item in res:
                print('Changed: ' + item[0] + ' at ' + item[1])
            print('Current amount is ' + response.split()[-1])
        else:
            print(*(errors[int(error)] for error in response.split()), sep='\n')
    elif command.startswith('Transfer'):
        print(*(errors[int(error)] for error in response.split()), sep='\n')
    elif command.startswith('Deposit'):
        print(*(errors[int(error)] for error in response.split()), sep='\n')
    elif command.startswith('Withdraw'):
        print(*(errors[int(error)] for error in response.split()), sep='\n')
    else:
        print('Could not find command')

def check_replay(response, threshold=180):
    # checks if the response is a replayed response or not
    time = ' '.join(response.split()[:2])  # first two parts of response is related to time
    time = datetime.strptime(time, datetime_format)
    now = datetime.now()
    s = (now - time).seconds
    s = s ** 2 ** 0.5   # absolute value of seconds
    if s > threshold:
        # is a replayed response
        return True
    return False

host = 'localhost'
port = 23654
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))
sock.settimeout(20)

public_key = read_public_key()
key = Fernet.generate_key()   # session key
encrypted = public_key.encrypt(
    key, padding.OAEP(padding.MGF1(hashes.SHA256()), hashes.SHA256(), None)
)

sock.sendall(encrypted)
fernet = Fernet(key)

auth_code = ''
prompt = '>>> '
datetime_format = '%d-%m-%Y %H:%M:%S'

print('--- Welcome ---')
print('Now you can Enter your commands. You can Enter "?" to see help')


while True:
    command = input(prompt)
    if command == '?':
        print_help()
        continue
    command = command.split()
    if command[0] not in command_args_counts:
        print('Wrong command!')
        continue
    
    if len(command) != command_args_counts[command[0]] + 1:
        print('Wrong args. To see help enter "?"')
        continue

    if command[0] not in ['Signup', 'Login', 'Logout'] and auth_code == '':
        # user is not loged in
        print('Please login first!')
        continue

    if command[0] == 'Login' or command[0] == 'Signup' or command[0] == 'Logout':
        auth_code = ''
        prompt = '>>> '         
        if command[0] == 'Logout':
            continue

    command = ' '.join(command)

    now = datetime.now().strftime(datetime_format)
    sock.send(fernet.encrypt((now + ' ' + command + ' ' + auth_code).encode()))
    try:
        res = sock.recv(1024)
    except socket.timeout:
        print('Servr can\'t answer right now')
        break
    res = fernet.decrypt(res).decode()

    if check_replay(res):
        print('A replay attack is detected. Be careful what are you doin!')
        continue

    res = ' '.join(res.split()[2:])  # removin timestamp

    intepret_response(command, res)
    if command.startswith('Login') and res.startswith('0 '):
        auth_code = res.split()[1]
        prompt = f'({command.split()[1]}) >>> '




