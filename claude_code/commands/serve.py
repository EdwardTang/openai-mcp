#!/usr/bin/env python3
# claude_code/commands/serve.py
"""Command to start the MCP server."""

import os
import sys
import logging
import argparse
from typing import Dict, Any, Optional, List
import subprocess
import pathlib

from claude_code.mcp_server import initialize_server, mcp

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add command-specific arguments to the parser.
    
    Args:
        parser: Argument parser
    """
    parser.add_argument(
        "--dev", 
        action="store_true", 
        help="Run in development mode with the MCP Inspector"
    )
    
    parser.add_argument(
        "--host", 
        type=str, 
        default="localhost", 
        help="Host to bind the server to"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to bind the server to"
    )
    
    parser.add_argument(
        "--dependencies", 
        type=str, 
        nargs="*", 
        help="Additional dependencies to install"
    )
    
    parser.add_argument(
        "--env-file", 
        type=str, 
        help="Path to environment file (.env)"
    )


def execute(args: argparse.Namespace) -> int:
    """Execute the serve command.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code
    """
    host = args.host
    port = args.port
    logger.info(f"Starting MCP server on {host}:{port}")
    logger.info(f"Visit http://{host}:{port} for Claude Desktop configuration instructions")

    # Add project root to Python path
    project_root = str(pathlib.Path(__file__).parent.parent.parent.absolute())
    sys.path.insert(0, project_root)
    
    # Load environment variables from file
    if args.env_file:
        if not os.path.exists(args.env_file):
            logger.error(f"Environment file not found: {args.env_file}")
            return 1
            
        import dotenv
        dotenv.load_dotenv(args.env_file)
    
    # Initialize the MCP server
    server = initialize_server()
    
    # Add any additional dependencies
    if args.dependencies:
        for dep in args.dependencies:
            server.dependencies.append(dep)
    
    # Override the run_sse_async method to add a custom root route
    async def custom_run_sse_async():
        """Run the server using SSE transport with a custom root route."""
        from starlette.applications import Starlette
        from starlette.routing import Route, Mount
        from starlette.responses import FileResponse, RedirectResponse, HTMLResponse
        from starlette.staticfiles import StaticFiles
        
        from mcp.server.sse import SseServerTransport

        sse = SseServerTransport("/messages")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await mcp._mcp_server.run(
                    streams[0],
                    streams[1],
                    mcp._mcp_server.create_initialization_options(),
                )

        async def handle_messages(request):
            await sse.handle_post_message(request.scope, request.receive, request._send)
            
        async def handle_root(request):
            """Handle requests to the root path."""
            # Try to serve the homepage HTML file if it exists
            homepage_path = pathlib.Path(__file__).parent.parent / "examples" / "claude_mcp_config.html"
            if homepage_path.exists():
                return FileResponse(str(homepage_path))
            else:
                # Return a simple HTML page
                return HTMLResponse("""
                <html>
                    <head>
                        <title>Claude Code MCP Server</title>
                        <style>
                            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                            h1 { color: #6F4E37; }
                            .container { background-color: #f8f9fa; border-radius: 5px; padding: 20px; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>Claude Code MCP Server</h1>
                            <p>The Model Context Protocol server is running.</p>
                            <p>To connect Claude Desktop to this MCP server, follow these instructions:</p>
                            <ol>
                                <li>Open Claude Desktop and go to Settings</li>
                                <li>Navigate to "Model Context Protocol" section</li>
                                <li>Click "Add New Server"</li>
                                <li>Use the following settings:
                                    <ul>
                                        <li>Name: Claude Code Tools</li>
                                        <li>Type: Local Process</li>
                                        <li>Command: python</li>
                                        <li>Arguments: claude.py serve</li>
                                    </ul>
                                </li>
                                <li>Click Save and connect to the server</li>
                            </ol>
                            <p>Server status: <span style="color: green; font-weight: bold;">Running</span></p>
                        </div>
                    </body>
                </html>
                """)

        starlette_app = Starlette(
            debug=mcp.settings.debug,
            routes=[
                Route("/", endpoint=handle_root),
                Route("/sse", endpoint=handle_sse),
                Route("/messages", endpoint=handle_messages, methods=["POST"]),
            ],
        )

        import uvicorn
        config = uvicorn.Config(
            starlette_app,
            host=mcp.settings.host,
            port=mcp.settings.port,
            reload=False,
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    # Set host and port in settings
    mcp.settings.host = host
    mcp.settings.port = port
    
    # Run the server directly using the custom run method
    try:
        # Override the run_sse_async method
        mcp.run_sse_async = custom_run_sse_async
        
        # Run with SSE transport for web server
        mcp.run(transport="sse")
        return 0
    except Exception as e:
        logger.error(f"Error running MCP server: {e}")
        raise


def main() -> int:
    """Run the serve command as a standalone script."""
    parser = argparse.ArgumentParser(description="Run the Claude Code MCP server")
    add_arguments(parser)
    args = parser.parse_args()
    return execute(args)


if __name__ == "__main__":
    sys.exit(main())