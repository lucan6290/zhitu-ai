from django.http import JsonResponse


def api_response(code=200, msg="success", data=None):
    return JsonResponse({
        "code": code,
        "msg": msg,
        "data": data
    })


def format_datetime(dt):
    if dt is None:
        return None
    dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    return dt_str.replace(' ', 'T')
