import re
import pandas as pd
from datetime import datetime


def preprocess(data):
    # Match pattern like: [26/08/24, 2:15:27 PM]
    pattern = r'\[(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}:\d{2})\s?\u202f?([APMapm]{2})\]'

    matches = re.findall(pattern, data)
    messages = re.split(r'\[\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}:\d{2}\s?\u202f?[APMapm]{2}\]', data)[1:]

    if len(matches) != len(messages):
        print("Mismatch between dates and messages. Parsing failed.")
        return pd.DataFrame()  # Return empty to avoid crashing Streamlit

    datetimes = []
    for (date, time, meridiem) in matches:
        dt_string = f"{date}, {time} {meridiem}"
        try:
            dt_obj = datetime.strptime(dt_string, "%d/%m/%y, %I:%M:%S %p")
            formatted = dt_obj.strftime("%d/%m/%Y, %H:%M - ")
            datetimes.append(formatted)
        except:
            datetimes.append(None)

    df = pd.DataFrame({'date': datetimes, 'user_message': messages})
    df.dropna(inplace=True)

    users = []
    messages = []

    for msg in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', msg.strip(), maxsplit=1)
        if len(entry) >= 3:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append("system")
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns='user_message', inplace=True)

    df['only_date'] = pd.to_datetime(df['date'], format='%d/%m/%Y, %H:%M - ').dt.date
    df['year'] = pd.to_datetime(df['date'], format='%d/%m/%Y, %H:%M - ').dt.year
    df['month_num'] = pd.to_datetime(df['date'], format='%d/%m/%Y, %H:%M - ').dt.month
    df['month'] = pd.to_datetime(df['date'], format='%d/%m/%Y, %H:%M - ').dt.month_name()
    df['day'] = pd.to_datetime(df['date'], format='%d/%m/%Y, %H:%M - ').dt.day
    df['day_name'] = pd.to_datetime(df['date'], format='%d/%m/%Y, %H:%M - ').dt.day_name()
    df['hour'] = pd.to_datetime(df['date'], format='%d/%m/%Y, %H:%M - ').dt.hour
    df['minute'] = pd.to_datetime(df['date'], format='%d/%m/%Y, %H:%M - ').dt.minute

    df['period'] = df['hour'].apply(lambda h: f"{h:02d}-{(h + 1) % 24:02d}")

    return df
