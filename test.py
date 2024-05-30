from datetime import datetime, timedelta
import pytz


def wating_to_wake_up(start_time, end_time):
    start = datetime.strptime(start_time, '%H:%M')
    end = datetime.strptime(end_time, '%H:%M')
    hours = datetime.strptime("00:00", "%H:%M")
    result = datetime.strftime(hours-(end-start), '%H:%M')
    asd = timedelta(hours=int(result[0] + result[1]), minutes=int(result[3] + result[4]))
    return round(asd.total_seconds())


print(wating_to_wake_up("09:00", "23:00"))