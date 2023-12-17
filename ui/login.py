import streamlit as st
import streamlit_authenticator_2 as stauth
import os
import yaml
from yaml.loader import SafeLoader
from logic import env_vars
from logic.crypto import generate_fernet_key
from ui.ui_helpers import login_background, register_button_as_link

users_file: str = os.path.join(env_vars.env_data_folder, 'users.yaml')

# Load the configuration file with the user credentials
if not env_vars.env_disable_auth:
    if not os.path.exists(users_file):
        os.makedirs(os.path.dirname(users_file), exist_ok=True)
        with open(users_file, 'w') as file:
            file.write("""
credentials:
  usernames:
cookie:
  expiry_days: 30
  key: 856_some_$0-signature_key
  name: strmlt-pld
""")
    with open(users_file) as file:
        config = yaml.load(file, Loader=SafeLoader)


def get_auth(config):
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        # config['preauthorized']
    )
    return authenticator


def authenticate() -> stauth.Authenticate | str | None:
    """
    Call this function to check if the user is authenticated.
    If the user is not authenticated, it will display the login screen.

    Returns:
        bool: None if auth is not present, True if the user is authenticated, "disabled" if authentication is diabled
    """

    if env_vars.env_disable_auth:
        return 'dsaibled'

    authenticator = get_auth(config)

    # authenticator.login('Login', 'main')
    # Init session vars without showing a login to avoid UI blinking
    if not st.session_state.get("cookie_checked", False):
        authenticator._check_cookie()
        st.session_state["cookie_checked"] = True
        return None

    authenticator._check_cookie()

    if st.session_state.get("authentication_status", None):
        return authenticator
    else:
        if 'view_mode' not in st.session_state:
            st.session_state['view_mode'] = 'login'

        register_button_as_link()
        login_background()

        if st.session_state['view_mode'] == 'login':
            if not env_vars.env_disable_user_registration and st.button('Register a new user'):
                st.session_state['view_mode'] = 'register'
                st.rerun()
            # Call generate_fernet_key insternally, pass user name and passwrod and keep the key in server cookies
            authenticator.login('', 'main', generate_fernet_key)
            if st.session_state["authentication_status"] is False:
                st.error('Username/password is incorrect')

        elif st.session_state['view_mode'] == 'register':
            if st.button('⇠ Back to login'):
                st.session_state['view_mode'] = 'login'
                st.rerun()
            try:
                if authenticator.register_user('Register a new user', preauthorization=False, skipEmail=True):
                    st.success('User registered successfully')
                    with open(users_file, 'w') as file:
                        yaml.dump(config, file, default_flow_style=False)
                    # st.session_state['view_mode'] = 'login'
            except Exception as e:
                st.error(e)

        # elif st.session_state["authentication_status"] is None:
        #     st.warning('Please enter your username and password')
        return None


def get_user_name() -> str | None:
    """
    Get the username of the authenticated user.

    Returns:
        Optional[str]: The name of the user if authenticated, otherwise None.
    """
    if env_vars.env_disable_auth:
        return 'default_user'
    return st.session_state.get("username", None)


def get_enc_key() -> bytes | None:
    """
    Get the extra payload from the session state if the user is authenticated.

    Returns:
        Optional[bytes]: The extra payload if present, otherwise None.
    """
    if env_vars.env_disable_auth:
        return generate_fernet_key('default', 'default')
    return st.session_state.get("auth_extra_payload", None)


def show_logout(authenticator: stauth.Authenticate | str) -> None:
    assert isinstance(authenticator, stauth.Authenticate) or \
           isinstance(authenticator, str), \
           "Parameter must be an instance of 'stauth.Authenticate' or 'str'"
    if not isinstance(authenticator, stauth.Authenticate):
        return
    authenticator.logout(f'Logout: *{st.session_state["username"]}*', 'main')
