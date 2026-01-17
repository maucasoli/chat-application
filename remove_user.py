from database import remove_user

username = input("Username: ")

remove_user(username)
print(f"Username '{username}' removed!")
