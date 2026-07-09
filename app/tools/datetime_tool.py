# backend/app/tools/datetime_tool.py

from datetime import datetime
import pytz
from app.tools.base import BaseTool

class DateTimeTool:
    """Returns the current date and time."""
    name = "datetime"
    description = "Useful for getting the current date and time. Input can be a timezone (e.g., 'UTC', 'US/Eastern') or empty for local."

    async def run(self, input_data: str) -> str:
        try:
            tz_name = input_data.strip() if input_data.strip() else "UTC"
            tz = pytz.timezone(tz_name)
            now = datetime.now(tz)
            return now.strftime("%Y-%m-%d %H:%M:%S %Z")
        except Exception as e:
            return f"DateTime error: {str(e)}. Please use a valid timezone."