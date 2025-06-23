# worker.py

import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from workflows import GetAlertsWorkflow, GetForecastWorkflow, WaitForSignalWorkflow
from activities import make_nws_request


async def main():
    # Connect to Temporal server (change address if using Temporal Cloud)
    client = await Client.connect("localhost:7233")

    # Start worker with both workflows and activities
    worker = Worker(
        client,
        task_queue="weather-task-queue",
        workflows=[GetAlertsWorkflow, GetForecastWorkflow, WaitForSignalWorkflow],
        activities=[make_nws_request],  # Can register more activities here as needed
    )
    print("Worker started. Listening for workflows...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
