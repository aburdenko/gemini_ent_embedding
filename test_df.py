import os
from google.cloud import dialogflowcx_v3 as dialogflow
from dotenv import load_dotenv
from google.oauth2 import service_account

load_dotenv()
credentials_path = os.getenv("SERVICE_ACCOUNT_KEY_FILE")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
credentials = service_account.Credentials.from_service_account_file(credentials_path)

project_id = os.getenv("GCP_PROJECT_ID")
agent_id = "77110326-4e07-4373-a1a3-3ca3296d7101"
location = "us-central1"

print(f"Testing Dialogflow CX Agent: {agent_id}")
client_options = {"api_endpoint": f"{location}-dialogflow.googleapis.com"}
client = dialogflow.AgentsClient(credentials=credentials, client_options=client_options)

name = f"projects/{project_id}/locations/{location}/agents/{agent_id}"
try:
    agent = client.get_agent(name=name)
    print(f"Success! Agent name: {agent.display_name}")
except Exception as e:
    print(f"Failed: {type(e).__name__} - {str(e)}")
