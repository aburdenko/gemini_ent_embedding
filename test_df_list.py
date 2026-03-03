from google.cloud import dialogflowcx_v3 as dialogflow
from google.auth import default

credentials, project = default()
print(f"Default project: {project}")

def list_agents(project_id, location):
    print(f"\nListing Dialogflow CX Agents in {project_id} ({location}):")
    client_options = {"api_endpoint": f"{location}-dialogflow.googleapis.com"}
    client = dialogflow.AgentsClient(credentials=credentials, client_options=client_options)
    parent = f"projects/{project_id}/locations/{location}"
    try:
        request = dialogflow.ListAgentsRequest(parent=parent)
        for agent in client.list_agents(request=request):
            print(f"Agent: {agent.display_name}, Name: {agent.name}")
    except Exception as e:
        print(f"Failed: {e}")

list_agents("kallogjeri-project-345114", "us-central1")
list_agents("kallogjeri-project-345114", "global")
