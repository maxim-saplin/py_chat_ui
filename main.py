__version__ = '0.1.3'

import streamlit as st
from logic.user_state import init
from ui.login import authenticate, show_logout, get_user_name, get_enc_key
from ui.home import show_home
from ui.ui_helpers import global_ui_tweaks, hide_streamlit_menu, hide_streamlit_toolbar
import time


print('Py Chat, Request received')
start_time = time.time()

st.set_page_config(
    page_title='Py Chat',
    page_icon='ツ'
)

st.session_state['version'] = __version__

hide_streamlit_menu()
hide_streamlit_toolbar()
global_ui_tweaks()

if auth := authenticate():
    user = get_user_name()
    if user is not None:
        try:
            init(user, get_enc_key())
            show_home(lambda: show_logout(auth))
        except Exception as e:
            st.error(f'Error in the main loop: {e}')
            show_logout(auth)
            raise e

print(f'Py Chat, Request done in {(time.time() - start_time) * 1000:.2f} ms')
