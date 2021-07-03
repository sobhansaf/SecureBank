import socket
import signup
import login
import account
from db import db_init

import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet

server_commands = {
    'Signup': signup.sign_up,
    'Login': login.login,
    'Create': account.create_account,
    'Join': account.join ,
    'List': account.list_join_requests,
    'Accept': account.accept_join_request,
    'Show_MyAccount': account.show_my_account,
    'Transfer': account.transfer,
    'Show_Account': account.show_my_account,
    'Deposit': account.deposit,
    'Withdraw': account.withdraw
}

def read_private_key(private_key_address='private.pem'):
    with open(private_key_address, 'rb') as key:
        private_key = serialization.load_pem_private_key(key.read(), password=None, backend=default_backend())
    
    return private_key


port = 23654
host = '127.0.0.1'

db_init()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((host, port))
sock.listen()
con, addr = sock.accept()

while True:
    try:
        data = con.recv(1024).decode().strip()
        data = data.split()
        res = server_commands[data[0]](*data[1:])
        res = list(map(str, res))
        con.sendall(' '.join(res).encode())
    except KeyboardInterrupt:
        break
    except:
        pass

sock.close()
