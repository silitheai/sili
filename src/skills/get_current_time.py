import datetime

def get_current_time(timezone_offset_hours: int = 0) -> str:
    """Returns the current date and time. 
    You can optionally provide an offset integer (e.g. -4 for EST, or +2 for CEST) to adjust the local time.
    """
    try:
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        
        if timezone_offset_hours != 0:
            offset = datetime.timedelta(hours=timezone_offset_hours)
            local_time = utc_now + offset
            return f"Time at GMT{timezone_offset_hours:+} is: {local_time.strftime('%Y-%m-%d %H:%M:%S')}"
            
        return f"Current UTC Time: {utc_now.strftime('%Y-%m-%d %H:%M:%S')}"
    except Exception as e:
        return f"Error fetching time: {str(e)}"
