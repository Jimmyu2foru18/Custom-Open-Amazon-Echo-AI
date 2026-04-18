# STEP 1: CLOUD AND API CONFIGURATION
* Obtain a Gemini 1.5 Flash API key. Flash is better for voice due to lower latency.
* Setup an Amazon Developer account and create a new Alexa Skill.
* Configure the Alexa Skill "Interaction Model" with a "ChatIntent" that accepts a "SearchQuery" slot.

# STEP 2: LOCAL ENVIRONMENT SETUP (4 GB VRAM STRATEGY)
* Install Ollama on your local machine.
* Download small models to stay within VRAM limits.
    - Run: ollama pull phi3:mini (approx. 2.3 GB)
    - Run: ollama pull llama3:8b-instruct-q2_K (approx. 3 GB)
* Set up OpenClaw as your agentic orchestrator. Point its "thinker" to the Gemini API for complex tasks.

# STEP 3: CREATING THE PUBLIC CONNECTOR
* Install Ngrok to make your local machine accessible to Amazon's servers.
* Run: ngrok http 5000 (or whichever port your Python backend uses).
* Copy the HTTPS URL from Ngrok and paste it into the "Endpoint" section of your Alexa Skill configuration.

# STEP 4: DEVELOPING THE BACKEND LOGIC
* Write a Python script using 'flask' and 'ask-sdk-core'.
* Program the script to receive the "SearchQuery" from Alexa.
* Forward the query to OpenClaw. 
* If the user asks for a search, OpenClaw calls the Search Tool and Gemini.
* If the user is just testing, route the call to the local Ollama endpoint (http://localhost:11434).

# STEP 5: VOICE AND AGENTIC INTEGRATION
* Configure OpenClaw tools to allow "Agentic Searches" via DuckDuckGo.
* Format the output as a clean string for Alexa's Text-to-Speech (TTS).
* Test the flow: Speak to your Echo, "Alexa, ask [Skill Name] what is the current temperature in New York."
* Verify the logs to see if OpenClaw chose the search tool or answered from its internal knowledge.
