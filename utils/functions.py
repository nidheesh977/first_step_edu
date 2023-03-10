import math
import random
from datetime import datetime, date, timedelta,time

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def OTP_Gen():
    otp = ""
    for i in range(6):
        otp += str(math.floor(random.randrange(0, 9)))
    return otp

def reterive_request_data(request_data:dict)->str:
    DATA = dict(request_data)
    if "csrfmiddlewaretoken" in DATA:
        DATA.pop("csrfmiddlewaretoken")
    url=""
    for i,v in enumerate(DATA.items()):
        if i==0:
            url+=f"?{v[0]}={v[1][0]}"
        else:
            url+=f"&{v[0]}={v[1][0]}"
    return url

def str_to_timedelta(str_time:str)->timedelta:
    try:
        splitted = str_time.split(":")
        len_of_splitted = len(splitted)
        match len_of_splitted:
            case 2: # -> only minutes and seconds
                time_obj = time(hour=0,minute=int(splitted[0]),second=int(splitted[1]))
                time_delta = timedelta(hours = time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second)
                return time_delta
        
            case 3: # -> hours, minutes and seconds
                time_obj = time(hour=int(splitted[0]),minute=int(splitted[1]),second=int(splitted[2]))
                time_delta = timedelta(hours = time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second)
                return time_delta
            case _:
                return timedelta(0)
    except Exception:
        return timedelta(0)