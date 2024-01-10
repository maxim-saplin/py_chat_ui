# Publishing to Azure Container Apps

Here's a detailed breakdown of publishing the UI using serverless hosting Microsoft Cloud. In order to proceed you would need an active Azure Subscription, e.g.:
- Profession/Premium MSDN package with $50/150 monthly credit
- Pay-as-you go
- Any other paid plan

We will create:
1. `Azure Container App` service to run `py_chat_ui` docker container and expose web UI
2. `Storage Account` with SMB file share to persist `py_chat_ui` files with user creds (hashed) and their dialogs

This set-up will cost **~$14 per month** (Jan 2024, East US 2, 0.5 CPU, 1Gi MEM).

## Creating Container Apps Service

### 1. Go to service creatin and type 'Container App'

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/6534c0cc-fa62-47de-b11b-301f46b14109)

In the above screenshot I have created `chat` resource group first and requested a new service from within this group. It is recomended to keep your Container App (+ related auto created resources) and Storage Account (next chapter) in a single resource group for convinience


### 2. Fill in basic Container App attributes

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/3eddabfe-4956-451f-8c74-7c85a0e48d8b)

Type in resource name (e.g. 'py-chat-ui'), choose correct resource group (e.g. already created 'chat'), region (there can be different pricies in different regions)

### 3. Configure Docker container to use

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/9542bd5e-c122-4f4b-ad41-bf40ec3d85f1)

Choose 'ghcr.io' (GitHub Container registry) and 'ghcr.io/maxim-saplin/py_chat_ui:latest' container image (the one published at this repo)

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/584f359d-3ad2-4f4c-9e43-d5310b50a716)

Choose runtime/reosurce allocation for the container. The minimal 0.25CPU and 0.5Gi MEM is enough to run the app.

#### 3.1 [OPTIONAL] Configure the app using ENV variables

At this step you can define environment variables controlling the behaviour of the app, such as disabling authentucation OR setting OpenAI/Azure endpoints for GPT 3.5/4 API. You can leave this configs as-is. By defualt the app has a registration screen allowing anybody to register, the model creds can be defined via the UI (API key etc.). You can also change this settings latter at Container App screen creating a new Revision (left side menu).

[Full list of ENV configs is here](https://github.com/maxim-saplin/py_chat_ui#evironment-variables)


### 4. Expose container app to the Internet

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/9588d959-93e6-413e-bc60-745c0af8a0ec)

Make sure ingress is enabled, keep settings as in the above screenshot.

### 5. Complete service creation

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/4aefce93-ae50-430b-a272-54481aa227dd)

## Access the app over the internet

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/d3333ec4-dce6-4c8a-9f8f-5e4c5172f988)

When you open the newly created Conter App service at the `Overview` tab on the top right you will see the public URL. You can click the link and go to the login screen.

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/7aef489c-9fbe-4487-acbc-6690b01a590e)

If no ENV vars have been set you will get `Register a new user` link available, go there and create a new user. Use the creds to access the app.

You can also disable user authentication OR user registration via [ENV variables](https://github.com/maxim-saplin/py_chat_ui#evironment-variables). If authentication is disabled you can configure Azure to disallow anonymous access and use a valid Microsoft account to access web app via URL (via Azure AD).

## Configure storage account, store backend files on Azure SMB



