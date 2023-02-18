import math
import random

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def OTP_Gen():
    otp = ""
    for i in range(6):
        otp += str(math.floor(random.randrange(0, 9)))
    return otp