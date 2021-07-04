import socket
import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


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
        Accept [username] [conf_label] [integrity_label]
                                       : Accepts join request of user_name with specified conf and int labels
        List [account_no]              : Lists all join requests for account_no if you are one of owners.
        Show_MyAccoun                  : Prints all account numbers which you are joined.
        Show_Account [account_no]      : Prints last 5 transactions of account_no if you have correct access rights.
        Transfer [from_account_no] [to_account_no] [amount]
                                       : Transfers from from_account_no to to_account_no amount units of money.
                                         You should have correct access rights
        Deposit [to_account_no] [amount]
                                       : Deposits amount unit of money to to_account_no. No access right is needed.
        Withdraw [from_account_no] [amount]
                                       : Withdraws amount unit of money from from_account_no if you have correct access rights    
    '''
    print(string)


host = 'localhost'
port = 23654
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

public_key = read_public_key()
key = Fernet.generate_key()   # session key
encrypted = public_key.encrypt(
    key, padding.OAEP(padding.MGF1(hashes.SHA256()), hashes.SHA256(), None)
)

sock.sendall(encrypted)
fernet = Fernet(key)

auth_code = ''

print('--- Welcome ---')
print('Now you can Enter your commands. You can Enter "?" to see help')


while True:
    command = input('>>> ')
    if command == '?':
        print_help()
        continue
    sock.send(fernet.encrypt((command + ' ' + auth_code).encode()))
    res = sock.recv(1024)
    res = fernet.decrypt(res).decode()
    print(res)
    if command.startswith('Login'):
        auth_code = res.split()[1]




