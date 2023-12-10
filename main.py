from logic import init
from login import authenticate, show_logout, get_user_name
from chat import show_chat
from crypto import *

if auth:=authenticate():
    user = get_user_name()
    if user is not None:
        try:
            init(user, generate_fernet_key("pass"))
            show_chat(lambda: show_logout(auth))
        except Exception as e:
            show_logout(auth)
            raise e


