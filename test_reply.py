import os
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions
from google.oauth2 import service_account

credentials_path = "/home/user/service_account.json"
credentials = service_account.Credentials.from_service_account_file(credentials_path)

client = discoveryengine.ConversationalSearchServiceClient(credentials=credentials)
parent = client.data_store_path(project="kallogjeri-project-345114", location="global", data_store="claims-data_1762979629917")

conv = client.create_conversation(parent=parent, conversation=discoveryengine.Conversation())
search_request = discoveryengine.ConverseConversationRequest(
    name=conv.name,
    query=discoveryengine.TextInput(input="Hello"),
    serving_config=client.serving_config_path(
        project="kallogjeri-project-345114", location="global", data_store="claims-data_1762979629917", serving_config="default_config"
    )
)
resp = client.converse_conversation(search_request)
print("Response keys:", dir(resp.reply))
print("Reply text:", getattr(resp.reply, 'summary', None))
