import os
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions
from google.auth import default

credentials, project = default()
print(f"Default project: {project}")

def test_engines(project_id, loc):
    print(f"\nTesting {project_id} in {loc}...")
    try:
        client_options = ClientOptions(api_endpoint=f"{loc}-discoveryengine.googleapis.com") if loc != "global" else None
        client = discoveryengine.EngineServiceClient(credentials=credentials, client_options=client_options)
        parent = f"projects/{project_id}/locations/{loc}"
        
        request = discoveryengine.ListEnginesRequest(parent=parent)
        page_result = client.list_engines(request=request)
        for response in page_result:
            print(f"Engine Found: {response.name}")
            print(f"Data Store IDs: {response.data_store_ids}")
    except Exception as e:
        print(f"Failed: {type(e).__name__} - {str(e)}")

for proj in ["adk-api-client", "kallogjeri-project-345114"]:
    for loc in ["global", "us", "eu"]:
        test_engines(proj, loc)
