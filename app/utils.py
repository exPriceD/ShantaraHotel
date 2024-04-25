from datetime import datetime
import pytz


def get_current_time(timezone='Europe/Moscow'):
    moscow_tz = pytz.timezone(timezone)
    moscow_time = datetime.now(moscow_tz)
    formatted_time = moscow_time.strftime('%d.%m.%y %H:%M')
    return formatted_time