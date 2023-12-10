import streamlit as st
from logic.user_state import init
from ui.login import authenticate, show_logout, get_user_name, get_enc_key
from ui.chat import show_chat
from logic.crypto import *

st.set_page_config(
    page_title="Py Chat",
    page_icon="ツ"
)

if auth:=authenticate():
    user = get_user_name()
    if user is not None:
        try:
            init(user, get_enc_key())
            show_chat(lambda: show_logout(auth))
        except Exception as e:
            st.error(f'Error in main: {e}')
            show_logout(auth)
            raise e