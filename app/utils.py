from datetime import datetime
import pytz


def get_current_date(timezone='Europe/Moscow', return_time=True):
    moscow_tz = pytz.timezone(timezone)
    moscow_time = datetime.now(moscow_tz)
    if return_time:
        return moscow_time.strftime('%d.%m.%Y %H:%M')
    return moscow_time.strftime('%d.%m.%Y')


def format_date(date_obj):
    # date_obj = datetime.strptime(date_str, '%d.%m.%y')
    formatted_date = date_obj.strftime('20%y-%m-%dT00:00:00')

    return formatted_date
