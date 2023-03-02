import math
import random

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