import os
import asyncio
from dotenv import load_dotenv
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions
from google.oauth2 import service_account

load_dotenv()
credentials_path = os.getenv("SERVICE_ACCOUNT_KEY_FILE")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
credentials = service_account.Credentials.from_service_account_file(credentials_path)

project_id = os.getenv("GCP_PROJECT_ID")
location = os.getenv("GCP_REGION", "global")
data_store_id = "77110326-4e07-4373-a1a3-3ca3296d7101"

print(f"Project: {project_id}, Location: {location}, Data Store: {data_store_id}")
print(f"Endpoint: {location}-discoveryengine.googleapis.com")

client_options = ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com") if location != "global" else None
client = discoveryengine.ConversationalSearchServiceClient(credentials=credentials, client_options=client_options)

parent = client.data_store_path(project=project_id, location=location, data_store=data_store_id)
print(f"Parent: {parent}")
try:
    conversation = client.create_conversation(
        parent=parent,
        conversation=discoveryengine.Conversation(),
    )
    print(conversation)
except Exception as e:
    import traceback
    traceback.print_exc()
