# Chat with AI - Streamlit Application

## Features

- **Token counter**: get number of tokens in the dialog and in the prompt being typed 
- **Azure and OpenAI supported**: Connect to OpenAI APIs either directly (via API key) or via models deployed in Microsoft Azure
- **Model Customization**: Users can add, update, and delete AI models with custom settings.
- **Single and Multi user**: Anonymous auth (single user) OR user authentication against a local YAML user DB (pairs of usernames/password hashes).
- **Chat Persistence**: Dialogs are saved on the server in flies and can be access acros different devices.
- **Data encryption**: All user data (chat dialogs and model settings) is encrypted using hashed keys (stored in users server-only cookies)
  - Loosing user creds means loosing stored user data. No pasword change is supported!
  - Protection against leaking sotred files. If the attacker can debug the server OR can steal cookies the encryption keys can be exposed
- **Environment Configuration**: Easy setup with environment variables or `.env` file.
- **Local and Debug Running**: Run the application locally or debug with VSCode.

## .env

Provide your Azure/OpenAI model credentials (API key, deployment URL, etc.) here. Users can also add their credentials in the web UI.

`DATA_DIR=".data"` - Directory where all conversations and model settings will be saved. Each user will have a `$username` subfolder.

`DISABLE_AUTH="False"` - If set to [True](file:///private/var/user/src/py_chat_ui/README.md#7%2C29-7%2C29), no login page will be shown, and all data will be stored under `$DATA_DIR/default_user`.

## Running Locally

1. Set OpenAI API credentials as environment variables or within the `.env` file (refer to `.env.template` for an example).
2. Install requirements with `pip3 install -r requirements.txt`.
3. Run the application using `streamlit run chat.py`.
4. Alternatively, debug in VSCode by pressing F5 and selecting the "Debug" configuration.