import os
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
from pydantic import BaseModel
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions
from google.oauth2 import service_account

# Load environment variables
load_dotenv(override=True)

app = FastAPI(title="Gemini Enterprise Custom Embed")

# Allow iframe embedding and cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Ensure X-Frame-Options allows embedding
    if "X-Frame-Options" in response.headers:
        del response.headers["X-Frame-Options"]
    return response

# Setup credentials
credentials_path = os.getenv("SERVICE_ACCOUNT_KEY_FILE")
if credentials_path and os.path.exists(credentials_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
else:
    credentials = None

project_id = os.getenv("GCP_PROJECT_ID")
# Default to 'global' if not specified for Discovery Engine
location = os.getenv("GCP_REGION", "global")
# Extract data store ID from the URL provided previously or set in env
data_store_id = os.getenv("GEMINI_DATA_STORE_ID", "77110326-4e07-4373-a1a3-3ca3296d7101")

# Configure client
# For regional endpoints, we need to pass client_options
client_options = (
    ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
    if location != "global"
    else None
)
client = discoveryengine.ConversationalSearchServiceClient(
    credentials=credentials, client_options=client_options
)

class ChatRequest(BaseModel):
    query: str
    conversation_id: str | None = None

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # 1. Determine or Create the Conversation
        if request.conversation_id:
            conversation_name = client.conversation_path(
                project=project_id,
                location=location,
                data_store=data_store_id,
                conversation=request.conversation_id,
            )
        else:
            conversation = client.create_conversation(
                parent=client.data_store_path(
                    project=project_id, location=location, data_store=data_store_id
                ),
                conversation=discoveryengine.Conversation(),
            )
            conversation_name = conversation.name

        # 2. Converse (Send query to Gemini Enterprise)
        search_request = discoveryengine.ConverseConversationRequest(
            name=conversation_name,
            query=discoveryengine.TextInput(input=request.query),
            serving_config=client.serving_config_path(
                project=project_id,
                location=location,
                data_store=data_store_id,
                serving_config="default_config",
            ),
        )
        response = client.converse_conversation(search_request)

        # 3. Extract ID and Response text
        conv_id = response.conversation.name.split("/")[-1]
        
        reply_text = "I'm sorry, I couldn't generate a response."
        if response.reply and response.reply.summary and response.reply.summary.summary_text:
            reply_text = response.reply.summary.summary_text

        return JSONResponse({
            "reply": reply_text,
            "conversation_id": conv_id
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/", response_class=HTMLResponse)
async def get_embedded_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gemini Enterprise - Custom Embed</title>
        <style>
            body { font-family: sans-serif; margin: 0; padding: 0; background-color: transparent; display: flex; flex-direction: column; height: 100vh; }
            .chat-container { flex-grow: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
            .message { max-width: 80%; padding: 10px 15px; border-radius: 20px; font-size: 15px; line-height: 1.4; }
            .user-msg { align-self: flex-end; background-color: #1a73e8; color: white; border-bottom-right-radius: 4px; }
            .bot-msg { align-self: flex-start; background-color: white; border: 1px solid #ddd; color: #333; border-bottom-left-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
            .input-area { display: flex; padding: 15px; background: white; border-top: 1px solid #ddd; }
            #query-input { flex-grow: 1; padding: 12px 15px; border: 1px solid #ccc; border-radius: 20px; outline: none; font-size: 15px; }
            #send-btn { margin-left: 10px; padding: 10px 20px; border: none; background-color: #1a73e8; color: white; border-radius: 20px; cursor: pointer; font-size: 15px; font-weight: bold; }
            #send-btn:hover { background-color: #1557b0; }
            .loading { align-self: flex-start; color: #666; font-size: 13px; font-style: italic; display: none; padding-left: 10px; }
        </style>
    </head>
    <body>
        <div class="chat-container" id="chat-container">
            <div class="message bot-msg">Hello! I am your custom embedded Gemini Enterprise agent. How can I help you today?</div>
            <div class="loading" id="loading">Agent is typing...</div>
        </div>
        <div class="input-area">
            <input type="text" id="query-input" placeholder="Ask a question about your data..." autocomplete="off">
            <button id="send-btn">Send</button>
        </div>

        <script>
            let currentConversationId = null;
            const chatContainer = document.getElementById('chat-container');
            const queryInput = document.getElementById('query-input');
            const sendBtn = document.getElementById('send-btn');
            const loading = document.getElementById('loading');

            function appendMessage(text, isUser) {
                const msgDiv = document.createElement('div');
                msgDiv.className = `message ${isUser ? 'user-msg' : 'bot-msg'}`;
                
                // Simple markdown/linebreak formatting for bot messages
                if (!isUser) {
                    msgDiv.innerHTML = text.replace(/\\n/g, '<br>');
                } else {
                    msgDiv.textContent = text;
                }
                
                chatContainer.insertBefore(msgDiv, loading);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            async function sendMessage() {
                const query = queryInput.value.trim();
                if (!query) return;

                appendMessage(query, true);
                queryInput.value = '';
                loading.style.display = 'block';
                chatContainer.scrollTop = chatContainer.scrollHeight;

                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            query: query, 
                            conversation_id: currentConversationId 
                        })
                    });

                    const data = await response.json();
                    loading.style.display = 'none';

                    if (response.ok) {
                        appendMessage(data.reply, false);
                        currentConversationId = data.conversation_id;
                    } else {
                        appendMessage('Error: ' + data.error, false);
                    }
                } catch (err) {
                    loading.style.display = 'none';
                    appendMessage('Error communicating with backend.', false);
                }
            }

            sendBtn.addEventListener('click', sendMessage);
            queryInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
