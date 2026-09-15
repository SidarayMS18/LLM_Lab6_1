# Lab6 - Personal Assistant with MCP Memory

A personal assistant chatbot with persistent memory using the Model Context Protocol (MCP).

## Features

- **Persistent Memory**: Save and retrieve notes using MCP tools
- **Natural Language Interface**: Chat with an AI assistant powered by Groq
- **CRUD Operations**: Create, read, update, and delete notes
- **Tag-based Organization**: Categorize notes with tags for easy searching

## Setup Instructions

### 1. Install Dependencies

```bash
cd lab6
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and add your Groq API key:

```bash
cp .env.example .env
```

Then edit `lab6/.env` and paste your Groq API key:

```
GROQ_API_KEY=gsk_your_actual_key_here
```

**Get your Groq API key**: Visit [console.groq.com/keys](https://console.groq.com/keys)

### 3. Run the Client

```bash
python client.py
```

## Usage

Once running, you can:

- **Save information**: "Remember that my project deadline is Friday"
- **Retrieve information**: "What's my project deadline?"
- **List notes**: "Show me all my notes"
- **Update notes**: "Update my deadline to next Monday"
- **Delete notes**: "Delete the note about the deadline"

Type `quit` or `exit` to stop the client.

## Optional Configuration

You can override the default LLM model by setting `LLM_MODEL` in your `.env` file:

```
LLM_MODEL=llama-3.3-70b-versatile
```

Default model: `openai/gpt-oss-120b`

## Project Structure

- `client.py` - MCP client that connects to the server and handles chat
- `server.py` - MCP server exposing memory CRUD tools
- `notes.json` - Local storage for persistent notes (auto-created)
- `.env` - Your API keys (not tracked in git)
- `.env.example` - Template for environment variables

## Important for Distribution

**Note**: When downloading this project as a ZIP, the `.env` file is not included (it's in `.gitignore`). After downloading:

1. Run `cp lab6/.env.example lab6/.env`
2. Edit `lab6/.env` and paste your Groq API key
3. The client will automatically pick it up

## Architecture

The project uses the Model Context Protocol (MCP) to give the LLM persistent memory:

1. **Server** (`server.py`): Exposes memory tools via MCP (save_note, search_notes, list_notes, update_note, delete_note)
2. **Client** (`client.py`): Connects to the server over stdio, discovers available tools, and lets the user chat with an LLM that can call those tools
3. **Storage**: Notes are stored locally in `notes.json`

The client uses Groq's API for LLM inference with function calling support.
