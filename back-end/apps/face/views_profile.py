import json
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .services import DatabaseService
from .views import get_login_user_id
from core.utils.response import api_response, format_datetime


@method_decorator(csrf_exempt, name='dispatch')
class UserProfileView(View):
    def post(self, request):
        user_id = get_login_user_id(request)
        if not user_id:
            return api_response(code=401, msg="未登录或登录已过期")

        try:
            data = json.loads(request.body.decode('utf-8'))
            action = data.get("action")

            result = DatabaseService.select_user(user_id=user_id)
            if not result:
                return api_response(code=401, msg="未登录或登录已过期")

            user = result[0]

            if action == "update":
                age = data.get("user_age")
                phone = data.get("user_phone")
                new_pwd = data.get("new_user_pwd")

                if age is not None:
                    age = int(age)
                if phone == "":
                    phone = None
                if new_pwd == "":
                    new_pwd = None

                update_name = user[1]
                DatabaseService.update_user(update_name, age=age, phone=phone, pwd=new_pwd)

                return api_response(msg="updated")

            return api_response(data={
                "user_id": user[0],
                "user_name": user[1],
                "user_age": user[2],
                "user_phone": user[3],
                "created_at": format_datetime(user[4]) if len(user) > 4 else None,
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return api_response(code=500, msg="服务器内部错误")
