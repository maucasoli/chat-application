import getpass
from database import save_user

username = input("Username: ")
password = getpass.getpass("Password: ")

save_user(username, password)
print(f"Username '{username}' created!")
