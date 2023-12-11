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

## Evironment variables

You can configure the app either via setting environment variables or puttin values into `.env` file (see `.env.template` for an example).

| Environment Variable | Description | Default Value |
|----------------------|-------------|---------------|
| `OPENAI_API_KEY`     | The API key for OpenAI or Azure | None |
| `API_TYPE`           | The type of API to use (OpenAI or Azure) | None |
| `API_VERSION`        | The version of the API | None |
| `OPENAI_API_BASE`    | The base URL for the OpenAI API | None |
| `ALIAS`              | The alias for the model | None |
| `MODEL`              | The name of the model | None |
| `TEMPERATURE`        | The temperature setting for the AI model | 0.0 |
| `DATA_DIR`           | The directory where data will be stored | ".data" |
| `DISABLE_AUTH`       | Whether to disable user authentication | "False" |

**Remarks, notes:**
- Providing  Azure/OpenAI model credentials (API key, deployment URL, etc.) via environment variables is not the only option. Users can also add their credentials in the Web UI, those creds will be encrypted and stored in `models.dat` file
- `DATA_DIR` - that's where all conversations and model settings will be saved. Each user will have a `$username` subfolder.
- `DISABLE_AUTH` - if set to [True], no login page will be shown, and all data will be stored under `$DATA_DIR/default_user`.

## Set-up user creds

`users.yaml` storder under `$DATA_DIR` stores usernames and hashes that are used to authenticate and allow user in. Make changes to this file in prod to make adjustment to who and how can access the app.

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