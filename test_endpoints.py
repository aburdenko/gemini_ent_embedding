import os
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions
from dotenv import load_dotenv
from google.oauth2 import service_account

load_dotenv()
credentials_path = os.getenv("SERVICE_ACCOUNT_KEY_FILE")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
credentials = service_account.Credentials.from_service_account_file(credentials_path)

project_id = os.getenv("GCP_PROJECT_ID")
data_store_id = "77110326-4e07-4373-a1a3-3ca3296d7101"

for loc in ["global", "us", "us-central1"]:
    print(f"Testing {loc}...")
    client_options = ClientOptions(api_endpoint=f"{loc}-discoveryengine.googleapis.com") if loc != "global" else None
    client = discoveryengine.ConversationalSearchServiceClient(credentials=credentials, client_options=client_options)
    
    parent = client.data_store_path(project=project_id, location=loc, data_store=data_store_id)
    try:
        conversation = client.create_conversation(
            parent=parent,
            conversation=discoveryengine.Conversation(),
        )
        print(f"Success on {loc}: {conversation.name}")
    except Exception as e:
        print(f"Failed on {loc}: {type(e).__name__} - {str(e)}")

