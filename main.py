from logic import init
from login import authenticate, show_logout, get_user_name
from chat import show_chat

if auth:=authenticate():
    user = get_user_name()
    if user != None:
        init(get_user_name())
        show_chat(lambda: show_logout(auth))

