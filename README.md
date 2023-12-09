
## .env

Azure/OpenAI model creds (API key, deployment URL etc.) can be provided here. If non provided users can always add their creds in the web UI.

`DATA_DIR=".data"` - that is where all conversation, model settions vill be saved, each user will have $username subfolder
`DISABLE_AUTH="False"` - if True, no login page wil be shown, all data will be under '$DATA_DIR/default_user'

## Running localy

1. Set OpenAI API creds as ENV variables or within .env file (check sample at `.env.template`)

2. Install requirements `pip3 install -r requirements.txt`  

3. Run it `streamlit run chat.py`

4. Or debug in VSCode via F5 and "Debug" confog