# Chat with AI - Streamlit Application

## Features

- **Token counter**: get number of tokens in the dialog and in the prompt being typed 
- **AI Model Integration**: Connect to OpenAI and Azure AI models for generating chat responses.
- **User Management**: Supports user authentication and individual user data storage.
- **Model Customization**: Users can add, update, and delete AI models with custom settings.
- **Session Persistence**: Chat sessions are saved and can be revisited or resumed.
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

## Solution Overview

This Streamlit-based web application allows users to interact with AI models from OpenAI and Azure for a conversational experience. The backend is structured to handle user sessions, AI model management, and message storage, ensuring a seamless chat experience.

### Backend

- **Model Management**: The [Model](file:///private/var/user/src/py_chat_ui/logic.py#11%2C7-11%2C7) and `ModelRepository` classes handle AI model configurations.
- **Session Handling**: The `ChatSession` and [ChatSessionManager](file:///private/var/user/src/py_chat_ui/logic.py#132%2C7-132%2C7) classes manage chat sessions and message persistence.
- **Environment Variables**: Configurations are managed through environment variables, as outlined in `env_vars.py`.

### Frontend

- **Streamlit UI**: The `chat.py` script provides a user-friendly interface for interacting with the AI models and managing chat sessions.
- **User Authentication**: The application supports user login to maintain separate chat histories.