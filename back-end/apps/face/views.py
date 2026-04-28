"""
人脸识别视图层 - CBV类视图
提供人脸采集、人脸识别、用户登录等API接口
"""

import os
import json
import base64
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

from .services import FaceService, DatabaseService, RandomService
from .forms import UserRegisterForm
from core.utils.response import api_response, format_datetime


def get_login_user_id(request):
    return request.session.get('user_id')


def require_login(view_func):
    def wrapper(request, *args, **kwargs):
        user_id = get_login_user_id(request)
        if not user_id:
            return api_response(code=401, msg="未登录或登录已过期")
        return view_func(request, *args, **kwargs, _user_id=user_id)
    return wrapper


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))

            invitation_code = data.get('invitation_code', '')
            if not invitation_code or invitation_code != settings.INVITATION_CODE:
                return api_response(code=1001, msg="邀请码无效")

            form = UserRegisterForm(data={
                'user_name': data.get("user_name"),
                'user_pwd': data.get("user_pwd"),
            })

            if not form.is_valid():
                errors = [error for field, errors in form.errors.items() for error in errors]
                if any('密码' in e for e in errors):
                    return api_response(code=1003, msg="密码格式错误")
                return api_response(code=400, msg=f"参数错误：{', '.join(errors)}")

            user_name = data.get("user_name")
            existing = DatabaseService.select_user(name=user_name)
            if existing:
                return api_response(code=1002, msg="用户名已存在")

            has_face = 'face_image' in data and data['face_image']

            if has_face:
                return self._register_with_face(request, data, form)
            else:
                return self._register_without_face(data, form)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return api_response(code=500, msg="服务器内部错误")

    def _register_with_face(self, request, data, form):
        try:
            image_data = data['face_image'].split(',')[1]
            image_bytes = base64.b64decode(image_data)

            video_encoding = FaceService.get_face_encoding(image_bytes)
            if video_encoding is None:
                return api_response(code=400, msg="未检测到人脸")

            face_save_path = settings.FACE_IMAGES_DIR
            if not face_save_path.exists():
                face_save_path.mkdir(parents=True, exist_ok=True)

            for file_name in os.listdir(face_save_path):
                file_path = face_save_path / file_name
                dir_encoding, _ = FaceService.load_face_from_file(str(file_path))
                if dir_encoding is not None:
                    if FaceService.compare_faces(dir_encoding, video_encoding):
                        return api_response(code=400, msg="当前用户已经采集过人脸信息")

            name_id = RandomService.generate_unique_random(1, 100)
            video_save_path = face_save_path / f"{name_id}.jpg"

            if DatabaseService.insert_user(name_id, data.get("user_name"), int(data.get("user_age", 0)), data.get("user_phone", ""), data.get("user_pwd")):
                with open(video_save_path, "wb") as f:
                    f.write(image_bytes)
                return api_response(data={"user_id": name_id})
            return api_response(code=500, msg="注册失败")
        except Exception as e:
            import traceback
            traceback.print_exc()
            return api_response(code=500, msg="服务器内部错误")

    def _register_without_face(self, data, form):
        try:
            name_id = RandomService.generate_unique_random(1, 100)

            if DatabaseService.insert_user(name_id, data.get("user_name"), int(data.get("user_age", 0)), data.get("user_phone", ""), data.get("user_pwd")):
                return api_response(data={"user_id": name_id})
            return api_response(code=500, msg="注册失败")
        except Exception as e:
            import traceback
            traceback.print_exc()
            return api_response(code=500, msg="服务器内部错误")


@method_decorator(csrf_exempt, name='dispatch')
class PasswordLoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            login_account = data.get("login_account", "").strip()
            user_pwd = data.get("user_pwd", "")

            if not login_account or not user_pwd:
                return api_response(code=400, msg="请求参数错误")

            result = DatabaseService.select_user(name=login_account)
            if not result:
                result = DatabaseService.select_user(phone=login_account)

            if not result:
                return api_response(code=1004, msg="登录账号或密码错误")

            user = result[0]
            if user[4] != user_pwd:
                return api_response(code=1004, msg="登录账号或密码错误")

            request.session['user_id'] = user[0]
            request.session['user_name'] = user[1]

            return api_response(data={
                "user_id": user[0],
                "user_name": user[1],
                "user_age": user[2],
                "user_phone": user[3],
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return api_response(code=500, msg="服务器内部错误")


@method_decorator(csrf_exempt, name='dispatch')
class FaceLoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            face_image = data.get('face_image', '')

            if not face_image:
                return api_response(code=400, msg="请求参数错误")

            image_data = face_image.split(',')[1]
            image_bytes = base64.b64decode(image_data)

            video_encoding = FaceService.get_face_encoding(image_bytes)
            if video_encoding is None:
                return api_response(code=1005, msg="未识别到已注册人脸")

            face_save_path = settings.FACE_IMAGES_DIR
            if not face_save_path.exists():
                return api_response(code=1005, msg="未识别到已注册人脸")

            for file_name in os.listdir(face_save_path):
                file_path = face_save_path / file_name
                dir_encoding, _ = FaceService.load_face_from_file(str(file_path))

                if dir_encoding is None:
                    continue

                if FaceService.compare_faces(dir_encoding, video_encoding):
                    user_id = int(file_name.split(".")[0])
                    result = DatabaseService.select_user(user_id=user_id)

                    if not result:
                        return api_response(code=500, msg="服务器内部错误")

                    user = result[0]

                    request.session['user_id'] = user[0]
                    request.session['user_name'] = user[1]

                    return api_response(data={
                        "user_id": user[0],
                        "user_name": user[1],
                        "user_age": user[2],
                        "user_phone": user[3],
                    })

            return api_response(code=1005, msg="未识别到已注册人脸")
        except Exception as e:
            import traceback
            traceback.print_exc()
            return api_response(code=500, msg="服务器内部错误")


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(View):
    def post(self, request):
        request.session.flush()
        return api_response()
