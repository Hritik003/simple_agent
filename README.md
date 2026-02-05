# MCP Streamable HTTP Client

A Python client for interacting with MCP (Model Context Protocol) servers using HTTP Streamable transport. This client integrates with OpenAI-compatible LLM APIs to process queries using tools provided by the MCP server.

## Features

- 🔌 Connect to MCP servers via HTTP Streamable transport
- 🤖 Integration with OpenAI-compatible LLM APIs
- 🛠️ Automatic tool discovery and execution
- 🔒 SSL verification disabled for self-signed certificates
- 💬 Interactive chat loop for continuous queries
- 🔐 Environment-based configuration for security

## Prerequisites

- Python 3.8 or higher
- Access to an MCP server with HTTP Streamable transport
- OpenAI-compatible API endpoint

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mcp_client
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example.json .env
```

Edit the `.env` file with your credentials:
```bash
# OpenAI/LLM Configuration
OPENAI_BASE_URL=https://your-api-endpoint.com/v1
OPENAI_API_KEY=your-api-key-here

# MCP Server Configuration
MCP_SERVER_URL=https://your-mcp-server.com/mcp/endpoint
MCP_AUTH_TOKEN=your-auth-token-here
```

## Usage

### Running the Client

Start the interactive chat client:

```bash
python mcp_client.py
```

### Interactive Mode

Once started, you can type queries and the client will:
1. Fetch available tools from the MCP server
2. Send your query to the LLM with tool definitions
3. Execute any tool calls requested by the LLM
4. Return the final response

Example session:
```
MCP Client Started!
Type your queries or 'quit' to exit.

Query: What tools are available?
[Response from LLM with available tools]

Query: quit
```

## Project Structure

```
mcp_client/
├── mcp_client.py       # Main client implementation
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (not in git)
├── .env.example.json  # Example environment configuration
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_BASE_URL` | Base URL for OpenAI-compatible API | Yes |
| `OPENAI_API_KEY` | API key for authentication | Yes |
| `MCP_SERVER_URL` | URL of the MCP server | Yes |
| `MCP_AUTH_TOKEN` | Bearer token for MCP server auth | Yes |

### SSL Configuration

The client is configured to disable SSL verification for self-signed certificates. This is useful for development environments but should be reviewed for production use.

## How It Works

1. **Connection**: The client establishes a connection to the MCP server using HTTP Streamable transport
2. **Tool Discovery**: Available tools are fetched from the MCP server
3. **Query Processing**: User queries are sent to the LLM along with tool definitions
4. **Tool Execution**: If the LLM requests tool calls, they are executed via the MCP server
5. **Response**: Final results are returned to the user

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   User      │─────▶│  MCP Client  │─────▶│  LLM API    │
│  (Console)  │      │              │      │  (OpenAI)   │
└─────────────┘      └──────┬───────┘      └─────────────┘
                            │
                            │ HTTP Streamable
                            ▼
                     ┌──────────────┐
                     │  MCP Server  │
                     │   (Tools)    │
                     └──────────────┘
```

## Dependencies

- `mcp` - Model Context Protocol client library
- `httpx` - Async HTTP client
- `openai` - OpenAI API client
- `python-dotenv` - Environment variable management
