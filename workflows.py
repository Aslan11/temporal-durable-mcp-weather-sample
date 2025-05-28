# workflows.py

from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

retry_policy = RetryPolicy(
    maximum_attempts=0,  # Infinite retries
    initial_interval=timedelta(seconds=2),
    maximum_interval=timedelta(minutes=1),
    backoff_coefficient=2.0,
)


NWS_API_BASE = "https://api.weather.gov"

def format_alert(feature: dict) -> str:
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

@workflow.defn
class GetAlertsWorkflow:
    @workflow.run
    async def run(self, state: str) -> str:
        url = f"{NWS_API_BASE}/alerts/active/area/{state}"
        data = await workflow.execute_activity(
            "make_nws_request",  # Name of the registered activity
            url,
            schedule_to_close_timeout=timedelta(seconds=40),
            retry_policy=retry_policy,  # Customize as needed
        )
        
        if not data or "features" not in data:
            return "Unable to fetch alerts or no alerts found."
        if not data["features"]:
            return "No active alerts for this state."
        alerts = [format_alert(feature) for feature in data["features"]]
        return "\n---\n".join(alerts)

@workflow.defn
class GetForecastWorkflow:
    @workflow.run
    async def run(self, latitude: float, longitude: float) -> str:
        points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
        points_data = await workflow.execute_activity(
            "make_nws_request",
            points_url,
            schedule_to_close_timeout=timedelta(seconds=40),
            retry_policy=retry_policy,
        )
        if not points_data:
            return "Unable to fetch forecast data for this location."

        forecast_url = points_data["properties"]["forecast"]
        forecast_data = await workflow.execute_activity(
            "make_nws_request",
            forecast_url,
            schedule_to_close_timeout=timedelta(seconds=40),
            # Use the same retry policy as other network calls
            retry_policy=retry_policy,
        )
        if not forecast_data:
            return "Unable to fetch detailed forecast."

        periods = forecast_data["properties"]["periods"]
        forecasts = []
        for period in periods[:5]:  # Only show next 5 periods
            forecast = f"""
                {period['name']}:
                    Temperature: {period['temperature']}°{period['temperatureUnit']}
                    Wind: {period['windSpeed']} {period['windDirection']}
                    Forecast: {period['detailedForecast']}
                    """
            forecasts.append(forecast)
        return "\n---\n".join(forecasts)
