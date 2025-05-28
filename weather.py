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


@mcp.tool()
async def start_waiting_workflow(workflow_id: str, message: str) -> str:
    """Start a workflow that will wait for a completion signal."""
    client = await get_temporal_client()
    await client.start_workflow(
        workflow="WaitForSignalWorkflow",
        args=[message],
        id=workflow_id,
        task_queue="weather-task-queue",
    )
    return f"Workflow {workflow_id} started"


@mcp.tool()
async def send_signal(workflow_id: str, value: str) -> str:
    """Send the completion signal to a running workflow."""
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id)
    await handle.signal("complete", value)
    return f"Signal sent to {workflow_id}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
