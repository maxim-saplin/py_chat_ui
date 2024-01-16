# Publishing to Azure Container Apps

Here's a detailed breakdown of publishing `py_chat_ui` web app using serverless hosting in Microsoft Cloud. In order to proceed you would need an active Azure Subscription, e.g.:
- Profession/Premium MSDN package with $50/$150 monthly credit
- Pay-as-you go
- Any other paid plan

We will create:
1. `Azure Container App` service to run `py_chat_ui` docker container and expose web UI to the internet
2. `Storage Account` with SMB file share to persist `py_chat_ui` files with user creds (hashed) and dialogs

This set-up will cost **~$14 per month** (Jan 2024, East US 2, 0.5 CPU, 1Gi MEM).

## Creating Container Apps Service

### 1. In Azure portal start creating service and tpye 'Container App'

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/6534c0cc-fa62-47de-b11b-301f46b14109)

In the above screenshot I have created `chat` resource group first and requested a new service from within this group. It is recomended to keep your Container App (+ related auto created resources) and Storage Account (next chapter) in a single resource group for convinience.


### 2. Fill-in basic Container App attributes

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/3eddabfe-4956-451f-8c74-7c85a0e48d8b)

Type in resource name (e.g. 'py-chat-ui'), choose correct resource group (e.g. already created 'chat'), select region (prices can vary in different regions).

### 3. Configure Docker container to use

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/9542bd5e-c122-4f4b-ad41-bf40ec3d85f1)

Choose 'ghcr.io' (GitHub Container registry) and 'ghcr.io/maxim-saplin/py_chat_ui:latest' container image (the one published at this repo).

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

When you open the newly created Container App service at the `Overview` tab you will see the public URL (top right of the page). You can click the link and go to the login screen.

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/7aef489c-9fbe-4487-acbc-6690b01a590e)

If no ENV vars have been set you will get `Register a new user` link available, go there and create a new user. Later use the creds to access the app.

You can also disable user authentication (anonimous access without login page) OR user registration via [ENV variables](https://github.com/maxim-saplin/py_chat_ui#evironment-variables). If authentication is disabled you can configure Azure to disallow anonymous access and use a valid Microsoft account to access web app via URL (using Azure AD).

## Configure storage account, store backend files on Azure File Share

Container can be reloaded any time, all data stored in local folder will be lost. If you set minimum number of replicas to be 0 when creating Container App you can expect the container to be released in a few hours after inactivity. You can set the minimal replicas to be at least 1 - this can give the container a few days before it will be restarted.

In order to ensure that whatever data is stored by the backend is persisted an external volume must be created. We will use Azure Storage Account and createa an SMB folder and point the container to use this path as a location to store its' data files.

!!! As long as you don't care about persistance of your dialogs and user registration you can skip this part nad proceed using single container which writes to ephemeral storage.

### 1. Create storage account

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/c7827056-20c4-48d5-ac11-d4151e86bd87)

At the top of Azure Portal type "Storage account" and go to the list of accounts. Create a new storage account (OR pick an existing one).

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/8023b6f4-f8dd-4b5c-9ba7-b8132c070cf7)

### 2. Create a new `File Share` under the storage account.

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/78571a6a-0123-46ee-908e-ed0190ce0fc8)

5 TiB is the minimal file share size, you will actually pay for the storage used, expect hunderds of killobytes and up to few megabytes of data would be required for a typical single user chat history.

### 3. Add the file share to container's managed environment

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/bc24e937-ea83-4273-869e-c44061485c23)

At first you need to copy the access key to the sotrage account where the file share has been created.

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/115eb009-e911-499e-8497-d3374f191774)

Next you need to go managed environment of the container app. It is created along with container app, you can navigate to the correspinding page from Container App's overview page. Over there you add the newly created file share and use the access key for the storage account where the file share was created. Make sure to pick 'Read/Write' access mode.

### 4. Create a new revision of the Container App, add File Share

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/60f95d2f-72ea-44cc-91da-9325d8d95b8a)

Open Container App service, go to 'Revisions' tab and create a new revision.

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/ff76d9b4-06ca-4d93-a00c-70edf14b6a07)

Click the existing container and edit it. In the side bar make sure that use define 'DATA_DIR' to point to a volume which will be our file share mount. E.g. '/chatdata'

![image](https://github.com/maxim-saplin/py_chat_ui/assets/7947027/24f6a06b-5efa-497d-b4cf-1bce75881048)

At the 'Volumes' tab you should be able to add the file share and point it to '/chatdata' mount point in the container.

Complete the configuration by creating this new revision and deleting the old revision. You should be good to access the app now with data persisted in file share.

You can access the file share and view/edit the files. E.g. you might want to disable user registration and manage users via [manually updating `users.yaml` file](https://github.com/maxim-saplin/py_chat_ui/tree/main#local-user-db)



 




