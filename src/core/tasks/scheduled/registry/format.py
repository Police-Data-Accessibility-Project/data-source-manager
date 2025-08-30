from datetime import datetime

def format_job_datetime(dt: datetime) -> str:
    date_str: str = dt.strftime("%Y-%m-%d")
    format_24: str = dt.strftime("%H:%M:%S")
    format_12: str = dt.strftime("%I:%M:%S %p")
    return f"{date_str} {format_24} ({format_12})"