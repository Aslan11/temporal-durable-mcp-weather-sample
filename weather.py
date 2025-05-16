# fastmcp_server.py

from temporalio.client import Client
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

# Temporal client setup (do this once, then reuse)
temporal_client = None

async def get_temporal_client():
    global temporal_client
    if not temporal_client:
        temporal_client = await Client.connect("localhost:7233")
    return temporal_client

@mcp.tool()
async def get_alerts(state: str) -> str:
    client = await get_temporal_client()
    handle = await client.start_workflow(
        "GetAlertsWorkflow",
        state,
        id=f"alerts-{state.lower()}",
        task_queue="weather-task-queue"
    )
    return await handle.result()

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    client = await get_temporal_client()
    handle = await client.start_workflow(
        workflow="GetForecastWorkflow",
        args=[latitude, longitude],
        id=f"forecast-{latitude}-{longitude}",
        task_queue="weather-task-queue",
    )

    return await handle.result()

if __name__ == "__main__":
    mcp.run(transport='stdio')
