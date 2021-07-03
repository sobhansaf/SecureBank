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
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


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


def decrypt_asymmetric(encrypted, private_key):
    res = private_key.decrypt(
        encrypted,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    ))
    return res


fernet = None
port = 23654
host = '127.0.0.1'

db_init()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((host, port))
sock.listen()
con, addr = sock.accept()
private_key = read_private_key()

encrypted_session_key = con.recv(1024)
session_key = decrypt_asymmetric(encrypted_session_key, private_key)
fernet = Fernet(session_key)

while True:
    try:
        data = con.recv(1024)
        if not data:
            break
        data = fernet.decrypt(data).decode().strip()
        data = data.split()
        res = server_commands[data[0]](*data[1:])
        res = list(map(str, res))
        res = fernet.encrypt((' '.join(res)).encode())
        con.sendall(res)
    except KeyboardInterrupt:
        break
    except:
        pass

sock.close()
