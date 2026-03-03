import os
from google.cloud import discoveryengine_v1 as discoveryengine
from dotenv import load_dotenv

load_dotenv()

project_id = os.getenv("GCP_PROJECT_ID")

def list_engines(location):
    client = discoveryengine.EngineServiceClient()
    parent = f"projects/{project_id}/locations/{location}"
    print(f"Listing engines in {parent}...")
    try:
        request = discoveryengine.ListEnginesRequest(parent=parent)
        page_result = client.list_engines(request=request)
        for response in page_result:
            print(response.name)
    except Exception as e:
        print(f"Error: {e}")

list_engines("global")
list_engines("us")
list_engines("us-central1")
