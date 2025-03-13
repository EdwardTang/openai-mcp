#!/usr/bin/env python3
# examples/mcp_client_example.py
"""Example script showing how to use an MCP client to connect to a Claude Code MCP server."""

import sys
import os
import time
import json
import argparse
import logging
from typing import Dict, Any

# Try to import the MCP client library 
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("Error: MCP client library not found. Please install it with:")
    print("pip install mcp")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp_client_example")


def main():
    """Run the MCP client example."""
    parser = argparse.ArgumentParser(description="MCP Client Example")
    parser.add_argument("--host", default="127.0.0.1", help="MCP server host")
    parser.add_argument("--port", type=int, default=8000, help="MCP server port")
    args = parser.parse_args()
    
    print(f"Connecting to MCP server at {args.host}:{args.port}...")
    
    try:
        # Connect to the MCP server
        connect_to_server(args.host, args.port)
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.exception(f"Error: {e}")
        return 1
    
    return 0


async def process_message(session: ClientSession):
    """Process MCP messages."""
    try:
        # Register client with server
        await session.execute_tool("RegisterClient", {"random_string": "example_client"})
        print("Connected to MCP server successfully!")
        
        # Get server configuration
        config = await session.execute_tool("GetConfiguration", {"format": "json"})
        print("\nServer Configuration:")
        print(json.dumps(json.loads(config), indent=2))
        
        # Get server metrics
        metrics = await session.execute_tool("GetServerMetrics", {"metric_type": "all"})
        print("\nServer Metrics:")
        print(metrics)
        
        # Example: View a file (if available)
        try:
            file_content = await session.execute_tool("View", {
                "params": {
                    "file_path": "/etc/hostname"
                }
            })
            print("\nFile content:")
            print(file_content)
        except Exception as e:
            print(f"Error viewing file: {e}")
        
        print("\nPress Ctrl+C to exit...")
        while True:
            # Keep session alive
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.exception(f"Error in process_message: {e}")


def connect_to_server(host: str, port: int):
    """Connect to the MCP server."""
    import asyncio
    import aiohttp
    
    async def run_client():
        """Run the MCP client."""
        url = f"http://{host}:{port}/sse"
        
        async with aiohttp.ClientSession() as http_session:
            async with http_session.get(url) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error(f"Failed to connect to MCP server: HTTP {resp.status} - {error_text}")
                    return
                
                # Create MCP client session
                session = ClientSession()
                
                # Process the SSE stream
                async for line in resp.content:
                    line = line.decode('utf-8').strip()
                    if not line or line.startswith(':'):
                        continue
                    
                    if line.startswith('data: '):
                        data = line[6:]
                        try:
                            message = json.loads(data)
                            await session.process_message(message)
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in SSE message: {data}")
                        except Exception as e:
                            logger.exception(f"Error processing message: {e}")
                
                logger.info("SSE stream ended")
    
    # Run the client
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_client())
    except KeyboardInterrupt:
        print("\nExiting client...")
    finally:
        loop.close()


if __name__ == "__main__":
    # Import asyncio here to avoid import errors on older Python versions
    import asyncio
    
    # Run the client
    sys.exit(main()) 