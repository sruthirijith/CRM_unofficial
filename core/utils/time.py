from datetime import datetime, timezone

import pytz


def utc_time() -> datetime:
    time = datetime.now()
    utc_time = time.astimezone(pytz.UTC)
    return utc_time


def ist_time() -> datetime:
    time = datetime.now()
    local = pytz.timezone("Asia/Kolkata")
    ist_time = local.localize(time, is_dst=True)
    return ist_time
