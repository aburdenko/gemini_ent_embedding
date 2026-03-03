import os
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions
from google.oauth2 import service_account

credentials_path = "/home/user/service_account.json"
credentials = service_account.Credentials.from_service_account_file(credentials_path)

project_id = "kallogjeri-project-345114"
location = "us"
data_store_id = "nl2sql-dummy-ds"

client_options = ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
client = discoveryengine.ConversationalSearchServiceClient(credentials=credentials, client_options=client_options)

parent = client.data_store_path(project=project_id, location=location, data_store=data_store_id)
print(f"Parent: {parent}")

try:
    conversation = client.create_conversation(
        parent=parent,
        conversation=discoveryengine.Conversation(),
    )
    print(f"Conversation created: {conversation.name}")
except Exception as e:
    import traceback
    traceback.print_exc()
