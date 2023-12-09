import streamlit as st
import streamlit_authenticator as stauth
import os
import yaml
from yaml.loader import SafeLoader
from env_vars import env_data_folder, env_disable_auth

users_file: str = os.path.join(env_data_folder, 'users.yaml')

# Load the configuration file with the user credentials
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

    if env_disable_auth:
        return 'dsaibled'

    authenticator = get_auth(config)
    #authenticator.login('Login', 'main')
    # Init session vars without showing a login form as suggested by docs to avoid UI blocking
    authenticator._check_cookie()

    if st.session_state.get("authentication_status", None):
        return authenticator
    else:
        authenticator.login('Login', 'main')
        if st.session_state["authentication_status"] is False:
            st.error('Username/password is incorrect')
        elif st.session_state["authentication_status"] is None:
            st.warning('Please enter your username and password')
        return None

def get_user_name() -> str | None:
    """
    Get the username of the authenticated user.

    Returns:
        Optional[str]: The name of the user if authenticated, otherwise None.
    """
    if env_disable_auth:
        return 'default_user'
    return st.session_state.get("username", None)

def show_logout(authenticator: stauth.Authenticate | str) -> None:
    assert isinstance(authenticator, (stauth.Authenticate, str)), "Parameter must be an instance of 'stauth.Authenticate' or 'str'"
    if not isinstance(authenticator, stauth.Authenticate):
        return
    authenticator.logout(f'Logout: *{st.session_state["username"]}*', 'main', key='unique_key')







