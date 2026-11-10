from datetime import datetime, date, timezone, timedelta
from zoneinfo import ZoneInfo

def socalDate(startend=None):
    socal_tz = ZoneInfo("America/Los_Angeles")
    today = datetime.now(socal_tz)

    if startend is None:
        return today.strftime("%Y-%m-%d")

    if startend == "start":
        socal_date = today.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    elif startend == "end":
        socal_date = today.replace(
            hour=23, minute=59, second=59, microsecond=999000
        )
    else:
        raise ValueError("Pick 'start' or 'end'")

print( socalDate() )