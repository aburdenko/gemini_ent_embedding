import os
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions
from google.oauth2 import service_account

credentials_path = "/home/user/service_account.json"
credentials = service_account.Credentials.from_service_account_file(credentials_path)

project_id = "kallogjeri-project-345114"

engines_to_test = [
    ("us", "nl2sql-dummy-ds"),
    ("global", "claims-data_1762979629917"),
    ("global", "aetna_1768232438709"),
    ("global", "medical-text-ds_1729173812143"),
    ("global", "goog_earnings_test")
]

for loc, ds in engines_to_test:
    print(f"Testing {ds} in {loc}...")
    try:
        client_options = ClientOptions(api_endpoint=f"{loc}-discoveryengine.googleapis.com") if loc != "global" else None
        client = discoveryengine.ConversationalSearchServiceClient(credentials=credentials, client_options=client_options)
        parent = client.data_store_path(project=project_id, location=loc, data_store=ds)
        
        conv = client.create_conversation(parent=parent, conversation=discoveryengine.Conversation())
        print(f"  Success! Conversation ID: {conv.name}")
    except Exception as e:
        print(f"  Failed: {type(e).__name__} - {str(e)}")

