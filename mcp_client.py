
"""MCP Streamable HTTP Client"""

import argparse
import asyncio
import json
import os
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
import httpx
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def create_insecure_httpx_client(**kwargs):
    """Create an httpx client with SSL verification disabled for self-signed certificates."""
    return httpx.AsyncClient(verify=False, **kwargs)

class MCPClient:
    """MCP Client for interacting with an MCP Streamable HTTP server"""

    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self._session_context = None
        self._streams_context = None
        http_client = httpx.Client(verify=False)
        self.openai = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY"),
            http_client=http_client
        )

    async def connect_to_streamable_http_server(
        self, server_url: str, headers: Optional[dict] = None
    ):
        """Connect to an MCP server running with HTTP Streamable transport"""
        print(f"Connecting to MCP server at: {server_url}")
        print(f"Using headers: {headers}")
        
        self._streams_context = streamablehttp_client(  
            url=server_url,
            headers=headers or {},
            httpx_client_factory=create_insecure_httpx_client,
            timeout=60.0  
        )
        read_stream, write_stream, _ = await self._streams_context.__aenter__()  
        print("Streams established successfully")

        self._session_context = ClientSession(read_stream, write_stream) 
        self.session: ClientSession = await self._session_context.__aenter__() 
        print("Session context created")

        print("Initializing session...")
        await self.session.initialize()
        print("Session initialized successfully!")

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        messages = [{"role": "user", "content": query,"tool_choice": "auto"}]

        response = await self.session.list_tools()
        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                }
            }
            for tool in response.tools
        ]

        response = self.openai.chat.completions.create(
            model="gpt-oss-20b",
            max_tokens=1000,
            messages=messages,
            tools=available_tools,
        )

        final_text = []
        message = response.choices[0].message

        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)  # Parse JSON string to dict

                result = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                messages.append({"role": "assistant", "content": message.content or ""})
                messages.append({"role": "user", "content": str(result.content)})

                response = self.openai.chat.completions.create(
                    model="test",
                    max_tokens=1000,
                    messages=messages,
                )

                final_text.append(response.choices[0].message.content)
        else:
            final_text.append(message.content)

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                import traceback
                print(f"\nError: {str(e)}")
                print(f"Error type: {type(e).__name__}")
                traceback.print_exc()

    async def cleanup(self):
        """Properly clean up the session and streams"""
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:  
            await self._streams_context.__aexit__(None, None, None)  
        await self.exit_stack.aclose()


async def main():
    """Main function to run the MCP client"""
    parser = argparse.ArgumentParser(description="Run MCP Streamable http based Client")
    client = MCPClient()

    try:
        await client.connect_to_streamable_http_server(
            server_url=os.getenv("MCP_SERVER_URL"),
            headers={
                "Authorization": f"Bearer {os.getenv('MCP_AUTH_TOKEN')}"
            }
        )
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())