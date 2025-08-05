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
     # check if state is a valid US state
    states = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY' }

    if state in states:
        state_short = states[state]
        client = await get_temporal_client()
        handle = await client.start_workflow(
            "GetAlertsWorkflow",
            state_short,
            id=f"alerts-{state.lower()}",
            task_queue="weather-task-queue"
        )
    else:
        return "This tool only works for US states. Please provide a valid US state."
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
