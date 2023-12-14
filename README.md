# Py Chat

Your private chat UI for OpenaAI/Azure APIs. Deploy anywhere, fill in API Key etc. and get your own ChatGPT. [Live demo](https://pychatui.streamlit.app)

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/b097f9bd-795b-44cc-acfd-931b1e889699)

## Features

- **Minimal, responsivee UI**: supports PWA, can be added to home-screen on mobile and work as full-screen app
- **Token counter**: get number of tokens in the dialog and in the prompt being typed
  - Can be seen at the top right corner, counts dialog length + the number of tokens in the promnpt being typed
- **Azure and OpenAI**: Connect to OpenAI APIs either directly (via API key) or via models deployed in Microsoft Azure
- **Can be deployed as a single container:** no dependencies on Postgress, all data is stored in local files and encrypted
-   `docker pull ghcr.io/maxim-saplin/py_chat_ui:latest`
- **Response srtreaming**: see how OpneAI is typing back
- **Model Customization**: Users can add, update, and delete AI models with custom settings in UI OR have a mode defined in ENV variables
- **Single and Multi user**: Anonymous authentication (single user) with not lock screen OR user authentication against a local user DBin a YAML file (pairs of usernames/password hashes).
- **Chat Persistence**: Dialogs are saved on the server in flies and can be access acros different devices.
- **Data encryption**: All user data (chat dialogs and model settings) is encrypted using hashed keys (stored in user's server-only/http-only cookies)
  - Loosing user creds means loosing stored user data. No pasword change is supported!
  - Protection against leaking sotred files. If the attacker can debug the server OR can steal cookies the encryption keys can be exposed
- **Environment Configuration**: Easy setup with environment variables or `.env` file.
- **Run and Debug localy**: Run the application locally or via Docker, or debug with VSCode

## Evironment variables

You can configure the app either via setting environment variables or puttin values into `.env` file (see `.env.template` for an example).

| Environment Variable | Description | Default Value |
|----------------------|-------------|---------------|
| `OPENAI_API_KEY`     | The API key for OpenAI or Azure | None |
| `API_TYPE`           | The type of API to use (OpenAI, Azure, Fake, Empty) | Fake |
| `API_VERSION`        | The version of the API | None |
| `OPENAI_API_BASE`    | The base URL for the OpenAI API | None |
| `ALIAS`              | The alias for the model | None |
| `MODEL`              | The name of the model | None |
| `TEMPERATURE`        | The temperature setting for the AI model | 0.0 |
| `DATA_DIR`           | The directory where data will be stored | ".data" |
| `DISABLE_AUTH`       | Whether to disable user authentication | "False" |
| `DISBLE_USER_REG`     | Whether to disable user registration | "False" |

**Remarks, notes:**
- If `API_TYPE` is set to `Fake` all message will get a static reply, no call to API will be made. For demonstration purposes. If `Empty` is provided than no model is expected in the environment variables
- Providing  Azure/OpenAI model credentials (API key, deployment URL, etc.) via environment variables is not the only option. Users can also add their credentials in the Web UI, those creds will be encrypted and stored in `models.dat` file
- `DATA_DIR` - that's where all conversations and model settings will be saved. Each user will have a `$username` subfolder.
- `DISABLE_AUTH` - if set to [True], no login page will be shown, and all data will be stored under `$DATA_DIR/default_user`.

## Local User DB

`users.yaml` stored under `$DATA_DIR` keeps usernames and hashes that are used to authenticate and allow users in. Make changes to this file in the prod to make adjustments to who and how can access the app.

1. Generate Credentials:
- Run generate_pass.py.
  `python generate_pass.py --username <username> --password <password>`
- Input a username and password when prompted.
- Copy the output (username and hashed password).

2. Edit users.yaml:
- Open users.yaml.
- Add a new entry with the generated username and hashed password.

3. Save and Test:
- Save users.yaml.
- Restart the application.
- Log in with the new credentials to test.

## Running Locally

1. Set OpenAI API credentials as environment variables or within the `.env` file (refer to `.env.template` for an example).
2. Install requirements with `pip3 install -r requirements.txt`.
3. Run the application using `streamlit run chat.py`.
4. Alternatively, debug in VSCode by pressing F5 and selecting the "Debug" configuration.

## Running in Docker

Start Docker Desktop and run command in terminal, after teh cintainer is started you can access the app on localhost:8501

```
docker build -t py-chat-ui .
docker run -p 8501:8501 py-chat-ui
```

## Screenshots

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/4f318108-3fa6-4e3d-b416-d1bf1535c58c)

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/cca8095f-1bad-443e-a911-3c650d035b9c)

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/37f988e4-ea53-4642-b457-4c3ba619fb92)

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/8d242ffd-88b1-4d63-88d8-6e5a214cfbe9)

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/5e00aa12-a8ee-45e1-8493-e5a113a06e8c)

## Changelog
- 0.1.3 - lazy loading of chat sessions from files, refactored chat session UI, UI tweaks (removing empty space), OpenAI and Streamlit packages updated
