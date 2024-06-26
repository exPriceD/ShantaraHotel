from datetime import datetime
import pytz
import requests


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


def send_notification(message):
    bot_token = "7075215827:AAH00pYLrJfuolLP46WnWIln3TwcvNDUA7s"
    method = "sendMessage"
    url = f"https://api.telegram.org/bot{bot_token}/{method}"

    chat_id = 903755276
    tg_data = {"chat_id": chat_id, "text": message}
    requests.post(url, data=tg_data)

    #chat_id = 281126819
    #tg_data = {"chat_id": chat_id, "text": message}
    #requests.post(url, data=tg_data)

