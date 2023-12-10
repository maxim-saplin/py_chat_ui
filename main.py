from logic import init
from login import authenticate, show_logout, get_user_name, get_enc_key
from chat import show_chat
from crypto import *

if auth:=authenticate():
    user = get_user_name()
    if user is not None:
        try:
            init(user, get_enc_key())
            show_chat(lambda: show_logout(auth))
        except Exception as e:
            show_logout(auth)
            raise e


