# client_example.py — Minimal MCP host for CertTrack-MCP (STDIO)
# Requirements: pip install mcp
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Launch the CertTrack-MCP server module via STDIO
    params = StdioServerParameters(
        command="python",
        args=["-m", "certtrack_mcp.server"],
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            # Handshake
            await session.initialize()

            # 1) Discover tools
            tools = await session.list_tools()
            print("Tools:", [t.name for t in tools.tools])

            # 2) Example: list_my_certs
            try:
                res = await session.call_tool(
                    "list_my_certs",
                    arguments={"nombre": "Laura Lopez"}  # change as needed
                )
                print("\n[list_my_certs] Result:")
                print(res)
            except Exception as e:
                print("Error calling list_my_certs:", e)

            # 3) Example: alerts_schedule_due (next 30 days)
            try:
                res = await session.call_tool(
                    "alerts_schedule_due",
                    arguments={"days": 30}
                )
                print("\n[alerts_schedule_due] Result:")
                print(res)
            except Exception as e:
                print("Error calling alerts_schedule_due:", e)

if __name__ == "__main__":
    asyncio.run(main())
